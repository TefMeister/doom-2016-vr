#!/usr/bin/env python3
"""Coverage check: widen the record filter and see whether the record count moves.
Also scans .rdata for the same 72-byte record shape."""
import sys
import numpy as np
from refwalk import data, secs, cstr, printable, IDENT, q

S = {n: (lo, lo + rsz, raw, rsz & ~7) for n, lo, hi, raw, rsz in secs}
RD_LO, RD_HI = S[".rdata"][0], S[".rdata"][1]
DT_LO, DT_HI = S[".data"][0], S[".data"][1]

def scan(secname, strlo, strhi, label):
    lo, hi, raw, rsz = S[secname]
    arr = np.frombuffer(data[raw:raw + rsz], dtype="<u8")
    ptr = (arr >= strlo) & (arr < strhi)
    v = arr
    small = ((v & 0xFFFFFFFF) < 0x400000) & ((v >> 32) < 0x400000) & ((v >> 32) > 0)
    n = arr.size
    i = np.arange(n - 8)
    cand = i[ptr[:n - 8] & ptr[2:n - 6] & small[3:n - 5]]
    ok = 0
    for j in cand.tolist():
        va = lo + j * 8
        nm = cstr(int(arr[j + 2]), 160)
        if nm is None or not IDENT.match(nm):
            continue
        ty = cstr(int(arr[j]), 300)
        if not printable(ty) or not (0 < len(ty) < 250):
            continue
        ok += 1
    print("%-46s cand=%-7d valid=%d" % (label, cand.size, ok))

# baseline: strings must be in .rdata, records in .data
scan(".data", RD_LO, RD_HI, "records in .data, strings in .rdata (baseline)")
# widened: strings anywhere in .rdata OR .data
scan(".data", RD_LO, DT_HI, "records in .data, strings in .rdata|.data")
# records living in .rdata instead
scan(".rdata", RD_LO, RD_HI, "records in .rdata, strings in .rdata")
scan(".rdata", RD_LO, DT_HI, "records in .rdata, strings in .rdata|.data")
