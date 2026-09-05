#!/usr/bin/env python3
"""Find RIP-relative references in .text to a given VA, and confirm them by
disassembling backwards with capstone.  Static; the exe is only read."""
import sys
import numpy as np
import capstone
from refwalk import data, secs

TARGETS = [int(a, 16) for a in sys.argv[1:]]

for n, lo, hi, raw, rsz in secs:
    if n == ".text":
        T_LO, T_RAW, T_SZ = lo, raw, rsz

b = np.frombuffer(data[T_RAW:T_RAW + T_SZ], dtype=np.uint8).astype(np.int64)
N = b.size - 4
d = (b[0:N] | (b[1:N + 1] << 8) | (b[2:N + 2] << 16) | (b[3:N + 3] << 24))
d = np.where(d >= 0x80000000, d - 0x100000000, d)   # sign extend
i = np.arange(N, dtype=np.int64)
key = d + T_LO + i                                   # == TARGET - 4 for a hit

md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = False

for TARGET in TARGETS:
    hits = np.nonzero(key == TARGET - 4)[0]
    print("### RIP-relative candidates for 0x%x : %d" % (TARGET, hits.size))
    for h in hits.tolist()[:40]:
        # the disp32 ends at byte h+4; back up and find an instruction that ends there
        shown = False
        for back in range(3, 11):
            st = h - back
            if st < 0:
                continue
            code = data[T_RAW + st:T_RAW + st + 20]
            try:
                ins = next(md.disasm(code, T_LO + st))
            except StopIteration:
                continue
            if ins.size == back + 4 and "rip" in ins.op_str:
                print("   0x%x  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
                shown = True
                break
        if not shown:
            print("   0x%x  (disp32 site, no clean instruction decode)" % (T_LO + h))
