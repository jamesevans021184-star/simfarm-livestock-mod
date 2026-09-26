#!/usr/bin/env python3
"""Version-locked SimFarm binary patch framework.

Patch definitions are intentionally empty until each target routine has been
identified and verified. This prevents producing a corrupt or falsely claimed
"modified" game.
"""
from __future__ import annotations
import argparse, hashlib, shutil
from pathlib import Path

SUPPORTED_SHA256="f497c6ffe5a6b729d3c48c431a1285b1b6c1e890313b9d5081b4f4cba399dd0a"
PATCHES=[]  # (file_offset, expected_bytes, replacement_bytes, description)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source",type=Path)
    ap.add_argument("output",type=Path)
    a=ap.parse_args()
    raw=bytearray(a.source.read_bytes())
    sha=hashlib.sha256(raw).hexdigest()
    if sha != SUPPORTED_SHA256:
        raise SystemExit(f"Unsupported SIMFARM.EXE: {sha}")
    if not PATCHES:
        raise SystemExit("No verified gameplay patches are defined yet; refusing to create a fake modified EXE.")
    for off,expected,repl,desc in PATCHES:
        if raw[off:off+len(expected)] != expected:
            raise SystemExit(f"Preimage mismatch at {off:#x}: {desc}")
        if len(expected)!=len(repl):
            raise SystemExit("In-place patch length mismatch")
        raw[off:off+len(repl)]=repl
    a.output.write_bytes(raw)
    print("Wrote",a.output)

if __name__=="__main__":
    main()
