# squeezelite-esp32-s3-qio-padding

# QIO Alignment & Memory Padding 

These files implement a custom padding mechanism designed to resolve alignment issues encountered when building squeezelite-esp32 for the ESP32-S3 with idf 4.x.
QIO mode is sensitive to the segments of the binaries ending with proper alignment.

## Overview

In certain hardware configurations, the alignment of code segments in Flash or IRAM can impact stability or prevent the bootloader from verifying the application signature. This system allows you to "nudge" memory segments by injecting controlled buffers into specific memory sections via CMake flags.

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

You can apply padding during the build process by passing the desired sizes (in bytes) to the idf.py command.

### Build Examples

To add 16 bytes of padding to the RODATA section:
> `idf.py build -DRODATA_PADDING=16`

To nudge both IRAM and Flash Code sections:
> `idf.py build -DIRAM_PADDING=24 -DIROM_PADDING=8`

To reset and build without padding:
> `idf.py fullclean`
> `idf.py build`

make sure to remove old builds before building with new parameters
> rm -r build
---

## Binary Analysis Tool

A Python utility **image-info.py** is provided to analyze the resulting `.bin` files and detect alignment conflicts that could cause QIO or Secure Boot failures.

### What it checks:
The script parses the output of `esptool.py image_info` and flags segments that meet high-risk alignment criteria:
* **[len]**: Flagged if the segment length % 16 == 12.
* **[end]**: Flagged if the (length + file_offset) % 16 == 12.

### Running the Analysis:
Ensure your project is built, then run the script from the project root:
> `python3 image-info.py`

The script specifically looks at `squeezelite.bin` and `recovery_padded.bin`, applying a shift calculation to Segments 1 and 4.

The logic isn't 100% conclusive, some binaries have other offsets when flashed.

### Effects

RODATA_PADDING increases the length of Segment 1 (DROM) and shifts file_offs of Segments 2-7
IROM_PADDING increases the length of Segment 4 (IROM) and shifts file_offs of Segments 5-7
IRAM_PADDING increases the length of Segment 5 (IRAM) and shifts file_offs of Segments 6-7

---

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
