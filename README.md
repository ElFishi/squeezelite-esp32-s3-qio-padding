# QIO Alignment & Memory Padding 

These files implement a custom padding mechanism designed to resolve alignment issues encountered when building squeezelite-esp32 for the ESP32-S3 with idf 4.x.
QIO mode is sensitive to the segments of the binaries ending with proper alignment. This system allows you to "nudge" memory segments by injecting controlled buffers into specific memory sections via CMake flags.

## Overview

When building binaries with epressif idf 4.x for squeezelite-esp32 targeted for an ESP32-S3 with flash_mode QIO switching from recovery to squeezelite and vice versa may fail with an error like
```
E (18344) esp_image: invalid segment length 0x5f676e69
E (18344) messaging: Unable to select partition for reboot: ESP_ERR_OTA_VALIDATE_FAILED
```
qio_padding introduces flags to add some bytes to the various segments to prevent this error.

In addition the build option `--secure-pad-v2` is added to `CMaleLists.txt`. While not directly meant for this purpose, this option prevents misalignments at the end of the binaries leading to failures like
```
E (12515) esp_image: Image hash failed - image is corrupt
E (12525) messaging: Unable to select partition for reboot: ESP_ERR_OTA_VALIDATE_FAILED
```

### Supported Padding Sections
* **RODATA**: Constant data in Flash.
* **IRAM**: Executable code in Internal RAM.
* **IROM**: Executable code in Flash (Instruction Bus).
* **RTC**: Data stored in Fast or Slow RTC memory.

---

## How It Works

The system consists of three integrated parts:

1.  **main/qio_padding.c**: Defines the actual buffers using GCC attributes.
2.  **qio_alignment.cmake**: Logic that translates build-time variables into compiler definitions and linker instructions.
3.  **Linker Enforcement**: Uses the -Wl,--undefined flag to ensure the linker does not "garbage collect" the padding buffers.

---

## Installation

Add `main/qio_padding` to `main/` and `qio_alignment.cmake` to the project root.
`CMakeLists.txt` overwrites the original `CMakeLists.txt`.

---

## Usage

You can apply padding during the build process by passing the desired sizes (in bytes) to the idf.py command. Provided flags for `idf.py build` are 
> `-DRODATA_PADDING=n`  
`-DIRAM_PADDING=n`  
`-DIROM_PADDING=n`  
`-RTC_PADDING=n`  

with n being the number of bytes to be inserted.

### Effects

RODATA_PADDING increases the length of Segment 1 (DROM) and shifts file_offs of Segments 2-7  
IROM_PADDING increases the length of Segment 4 (IROM) and shifts file_offs of Segments 5-7  
IRAM_PADDING increases the length of Segment 5 (IRAM) and shifts file_offs of Segments 6-7  
RTC_PADDING is not really useful 😞

### Build Examples

To add 4 bytes of padding to the RODATA section:
> `idf.py build -DRODATA_PADDING=4`

To nudge both IRAM and Flash Code sections:
> `idf.py build -DIRAM_PADDING=4 -DIROM_PADDING=8`

To reset and build without padding:
> `idf.py fullclean`  
`idf.py build`

make sure to remove old builds before building with new parameters
> rm -r build
---

## Binary Analysis Tool

A Python utility **image-info.py** is provided to analyze the resulting `.bin` files and detect alignment conflicts that are likely to cause QIO boot failures.

### What it checks:
The script parses the output of `esptool.py image_info` and flags segments that are likely to fail with **⚠**.

The reason for failure is the bootloader for the S3 expecting all segments to be 32-byte aligned with respect to the 8-byte header following one segment, preceding the next. If the end of a segment ends less than 8 bytes before the next 32-byte block, the header gets split, the bootloader fails to read the header correctly and fails with `invalid segment length`. The aim of the padding is thus to nudge each segment wrt length and offset that the end is 0xc or less. To calculate the end of each segment the script considers that the paddr of each segment is found 8 bytes higher that file_offs would suggest. 


### Running the Analysis:
Ensure your project is built, then run the script from the project root:
> `python3 image-info.py`

The script by default looks at `build/squeezelite.bin` and `build/recovery_padded.bin`.

---

## Recipe

1.  Build binaries with `idf.py build`
2.  Run image-info.py and check the output for **⚠** warnings.
3.  Add padding bytes to the first Segment with a warning and re-run image-info.py.
4.  Repeat 2. & 3. until first warning is gone.  
By adding bytes later Segments may receive (or lose) a warning. 
5.  Continue with next marked Segment until all warnings are gone.  
squeezelite.bin and recovery-padded.bin may need different paddings to lose all warnings.
6.  Flash and test by entering in a terminal  
`restart_ota` to switch from recovery to squeezelite  
`recovery` to switch from squeezelite to recovery.


## Configuration Details

### CMake Variables
| Variable | C Symbol | Target Section |
| :--- | :--- | :--- |
| RODATA_PADDING | qio_rodata_padding | .rodata |
| IRAM_PADDING | qio_code_padding | .iram1.text |
| IROM_PADDING | qio_irom_padding | .flash.text |
| RTC_PADDING | qio_rtc_padding | .rtc.data |

---

## Technical Notes

* **NOP Sleds**: IRAM and IROM padding are filled with 0x90 (No-Operation) instructions. This ensures that if the CPU program counter ever accidentally enters the padding zone, it will "slide" through safely rather than triggering an illegal instruction exception.
* **Zero-Fill**: RODATA and RTC padding are initialized to 0x00.
* **Secure Boot**: This logic is compatible with --secure-pad-v2 as it modifies the ELF structure before the binary is signed and converted to a bootable image.
