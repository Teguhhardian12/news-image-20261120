#!/usr/bin/env python3
"""Copy the committed front page to the output directory, unchanged.

Standard library only. No network, no clock, no randomness. The image bytes
are committed at entry.png; this program validates them (size, dimensions,
whole PNG structure) and copies them verbatim to
${MAKEFUN_OUTPUT_DIR:-/output}/entry.png.

Run: python3 -P -s main.py
"""
import hashlib
import os
import shutil
import struct
import sys
import zlib
from typing import NoReturn

MAX_BYTES = 1 * 1024 * 1024     # 1 MiB
MAX_DIM = 1024
PNG_SIG = b"\x89PNG\r\n\x1a\n"


def fail(msg: str) -> NoReturn:
    print("FAIL: " + msg, file=sys.stderr)
    sys.exit(1)


def validate_png(data):
    """Check size, dimensions and full PNG integrity using only the stdlib."""
    if len(data) > MAX_BYTES:
        fail(f"entry.png is {len(data)} bytes (> 1 MiB)")
    if not data.startswith(PNG_SIG):
        fail("bad PNG signature")

    pos = 8
    width = height = None
    bit_depth = color_type = None
    idat = []
    saw_iend = False
    while pos + 12 <= len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        tag = data[pos + 4:pos + 8]
        if pos + 12 + length > len(data):
            fail(f"truncated chunk {tag!r}")
        chunk = data[pos + 8:pos + 8 + length]
        (crc,) = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])
        if zlib.crc32(tag + chunk) & 0xFFFFFFFF != crc:
            fail(f"CRC mismatch in chunk {tag!r}")
        if tag == b"IHDR":
            if length < 13:
                fail("short IHDR")
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk[:10])
        elif tag == b"IDAT":
            idat.append(chunk)
        elif tag == b"IEND":
            saw_iend = True
            pos += 12 + length
            break
        pos += 12 + length

    if width is None:
        fail("missing IHDR")
    if not saw_iend:
        fail("missing IEND (image is not whole)")
    if pos != len(data):
        fail("trailing bytes after IEND")
    if not (1 <= width <= MAX_DIM and 1 <= height <= MAX_DIM):
        fail(f"dimensions {width}x{height} exceed {MAX_DIM}x{MAX_DIM}")
    if not idat:
        fail("no IDAT pixel data")

    # Decompress the pixel stream and check its exact expected length.
    try:
        raw = zlib.decompress(b"".join(idat))
    except zlib.error as e:
        fail(f"IDAT does not decompress: {e}")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type)
    if channels is None:
        fail(f"unknown color type {color_type}")
    if bit_depth == 8:
        expected = height * (1 + width * channels)
        if len(raw) != expected:
            fail(f"pixel data length {len(raw)} != expected {expected}")
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        fail("entry.png not found next to main.py")
    with open(src, "rb") as f:
        data = f.read()
    width, height = validate_png(data)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)

    # Read back and prove the copy is byte-for-byte identical.
    with open(dst, "rb") as f:
        copied = f.read()
    if hashlib.sha256(copied).digest() != hashlib.sha256(data).digest():
        fail("copied bytes differ from source")
    print(f"OK: {width}x{height} PNG, {len(data)} bytes "
          f"({len(data) / 1048576:.3f} MiB), copied unchanged to {dst}")
    print("sha256: " + hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()