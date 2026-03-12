#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZIP_FILE="$SCRIPT_DIR/../data/raw/VCTK-Corpus-0.92/VCTK-Corpus-0.92.zip"
TARGET_DIR="$SCRIPT_DIR/../data/extracted/VCTK-Corpus-0.92"

if [[ ! -f "$ZIP_FILE" ]]; then
    echo "Error: ZIP file not found at $ZIP_FILE" >&2
    exit 1
fi

mkdir -p "$TARGET_DIR"

echo "Extracting $ZIP_FILE to $TARGET_DIR ..."
unzip -q "$ZIP_FILE" -d "$TARGET_DIR"

echo "Extraction complete. Files saved to: $TARGET_DIR"
