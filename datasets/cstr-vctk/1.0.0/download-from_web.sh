#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$SCRIPT_DIR/../data/raw/VCTK-Corpus-0.92"

mkdir -p "$TARGET_DIR"

echo "Downloading VCTK-Corpus-0.92.zip (approx. 10 GB)..."
wget -c -O "$TARGET_DIR/VCTK-Corpus-0.92.zip" \
    "https://datashare.ed.ac.uk/bitstream/handle/10283/3443/VCTK-Corpus-0.92.zip?sequence=2&isAllowed=y"

echo "Downloading README.txt..."
wget -c -O "$TARGET_DIR/README.txt" \
    "https://datashare.ed.ac.uk/bitstream/handle/10283/3443/README.txt?sequence=1&isAllowed=y"

echo "Downloading license_text.txt..."
wget -c -O "$TARGET_DIR/license_text.txt" \
    "https://datashare.ed.ac.uk/bitstream/handle/10283/3443/license_text.txt?sequence=6&isAllowed=y"

echo "All downloads complete. Files saved to: $TARGET_DIR"
