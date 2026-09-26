#!/usr/bin/env python3
"""Structural scanner for the supported SimFarm DOS executable."""
from __future__ import annotations
import argparse, hashlib, struct
from pathlib import Path

SUPPORTED_SHA256="f497c6ffe5a6b729d3c48c431a1285b1b6c1e890313b9d5081b4f4cba399dd0a"
DESC_TABLE=0x2A903
DESC_SIZE=18
OVL_BASE_SEG=0x2A56

def u16(b,o): return struct.unpack_from("<H",b,o)[0]

def root_header(b):
    cblp,cp=u16(b,2),u16(b,4)
    return {"exact_size":(cp-1)*512+(cblp or 512),
            "header_bytes":u16(b,8)*16,"relocations":u16(b,6),
            "ss":u16(b,0x0e),"sp":u16(b,0x10),
            "ip":u16(b,0x14),"cs":u16(b,0x16)}

def overlay_descriptors(b):
    """Parse SimFarm's resident overlay-manager descriptor table.

    For normal overlays the 9 little-endian words are:
      file_paragraph, flags, image_paragraphs, relocation_count,
      resident_marker, overlay_number, image_paragraphs_copy,
      load_segment, manager_segment
    The first 29 overlays are mapped at 2A56h. Overlay 30 uses a different
    load segment and is retained as a descriptor rather than discarded.
    """
    out=[]
    pos=DESC_TABLE
    last_start=0
    for _ in range(64):
        if pos+DESC_SIZE>len(b): break
        w=struct.unpack_from("<9H",b,pos)
        start=w[0]*16
        if not start or start<=last_start or start>=len(b): break
        if w[4] != 0xffff: break
        out.append({"descriptor_file_offset":pos,"file_offset":start,
                    "flags":w[1],"image_paragraphs":w[2],
                    "relocation_count":w[3],"overlay_number":w[5],
                    "image_paragraphs_copy":w[6],"load_segment":w[7],
                    "manager_segment":w[8]})
        last_start=start
        pos+=DESC_SIZE
    return out

def describe_overlay(b,d):
    start=d["file_offset"]
    relbytes=d["relocation_count"]*4
    image=start+relbytes
    calc_end=image+d["image_paragraphs"]*16
    return {**d,"relocation_bytes":relbytes,"image_file_offset":image,
            "calculated_end":calc_end}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("exe",type=Path)
    a=ap.parse_args()
    b=a.exe.read_bytes()
    sha=hashlib.sha256(b).hexdigest()
    if b[:2]!=b"MZ": raise SystemExit("Not an MZ executable")
    print("SHA256",sha)
    print("supported",sha==SUPPORTED_SHA256)
    print("file_size",len(b))
    print("root",root_header(b))
    if sha!=SUPPORTED_SHA256:
        raise SystemExit("Unsupported executable hash")
    ds=[describe_overlay(b,d) for d in overlay_descriptors(b)]
    print("overlay_descriptors",len(ds))
    for d in ds:
        print("OVL",d["overlay_number"],
              "start",hex(d["file_offset"]),
              "relocs",d["relocation_count"],
              "image",hex(d["image_file_offset"]),
              "image_paras",hex(d["image_paragraphs"]),
              "end",hex(d["calculated_end"]),
              "load_seg",hex(d["load_segment"]))

if __name__=="__main__":
    main()
