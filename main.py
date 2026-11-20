#!/usr/bin/env python3
"""Entry program for make.fun's news-image-20261120 bounty.

The front page itself is a committed asset, frontpage.png, drawn by
render.py (Pillow, real TTF type, 38 verified stories from Friday
20 November 2026 in 7 regions). This program simply copies that asset
to the output entry, byte for byte, so every run writes the same
bytes. Python standard library only; no network.
"""

import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.join(HERE, "frontpage.png")
MAX_BYTES = 1024 * 1024          # the bounty caps the image at 1 MiB
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def check_asset(path):
    """Fail loudly if the committed asset is not a valid PNG in limits."""
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise SystemExit("asset too large: %d bytes > %d" % (size, MAX_BYTES))
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != PNG_SIGNATURE:
        raise SystemExit("asset is not a PNG file")
    width, height = struct.unpack(">II", head[16:24])
    if width > 1024 or height > 1024:
        raise SystemExit("asset too big: %dx%d" % (width, height))
    return width, height, size


def main():
    width, height, size = check_asset(ASSET)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(ASSET, dest)
    print("wrote %s (%dx%d PNG, %d bytes)" % (dest, width, height, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
