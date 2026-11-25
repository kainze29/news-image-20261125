#!/usr/bin/env python3
"""Publish the 25 November 2026 front page for make.fun.

The finished page lives in this repository as news.jpg. It shows six
photo stories from Wednesday 25 November 2026, a numbered brief of 45
more stories from the same day, and a world map of where they happened.
This script only copies that file into the grader's output directory
under the name entry.png, after checking it fits the competition's
limits. No network, no clock, no randomness: running it twice writes
identical bytes.
"""

import hashlib
import os
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "news.jpg"
OUTPUT_NAME = "entry.png"
BYTE_LIMIT = 1_048_576
EDGE_LIMIT = 1024
SOI = b"\xff\xd8"
EOI = b"\xff\xd9"
FRAME_MARKERS = frozenset((0xC0, 0xC1, 0xC2))


def jpeg_size(blob):
    """Return (width, height) by walking the JPEG segment headers."""
    if blob[:2] != SOI:
        sys.exit("news.jpg is not a JPEG (missing SOI marker)")
    pos = 2
    while pos + 9 <= len(blob):
        if blob[pos] != 0xFF:
            sys.exit("news.jpg has a broken marker at offset %d" % pos)
        # Fill bytes (extra 0xFF) are legal padding between segments.
        while blob[pos + 1] == 0xFF:
            pos += 1
        marker = blob[pos + 1]
        if marker in FRAME_MARKERS:
            height = (blob[pos + 5] << 8) | blob[pos + 6]
            width = (blob[pos + 7] << 8) | blob[pos + 8]
            return width, height
        if marker == 0xD8 or marker == 0xD9 or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        seg_len = (blob[pos + 2] << 8) | blob[pos + 3]
        if seg_len < 2:
            sys.exit("news.jpg has a bad segment length at offset %d" % pos)
        pos += 2 + seg_len
    sys.exit("news.jpg carries no frame marker, so its size is unknown")


def run():
    blob = SOURCE.read_bytes()
    if len(blob) > BYTE_LIMIT:
        sys.exit("news.jpg is %d bytes, over the 1 MiB limit" % len(blob))
    if blob[-2:] != EOI:
        sys.exit("news.jpg is truncated (missing EOI marker)")
    width, height = jpeg_size(blob)
    if width > EDGE_LIMIT or height > EDGE_LIMIT:
        sys.exit("news.jpg is %dx%d, over the 1024-pixel limit" % (width, height))
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / OUTPUT_NAME
    dest.write_bytes(blob)
    digest = hashlib.sha256(blob).hexdigest()
    print("wrote %s (%d bytes, %dx%d, sha256=%s)" % (dest, len(blob), width, height, digest))


if __name__ == "__main__":
    run()
