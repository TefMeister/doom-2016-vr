#!/usr/bin/env python3
"""Query the scanned run table."""
import sys, json, re
runs = json.load(open(sys.argv[1]))
mode = sys.argv[2]
pat = sys.argv[3] if len(sys.argv) > 3 else None

def show(r, mark=None):
    print("=== run @0x%x  %d fields ===" % (r["start"], r["n"]))
    for f in r["fields"]:
        m = "  <<<" if (mark and re.search(mark, f["name"], re.I)) else ""
        c = ("   // " + f["comment"]) if f["comment"] else ""
        print("  0x%x  +%-6d sz=%-6d %s%s %s%s%s" % (f["va"], f["off"], f["size"],
              f["type"], f["suffix"], f["name"], m, c))

if mode == "find":                 # find runs containing a field name matching pat
    rx = re.compile(pat, re.I)
    hits = [r for r in runs if any(rx.search(f["name"]) for f in r["fields"])]
    print("%d runs matched" % len(hits))
    for r in hits:
        show(r, pat)
elif mode == "names":              # list matching field names across everything
    rx = re.compile(pat, re.I)
    seen = set()
    for r in runs:
        for f in r["fields"]:
            if rx.search(f["name"]):
                k = (f["name"], f["type"], f["suffix"])
                if k in seen: continue
                seen.add(k)
                print("0x%-12x run@0x%-12x n=%-4d +%-6d sz=%-6d %s%s %s   // %s" % (
                    f["va"], r["start"], r["n"], f["off"], f["size"], f["type"], f["suffix"], f["name"], f["comment"]))
elif mode == "at":                 # show run containing a VA
    v = int(pat, 16)
    for r in runs:
        if r["start"] <= v < r["start"] + 72 * r["n"]:
            show(r)
elif mode == "big":
    for r in sorted(runs, key=lambda r: -r["n"])[:int(pat or 20)]:
        print("run@0x%x n=%d  first=%s last=%s" % (r["start"], r["n"], r["fields"][0]["name"], r["fields"][-1]["name"]))
