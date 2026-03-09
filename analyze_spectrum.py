#!/usr/bin/env python3
"""Quick analyzer for ZX Spectrum .tap and .z80 files.

This script is intended to bootstrap reverse engineering before porting a game to pygame.
"""

from __future__ import annotations

import argparse
import pathlib
import struct
from dataclasses import dataclass


@dataclass
class TapBlock:
    length: int
    flag: int
    data: bytes

    @property
    def is_header(self) -> bool:
        return self.flag == 0x00 and len(self.data) >= 19


def parse_tap(path: pathlib.Path) -> list[TapBlock]:
    raw = path.read_bytes()
    blocks: list[TapBlock] = []
    i = 0

    while i + 2 <= len(raw):
        (block_len,) = struct.unpack_from("<H", raw, i)
        i += 2
        if i + block_len > len(raw):
            break

        chunk = raw[i : i + block_len]
        i += block_len
        if not chunk:
            continue

        blocks.append(TapBlock(length=block_len, flag=chunk[0], data=chunk))

    return blocks


def describe_tap(blocks: list[TapBlock]) -> str:
    lines = [f"TAP blocks: {len(blocks)}"]
    for idx, block in enumerate(blocks, start=1):
        if block.is_header:
            type_id = block.data[1]
            name = block.data[2:12].decode("ascii", errors="replace").strip()
            data_len = struct.unpack_from("<H", block.data, 12)[0]
            param1 = struct.unpack_from("<H", block.data, 14)[0]
            param2 = struct.unpack_from("<H", block.data, 16)[0]
            lines.append(
                f"  {idx:02d}. HEADER type={type_id} name='{name}' data_len={data_len} "
                f"param1={param1} param2={param2}"
            )
        else:
            lines.append(f"  {idx:02d}. DATA flag=0x{block.flag:02X} bytes={block.length-1}")
    return "\n".join(lines)


def describe_z80(path: pathlib.Path) -> str:
    raw = path.read_bytes()
    if len(raw) < 30:
        return "Invalid Z80: too short"

    a, f, c, b, l, h, pc, sp, i, r, flags = struct.unpack_from("<BBBBBBHHBBB", raw, 0)
    compressed = bool(flags & 0x20)

    lines = [
        "Z80 snapshot summary:",
        f"  size={len(raw)} bytes",
        f"  PC=0x{pc:04X} SP=0x{sp:04X}",
        f"  AF=0x{a:02X}{f:02X} BC=0x{b:02X}{c:02X} HL=0x{h:02X}{l:02X}",
        f"  I=0x{i:02X} R=0x{r:02X}",
        f"  compressed_memory={compressed}",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze ZX Spectrum TAP/Z80 files")
    parser.add_argument("file", type=pathlib.Path, help="Input .tap or .z80 file")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"File not found: {args.file}")
        return 1

    suffix = args.file.suffix.lower()
    if suffix == ".tap":
        print(describe_tap(parse_tap(args.file)))
    elif suffix == ".z80":
        print(describe_z80(args.file))
    else:
        print("Unsupported file type. Use .tap or .z80")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())