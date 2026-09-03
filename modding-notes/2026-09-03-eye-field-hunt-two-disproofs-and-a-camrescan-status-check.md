# The eye-field hunt: two disproofs, plus confirming `ringcam` already solves camrescan

**Session:** `/pd`, dev PC, 2026-09-03. **The game was not launched, and nothing was run.**
Everything below is static PE reading (string extraction, `static-disasm.py xrefs`, raw `pefile`
reads) against `DOOMx64vk.exe`/`DOOMx64.exe` already on disk, plus reading source already in
`staging/doom-2016-vr/`.

## What this closes

OPEN block row: "mine the reflection database for an eye field on the view object (BFG's is
`viewEyeBuffer`)", and the overlapping "critical path is two eyes in one frame" row that pointed
at the same task plus §6f's per-draw copies.

## 1. The literal BFG-predicted names: disproved

`ENGINE-DOSSIER.md` §6d (2026-09-02, via `/gr`) predicted searching for the adjacent
`int`+`float` pair `viewEyeBuffer`/`stereoScreenSeparation` — the last two fields of BFG's
`renderView_t`. `llvm-strings -n 4` extraction of both exes (748,762 lines VK, 669,170 lines GL)
found **zero hits**, exact or loose substring, in either binary.
`[disproved 2026-09-03, n=2 exes, exhaustive substring search]`

## 2. A real camera-reflection cluster, cross-exe corroborated

A genuine cluster of camera-related reflection strings exists around vk_strings.txt
lines ~606000-606400 (curated extract:
`dev-archive/recon/2026-09-03-eye-field-mining/vk_string_cluster.txt`):

```
viewOrg, fov_x, [comment: "the projection matrix is derived from these"], fov_y, viewFwd,
cramZNear, viewLeft, leftFrameOffset, viewUp, rightFrameOffset, explicitProjectionMatrix,
useExplicitProjectionMatrix, vieworg, [comment: "the view matrix is derived from these"],
viewaxis, [comment: "transformation matrix, view looks down the positive X axis"],
forceIdentityViewMatrix
```

The same relative ordering (`viewFwd` -> `cramZNear` -> `viewLeft` -> `leftFrameOffset` ->
`viewUp` -> `rightFrameOffset`) exists independently in `gl_strings.txt` at its own, different
offsets (~519600+) — the two exes are independently linked, so the same neighbour sequence
surviving in both is real corroboration the cluster is a compiled structure, not extraction
noise. `[inferred-static, n=2 independent exes, cross-corroborated ordering]`

A separate stereo-specific comment sits in the same neighbourhood: "For steroescopic 3D
rendering, we don't want to allow the hands/weapons to use a custom (inconsistant) FOV" —
plausibly decorating `inhibitModelFovScale`, not investigated further this session.

Also found: a `stereo`-substring sweep of the whole VK string table turned up
`topBottomStereo`/`leftRightStereo` immediately before the four known `stereoRender_*` cvars —
**these are already recorded**, `ENGINE-DOSSIER.md` §15 line 76 / `status/doom-2016-vr.md` since
2026-08-26, not a new finding this session.

## 3. `leftFrameOffset`/`rightFrameOffset` traced to an xref — and disproved as the eye field

