#!/usr/bin/env python3
import subprocess
import re
import sys
import os
import argparse


def analyze_files(files=None):
    # List of files to process
    if files is None:
        target_files = ["build/squeezelite.bin", "build/recovery_padded.bin"]
    else:
        target_files = files

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
                flags = ""

                if match:
                    length = int(match.group(1), 16)
                    file_offs = int(match.group(3), 16)

                    paddr = file_offs + 8

                    # Check if segment end is closer than 8 bytes to 32-byte block end;
                    if (length + paddr) % 0x20 > 0x18:
                        flags += ("⚠ ")

                print(
                    " ".join(clean_line.split(" ")[:8])
                    + flags + " "
                    + " ".join(clean_line.split(" ")[8:])
                )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze ESP32-S3 binary files using esptool.py")
    parser.add_argument("files", nargs="*", help="Binary file(s) to analyze (optional)")

    args = parser.parse_args()

    if args.files:
        analyze_files(args.files)
    else:
        analyze_files()
