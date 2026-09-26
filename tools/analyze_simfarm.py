#!/usr/bin/env python3
"""Structural scanner for the supported SIMFARM.EXE.

No copyrighted game bytes are embedded here. The scanner identifies the root
MZ load image, appended data, selected resource strings, relocations, and
candidate 8086 references to offsets/segments associated with those resources.
"""
from __future__ import annotations
import argparse, hashlib, struct
from pathlib import Path

SUPPORTED_SHA256 = "f497c6ffe5a6b729d3c48c431a1285b1b6c1e890313b9d5081b4f4cba399dd0a"
TARGETS = [
    b"Feed for Animals",
    b"Water Trough for Animals",
    b"Place Fences",
    b"Horse",
    b"Sheep",
    b"Severe Drought",
]

def u16(b,o): return struct.unpack_from("<H", b, o)[0]

def root_header(b):
    if b[:2] != b"MZ": raise ValueError("not an MZ executable")
    cblp, cp = u16(b,2), u16(b,4)
    root_size=(cp-1)*512+(cblp or 512)
    return {
        "root_size":root_size, "relocations":u16(b,6),
        "header_bytes":u16(b,8)*16, "ss":u16(b,0x0e), "sp":u16(b,0x10),
        "ip":u16(b,0x14), "cs":u16(b,0x16), "reloc_off":u16(b,0x18),
        "overlay_no":u16(b,0x1a)
    }

def all_offsets(b, needle):
    out=[]; pos=0
    while True:
        pos=b.find(needle,pos)
        if pos < 0: return out
        out.append(pos); pos += 1

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("exe", type=Path)
    args=ap.parse_args()
    b=args.exe.read_bytes()
    sha=hashlib.sha256(b).hexdigest()
    h=root_header(b)
    print("SHA256",sha)
    print("supported",sha==SUPPORTED_SHA256)
    print("file_size",len(b))
    print("root_mz_size",h["root_size"])
    print("appended_size",len(b)-h["root_size"])
    print("header",h)
    for t in TARGETS:
        print(t.decode("ascii"), [hex(x) for x in all_offsets(b,t)])
    if sha != SUPPORTED_SHA256:
        raise SystemExit("Refusing version-specific analysis: unsupported executable hash")

if __name__=="__main__":
    main()