`leftFrameOffset` and `rightFrameOffset` were the most plausible candidate pair by name. Static
xref (`static-disasm.py xrefs` on each string's VA) found exactly one absolute-pointer reference
to each, in `.data`, **72 bytes apart — one record-stride, i.e. adjacent entries in the same
table.** Full reproduction and record dump:
`dev-archive/recon/2026-09-03-eye-field-mining/xref_record_dump.txt`.

Both records have the identical shape:

```
{ typeName="unsigned char", arraySuffix="[256]", fieldName=<the string>,
  (u32 byteOffset, u32 size) = (0, 256) for left / (256, 256) for right,
  emptyStringConst, padding }
```

**This is a C++ reflection/serialization table entry describing
`unsigned char leftFrameOffset[256]; unsigned char rightFrameOffset[256];` declared back to back
in some class — a pair of fixed 256-byte BYTE BUFFERS, not scalar floats.**
`[verified-numerically 2026-09-03, n=2 adjacent table records, consistent field layout]`

That is inconsistent with a per-eye camera offset, which needs one float (or at most a small
vector) per eye, not a 256-byte buffer. **The name match was misleading — this is very likely a
pair of fixed-size string/path buffers** (e.g. per-eye screenshot or capture filenames — id Tech
commonly sizes path buffers at 256), unrelated to the runtime stereo transform.
`[disproved 2026-09-03]` as a candidate for the per-eye camera offset field, despite surviving
the earlier structural-proximity check. The string and its table entry are real, referenced,
compiled data (not dead strings) — just not what the name suggested.

**Net result of the mining task this session: two named-pair hypotheses tested, both
disproved by direct evidence (absence, then type mismatch).** No positive candidate for the eye
field was found. The row stays `[PD]` OPEN — `[hypothesis]` is still on the table that the
per-eye numeric offset either has no dedicated reflected field name (folded into a generic
"projection offset" or similar), or lives in a struct this session's cluster search did not
reach. Nothing here rules that out; it just narrows what has already been checked.

## 4. `ringcam` already implements §6h-4's prescribed fix — this is not open static work

The other half of the merged OPEN row pointed at "§6f's per-draw GPU copies" as static work
still to do. Reading `staging/doom-2016-vr/proxy-vulkan/src/{camhunt.c,ringcam.c,framespy.c}`
in full: **`ringcam.c` already is the fix `ENGINE-DOSSIER.md` §6h-4 prescribes** ("stop scanning
64 MB and stop caching addresses... scan only the range written this frame"). It hooks
`vkCmdBindDescriptorSets` for the live dynamic-offset window, bounds its one-off learning scan
to `LEARN_CAP` (512 KB, not 64 MB), and probes per frame at `offset + delta` with no cached
absolute address and a verify-before-write guard. It was built and `[compile-verified
2026-09-01]` (clean build, 246 exports, 96/96 imports covered, off-game smoke test passed) —
**already documented in `status/doom-2016-vr.md`, never run against the game, resume point
already recorded** (`ringlearn` -> `ringstat` -> `ringyaw 20` -> screenshot).

Note the discrepancy between `camhunt.c`'s `SCAN_BUDGET_BYTES = 96u << 20` (96 MB) and the
dossier's stated "64 MB" figure: `camhunt.c` is the **old**, still-present blanket-scan tool
(`snapa`/`snapb`/`camrescan`'s `runDiscovery`), whose budget was independently raised to 96 MB at
some point without the dossier prose being updated; `ringcam.c` is the **new** tool that replaces
it for the per-frame write path and was sized against the measured ~137 KB/frame window, not
against `camhunt`'s constant. The two files coexist; `camhunt`'s functions
(`camhunt_biggestMapping`, `camhunt_trackMapping`) are still used by `ringcam` for mapping
bookkeeping, but the write-side blanket scan (`camrescan`) is what the dossier's freeze warning
is about, and it is superseded by `ringcam` for that purpose, not deleted. `[inferred-static]`

**Conclusion: there is no remaining static work on this half of the row.** The next action is
inherently a live one (does `ringyaw 20` visibly rotate the view — untested, not disproved), and
it is already fully specified as a resume point. Continuing to list it as static `[PD]` work
overstated what a `/pd` session can still do here.

## What is NOT established

- Which field, if any, holds the actual per-eye stereo offset at runtime — still unknown.
- Whether `ringcam`'s write actually moves the rendered view — untested by design (needs the
  game running); every earlier attempt wrote to stale slots and could not have shown a positive.
- Whether resubmission-based two-eye compositing (copy result out, rewrite uniform, resubmit,
  composite) works end to end — this depends on the `ringyaw 20` result and was correctly not
  built ahead of that confirmation (a contingent item, not `[PD]` work, per this command's own
  scope rule).

**Diagnostic if `ringyaw 20` shows no rotation despite `ringstat` reporting learned deltas:**
that would point at the delta-based probe missing the actual write-time copy (e.g. the game
recomputes the block after `vkCmdBindDescriptorSets` records the offset, so the delta target is
stale by write time) — not at the general resubmission approach, which `framespy` already
confirmed is legal independently of `ringcam`.
