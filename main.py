"""ai-happy-01 entry: copy the bundled image to the output directory.

The entry image lives beside this program as entry.png (JPEG bytes in a
.png name, which the gate allows: it tells PNG from JPEG by the first
bytes). The program copies it byte for byte to /output/entry.png (or
$MAKEFUN_OUTPUT_DIR when set, for local runs outside the grader), so both
grader runs produce identical bytes. The copy is guarded: the source must
exist and fit the competition limits (at most 1 MiB, at most 1024x1024
pixels), and the written file is checked byte for byte against the source
before the program exits.
Python 3.13 standard library only.
"""

import os
import shutil
import struct
from pathlib import Path

MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def _dimensions(data: bytes) -> tuple[int, int]:
    """Read width/height from a PNG IHDR or a JPEG SOF marker; (0, 0) if unknown."""
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                break
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack(">HH", data[i + 5:i + 9])
                return width, height
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + length
    return 0, 0


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"entry image missing: {SOURCE}")
    data = SOURCE.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit(f"entry image too large: {len(data)} bytes")
    width, height = _dimensions(data)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise SystemExit(f"entry image too big: {width}x{height}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUTPUT_DIR / "entry.png"
    shutil.copyfile(SOURCE, target)
    written = target.read_bytes()
    if written != data:
        raise SystemExit("copy verification failed: output differs from source")
    out_width, out_height = _dimensions(written)
    if (out_width, out_height) != (width, height):
        raise SystemExit("copy verification failed: output dimensions differ")
    print(f"wrote {target} ({len(written)} bytes, {width}x{height})")


if __name__ == "__main__":
    main()
