#!/usr/bin/env python3
"""Static walker for the id Tech 6 reflection/serialisation field table in
DOOMx64vk.exe / DOOMx64.exe.  READ ONLY -- the exe is opened 'rb' and never
written.  The game is never launched.

Record shape established 2026-09-03 (dev-archive/recon/2026-09-03-eye-field-mining):
  off+0  qword -> char* typeName
  off+8  qword -> char* arraySuffix ("[256]") or 0
  off+16 qword -> char* fieldName
  off+24 u32 byteOffset, u32 size
  off+32 qword ?
  off+40 qword -> char* comment ("" const when absent)
  off+48/56/64 qword  (usually 0)
  stride = 72 bytes
"""
import sys, os, struct, re, json

import pefile

EXE = os.environ.get("DOOM_EXE", r"C:\Steam\steamapps\common\DOOM\DOOMx64vk.exe")

pe = pefile.PE(EXE, fast_load=True)
IB = pe.OPTIONAL_HEADER.ImageBase
data = open(EXE, "rb").read()

secs = []
for s in pe.sections:
    name = s.Name.rstrip(b"\x00").decode("latin1")
    va = IB + s.VirtualAddress
    vsz = max(s.Misc_VirtualSize, s.SizeOfRawData)
    secs.append((name, va, va + vsz, s.PointerToRawData, s.SizeOfRawData))

def sec_of(va):
    for s in secs:
        if s[1] <= va < s[2]:
            return s
    return None

def rd(va, n):
    s = sec_of(va)
    if not s:
        return None
    off = s[3] + (va - s[1])
    if off < 0 or off + n > s[3] + s[4]:
        return None
    return data[off:off + n]

def q(va):
    b = rd(va, 8)
    return None if b is None or len(b) < 8 else struct.unpack("<Q", b)[0]

IDENT = re.compile(rb"^[A-Za-z_][A-Za-z0-9_]{0,127}$")

def cstr(va, maxlen=400):
    if not va:
        return None
    b = rd(va, maxlen)
    if b is None:
        return None
    i = b.find(b"\x00")
    if i < 0:
        return None
    return b[:i]

def printable(b):
    return b is not None and all(32 <= c < 127 for c in b)

if __name__ == "__main__":
    print("ImageBase 0x%x" % IB)
    for s in secs:
        print("  %-8s VA 0x%x-0x%x raw 0x%x size 0x%x" % (s[0], s[1], s[2], s[3], s[4]))
