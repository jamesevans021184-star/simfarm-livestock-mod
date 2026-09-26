#!/usr/bin/env python3
"""Report verified livestock-related instruction signatures in supported SimFarm."""
from pathlib import Path
import argparse,hashlib
SHA="f497c6ffe5a6b729d3c48c431a1285b1b6c1e890313b9d5081b4f4cba399dd0a"
SIGS={
 "livestock_create": (0x15534, bytes.fromhex("55 8b ec b8 06 00")),
 "livestock_delete": (0x155b4, bytes.fromhex("55 8b ec 33 c0 9a")),
 "livestock_update": (0x1576a, bytes.fromhex("55 8b ec b8 06 00")),
 "relocation_livestock_range": (0x1c63f, bytes.fromhex("81 7e e6 dc 00 7c 47 81 7e e6 df 00 7f 40")),
 "purchase_livestock_range": (0x3e55e, bytes.fromhex("81 7e 06 dc 00 7c 31 81 7e 06 df 00 7f 2a")),
}
def main():
 p=argparse.ArgumentParser();p.add_argument("exe",type=Path);a=p.parse_args();b=a.exe.read_bytes()
 if hashlib.sha256(b).hexdigest()!=SHA: raise SystemExit("Unsupported executable")
 for name,(off,sig) in SIGS.items():
  ok=b[off:off+len(sig)]==sig
  print(f"{name:30} {off:#08x} {'OK' if ok else 'MISMATCH'}")
if __name__=="__main__":main()
