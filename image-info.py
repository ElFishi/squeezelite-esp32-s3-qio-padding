#!/usr/bin/env python3
import subprocess
import re
import sys
import os

def analyze_files():
    # List of files to process
    target_files = ["build/squeezelite.bin", "build/recovery_padded.bin"]
    TARGET_COL = 98

    # Regex to extract hex values
    data_pattern = re.compile(r"len (0x[0-9a-fA-F]+) load (0x[0-9a-fA-F]+) file_offs (0x[0-9a-fA-F]+)")

    for bin_file in target_files:
        print(f"\n--- Analyzing: {bin_file} ---")
        
        if not os.path.exists(bin_file):
            print(f"Error: {bin_file} not found. Skipping...", file=sys.stderr)
            continue

        command = ["esptool.py", "--chip", "esp32s3", "image_info", bin_file]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error executing esptool for {bin_file}: {e}", file=sys.stderr)
            continue
        except FileNotFoundError:
            print("Error: esptool.py not found in PATH.", file=sys.stderr)
            return

        for line in output.splitlines():
            clean_line = line.strip()
            
            if clean_line.startswith("Segment"):
                match = data_pattern.search(clean_line)
                flags = []
                
                if match:
                    length = int(match.group(1), 16)
                    orig_file_offs = int(match.group(3), 16)
                    
                    # Special treatment for Segment 1 and Segment 4
                    # Shift file_offs from ending in 0x18 to 0x20 for calculation
                    if clean_line.startswith("Segment 1:") or clean_line.startswith("Segment 4:"):
                        # We replace the last bits to ensure it ends in 0x20
                        # Calculation: (offs & ~0xFF) + 0x20 or simply orig + 8 if it was 0x18
                        file_offs = (orig_file_offs & ~0x1F) + 0x20
                    else:
                        file_offs = orig_file_offs

                    # 1) Check if len % 16 == 12 (0xc)
                    if length % 16 == 12:
                        flags.append("len")

                    # 2) Check if (len + shifted_file_offs) % 16 == 12 (0xc)
                    if (length + file_offs) % 16 == 12:
                        flags.append("end")

                if flags:
                    flag_str = f"[{' '.join(flags)}]"
                    padding = max(1, TARGET_COL - len(clean_line))
                    print(f"{clean_line}{' ' * padding}{flag_str}")
                else:
                    print(clean_line)

if __name__ == "__main__":
    analyze_files()
