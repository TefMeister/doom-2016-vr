#!/usr/bin/env python3
"""Scan .data for 72-byte reflection field records and group them into runs.
READ ONLY. Game never launched."""
import sys, struct, re, json
import numpy as np
from refwalk import pe, IB, data, secs, sec_of, rd, q, cstr, printable, IDENT, EXE

RD_LO, RD_HI = None, None
DT_LO, DT_HI = None, None
for n, lo, hi, raw, rsz in secs:
    if n == ".rdata":
        RD_LO, RD_HI, RD_RAW, RD_RSZ = lo, lo + rsz, raw, rsz
    if n == ".data":
        DT_LO, DT_HI, DT_RAW, DT_RSZ = lo, lo + rsz, raw, rsz

arr = np.frombuffer(data[DT_RAW:DT_RAW + DT_RSZ], dtype="<u8")
n = arr.size
print("qwords in .data raw: %d" % n, file=sys.stderr)

# a qword that is a plausible pointer into .rdata (where the string pool lives)
ptr_rd = (arr >= RD_LO) & (arr < RD_HI)
# slot3 = (u32 byteOffset, u32 size), both small
lo32 = (arr & 0xFFFFFFFF)
hi32 = (arr >> 32)
small = (lo32 < 0x400000) & (hi32 < 0x400000) & (hi32 > 0)

idx = np.arange(n - 8)
cand = idx[ptr_rd[:n - 8] & ptr_rd[2:n - 6] & small[3:n - 5]]
print("numeric candidates: %d" % cand.size, file=sys.stderr)

recs = {}
for i in cand.tolist():
    va = DT_LO + i * 8
    p_type = int(arr[i]); p_arr = int(arr[i + 1]); p_name = int(arr[i + 2])
    nm = cstr(p_name, 160)
    if nm is None or not IDENT.match(nm):
        continue
    ty = cstr(p_type, 300)
    if not printable(ty) or not (0 < len(ty) < 250):
        continue
    suffix = b""
    if RD_LO <= p_arr < RD_HI:
        s = cstr(p_arr, 64)
        if s is not None and printable(s):
            suffix = s
    elif p_arr != 0:
        continue
    boff = int(arr[i + 3] & 0xFFFFFFFF)
    bsz = int(arr[i + 3] >> 32)
    p_com = int(arr[i + 5])
    com = b""
    if RD_LO <= p_com < RD_HI:
        c = cstr(p_com, 400)
        if c is not None and printable(c):
            com = c
    recs[va] = dict(va=va, type=ty.decode(), suffix=suffix.decode(),
                    name=nm.decode(), off=boff, size=bsz,
                    s4=int(arr[i + 4]), s6=int(arr[i + 6]),
                    s7=int(arr[i + 7]), s8=int(arr[i + 8]),
                    comment=com.decode())

print("validated records: %d" % len(recs), file=sys.stderr)

vas = sorted(recs)
runs = []
cur = [vas[0]]
for a, b in zip(vas, vas[1:]):
    if b - a == 72:
        cur.append(b)
    else:
        runs.append(cur); cur = [b]
runs.append(cur)
runs = [r for r in runs if len(r) >= 1]
print("runs (stride-72 contiguous groups): %d" % len(runs), file=sys.stderr)
print("runs with >=2 records: %d" % sum(1 for r in runs if len(r) > 1), file=sys.stderr)

json.dump([{"start": r[0], "n": len(r), "fields": [recs[v] for v in r]} for r in runs],
          open(sys.argv[1] if len(sys.argv) > 1 else "runs.json", "w"), indent=1)
