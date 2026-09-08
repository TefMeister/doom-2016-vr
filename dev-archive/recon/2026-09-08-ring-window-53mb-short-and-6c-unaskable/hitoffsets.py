import re

LOG = r"D:\Program Files (x86)\Steam\steamapps\common\DOOM\doom_vk_proxy_log.txt"
BASE = 0x00000282637E0000          # map 2, from `mappings`
SIZE = 65536 * 1024                # 64 MB
WIN_LO, WIN_HI = 0, 2832128        # the span ringcam's LEARN actually scanned

txt = open(LOG, encoding="utf-8", errors="replace").read()
hits = [int(m, 16) for m in re.findall(r"HIT \d+ at ([0-9A-F]+)", txt)]
hits = sorted(set(hits))
print("findvec hits:", len(hits))

offs = [h - BASE for h in hits]
inside_region = [o for o in offs if 0 <= o < SIZE]
inside_window = [o for o in offs if WIN_LO <= o < WIN_HI]

print("inside region 2 :", len(inside_region), "of", len(offs))
print("inside LEARN win:", len(inside_window), "of", len(offs))
if inside_region:
    lo, hi = min(inside_region), max(inside_region)
    print("offset range    : 0x%X .. 0x%X  (%.2f MB .. %.2f MB)"
          % (lo, hi, lo / 1048576.0, hi / 1048576.0))
print("LEARN window    : 0x%X .. 0x%X  (%.2f MB)"
      % (WIN_LO, WIN_HI, (WIN_HI - WIN_LO) / 1048576.0))
gap = (min(inside_region) - WIN_HI) if inside_region else None
if gap is not None:
    print("nearest hit is %.2f MB PAST the end of the scanned window" % (gap / 1048576.0))
