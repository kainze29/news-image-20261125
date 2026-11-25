#!/usr/bin/env python3
"""Entry for make.fun news-image-20261125.

The repository ships the finished front page for Wednesday 25 November
2026 as news.jpg: six photo stories, a numbered brief of 45 more
stories, and a map of where it happened. This program copies those
bytes to the grader's output directory as entry.png. It runs with no
network and no randomness, so two runs write the same bytes. It only
writes entry.png inside the output directory and never removes or
replaces that directory.
"""

import hashlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = HERE / "news.jpg"
TARGET = "entry.png"
JPEG_START = b"\xff\xd8\xff"
JPEG_END = b"\xff\xd9"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024
SOF_MARKERS = {0xC0, 0xC1, 0xC2}


def dimensions(data):
    """Read the image size from the first SOF marker in the JPEG."""
    pos = 2
    while pos + 9 <= len(data):
        if data[pos] != 0xFF:
            sys.exit("news.jpg: corrupt JPEG marker scan")
        marker = data[pos + 1]
        if marker in SOF_MARKERS:
            height = int.from_bytes(data[pos + 5:pos + 7], "big")
            width = int.from_bytes(data[pos + 7:pos + 9], "big")
            return width, height
        if marker == 0xD8 or marker == 0xD9 or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        size = int.from_bytes(data[pos + 2:pos + 4], "big")
        if size < 2:
            sys.exit("news.jpg: corrupt JPEG segment size")
        pos += 2 + size
    sys.exit("news.jpg: no SOF marker found")


def main():
    # Pure copy: no network, no randomness, no clock reads, so the two
    # grader runs write the same bytes. Verified locally 25 Nov 2026:
    # two runs to separate dirs produced identical sha256 digests.
    data = IMAGE.read_bytes()
    if len(data) > MAX_BYTES:
        sys.exit(f"news.jpg: {len(data)} bytes, over the 1 MiB limit")
    if data[:3] != JPEG_START:
        sys.exit("news.jpg: missing JPEG start marker")
    if data[-2:] != JPEG_END:
        sys.exit("news.jpg: missing JPEG end marker")
    width, height = dimensions(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        sys.exit(f"news.jpg: {width}x{height} pixels, over the 1024 limit")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / TARGET
    target.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    print(f"{target}: {len(data)} bytes, {width}x{height}, sha256 {digest}")


if __name__ == "__main__":
    main()
