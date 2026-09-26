#!/usr/bin/env python3
"""Extract SimFarm overlay images into analysis-friendly binary files."""
from pathlib import Path
import argparse, hashlib, struct
SHA="f497c6ffe5a6b729d3c48c431a1285b1b6c1e890313b9d5081b4f4cba399dd0a"
TABLE=0x2A903
def main():
    p=argparse.ArgumentParser(); p.add_argument("exe",type=Path); p.add_argument("out",type=Path); a=p.parse_args()
    b=a.exe.read_bytes()
    if hashlib.sha256(b).hexdigest()!=SHA: raise SystemExit("Unsupported SIMFARM.EXE")
    a.out.mkdir(parents=True,exist_ok=True)
    pos=TABLE
    for _ in range(32):
        w=struct.unpack_from("<9H",b,pos)
        start=w[0]*16
        if not start or start>=len(b) or w[4]!=0xffff: break
        ov=w[5]; nrel=w[3]; memp=w[2]; filep=w[6]
        rel_end=start+nrel*4
        # Normal overlays use word 2 for their image size; the final permanent
        # data image uses word 6 as the file-backed size (word 2 includes BSS).
        paras=filep if filep and (rel_end+filep*16)<=len(b) and ov>=31 else memp
        end=min(len(b),rel_end+paras*16)
        (a.out/f"ovl_{ov:02d}.bin").write_bytes(b[rel_end:end])
        print(ov,hex(start),hex(rel_end),hex(end),end-rel_end)
        pos+=18
if __name__=="__main__": main()
