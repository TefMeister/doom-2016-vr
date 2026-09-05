#!/usr/bin/env python3
"""Authoritative walk of the id Tech 6 reflection database in DOOMx64vk.exe.

Class descriptor array in .data, stride 56:
    +0  void*  runtime slot        +8  char* className
    +16 char*  "" (base/comment)   +24 u64   sizeof(class)
    +32 u64    0                   +40 ptr   -> field table
    +48 u64    0
Field table: 72-byte records, terminated by an all-zero record.
    +0 char* typeName   +8 char* arraySuffix   +16 char* fieldName
    +24 u32 byteOffset, u32 size                +40 char* comment

READ ONLY on the exe. The game is never launched.
"""
import sys, json
import numpy as np
from refwalk import IB, data, secs, cstr, printable, q, rd, IDENT

for n, lo, hi, raw, rsz in secs:
    if n == ".data":
        DT_LO, DT_RAW, DT_RSZ = lo, raw, rsz & ~7
        DT_HI = lo + rsz
    if n == ".rdata":
        RD_LO, RD_HI = lo, lo + rsz

arr = np.frombuffer(data[DT_RAW:DT_RAW + DT_RSZ], dtype="<u8")

def s_at(va, maxlen=400):
    if not va or not (RD_LO <= va < RD_HI):
        return None
    b = cstr(va, maxlen)
    if b is None or not printable(b) or not (0 < len(b) < maxlen):
        return None
    return b.decode()

def is_desc(va):
    """Does a 56-byte class descriptor start at va?"""
    cn = q(va + 8); sz = q(va + 24); tb = q(va + 40)
    z1 = q(va + 32); z2 = q(va + 48)
    if cn is None or tb is None or sz is None:
        return None
    if z1 != 0 or z2 != 0:
        return None
    name = s_at(cn, 300)
    if name is None or sz > 0x800000:
        return None
    if tb and not (DT_LO <= tb < DT_HI):
        return None
    return (name, sz, tb)

def read_fields(tbl, cap=4000):
    out = []
    if not tbl:
        return out
    for k in range(cap):
        va = tbl + 72 * k
        p0 = q(va); p1 = q(va + 8); p2 = q(va + 16); pk = q(va + 24)
        p5 = q(va + 40)
        if p0 is None:
            break
        if p0 == 0 and p2 == 0 and pk == 0:
            break                     # all-zero terminator
        ty = s_at(p0, 300)
        nm = s_at(p2, 200)
        if ty is None or nm is None:
            break
        out.append(dict(va=va, type=ty, suffix=(s_at(p1, 64) or ""), name=nm,
                        off=pk & 0xFFFFFFFF, size=pk >> 32,
                        comment=(s_at(p5, 500) or "")))
    return out

# --- locate every descriptor by scanning .data at 8-byte alignment -----------
cand = []
ptr_rd = (arr >= RD_LO) & (arr < RD_HI)
zero = (arr == 0)
i = np.arange(arr.size - 7)
sel = i[ptr_rd[1:arr.size - 6] & zero[4:arr.size - 3] & zero[6:arr.size - 1]]
print("numeric descriptor candidates: %d" % sel.size, file=sys.stderr)

classes = {}
for j in sel.tolist():
    va = DT_LO + j * 8
    d = is_desc(va)
    if not d:
        continue
    name, sz, tbl = d
    if not tbl:
        continue
    classes[va] = dict(va=va, name=name, sizeof=sz, table=tbl)

print("class descriptors found: %d" % len(classes), file=sys.stderr)

db = []
for va in sorted(classes):
    c = classes[va]
    c["fields"] = read_fields(c["table"])
    c["n"] = len(c["fields"])
    db.append(c)

# how contiguous is the descriptor array?
vas = sorted(classes)
runs = []
cur = [vas[0]]
for a, b in zip(vas, vas[1:]):
    if b - a == 56:
        cur.append(b)
    else:
        runs.append(cur); cur = [b]
runs.append(cur)
runs.sort(key=len, reverse=True)
print("descriptor array runs (stride 56): %d; biggest %s" %
      (len(runs), [len(r) for r in runs[:6]]), file=sys.stderr)
print("total fields via descriptors: %d" % sum(c["n"] for c in db), file=sys.stderr)

json.dump(db, open("db.json", "w"), indent=1)
