# The ring route was searching the wrong region for the wrong object

`/pd`, dev PC, 2026-09-08e. **The game was not launched. Nothing in this note has been run.**

Source: `staging/doom-2016-vr/proxy-vulkan/`. Deployed `vulkan-1.dll` md5 `0b666197…`, 202,752 B,
dated backup kept.

## The row, and why I did not write the design it asked for

The board asked me to *design* the successor to the dead ring route — "resubmit the game's own
command buffers and redirect the recorded draws at a second copy of the per-draw uniform region".

Reading the measurements behind it, the design turned out to be blocked on something cheaper and
more specific than a strategy, and that thing was **buildable in the same session**. So this note is
a correction plus an instrument rather than a plan.

## ⚠️ First: I over-stated something last session, and it is worth withdrawing plainly

On 2026-09-08d I called this row *"the fallback path"* and said it *"risks being wasted work"* if
§6c (`rvhold`) comes back yes. **That was wrong.** The two answer different questions:

- **§6c / `rvhold`** asks *how a different projection gets into a pass.*
- **The resubmission route** asks *how a second pass exists at all.*

Stereo needs both. If §6c is yes, the cheapest stereo is frame-sequential alternation — half
framerate and a temporal mismatch between the eyes. Resubmission is what gets both eyes from **one
recorded frame**, which is the thing the dossier already identified as possible because
`ONE_TIME_SUBMIT` is not set on any of the 8 command buffers `[measured 2026-09-01]`. It is not a
fallback; it is the other half.

## The correction: two reasons "the ring route is dead" does not mean what it looks like

The 2026-09-08c measurement is sound and is not disputed here:

```
252 camera hit(s): 0 with a usable delta, 252 too far from any bound offset
the nearest bound offset is 60673 KB BELOW the nearest copy
```

Corroborated independently by `framespy` in the same session: every pass's `dynOffset` range falls
in **3,783,680–3,794,176** (~3.78 MB) while the camera copies sit at **62.9–67.1 MB**. Two
instruments, same gap. Offset+delta probing genuinely cannot reach those copies however the window
is set.

**But two things follow that were not stated, and both are claims about our own code rather than new
speculation:**

### 1. The bound window itself was never searched

`ringcam` used the bound dynamic-offset range only as an *anchor to probe outward from*, toward
copies discovered elsewhere by value-matching. **The bound range is, by definition, the memory the
GPU reads** — a dynamic descriptor offset is where a shader's uniform slice begins. Nobody has
looked inside it.

### 2. `ringcam` could not have found a projection even if one were there

Its match test is:

```c
static int matches(const float *m, const float *origin)
{
    return fabsf(m[3]  - origin[0]) < MATCH_TOL
        && fabsf(m[7]  - origin[1]) < MATCH_TOL
        && fabsf(m[11] - origin[2]) < MATCH_TOL;
}
```

That accepts a block only when its fourth column equals the **camera origin** — a camera-to-world
matrix. **A perspective projection contains no camera position at all**, so it is rejected by
construction. So "252 hits, 0 usable deltas" is *silent* about whether a projection sits in the
bound window — and the projection is what per-eye stereo needs.

**The ring route was searching the wrong region for the wrong object.** Both halves are fixable, and
neither needs the game running to fix.

## What was built: `uniscan`

Scan the bound window itself, by **shape**, for a projection.

```
uniscan [slackKB]     one-shot, read-only, byte-capped
```

At the next present — **before** `ringcam_onPresent` clears the frame's offsets — it takes the span
of dynamic offsets bound this frame, adds a slack, and walks every tracked mapping over that window
at 4-byte stride, testing each 64-byte block with `proj_classify`.

Each hit is reported with its offset, **the nearest bound dynamic offset below it, and the delta** —
because that delta is exactly what a replay would reuse.

### The shape test (`src/projshape.c`, pure and host-tested)

A perspective projection has one structural signature: it moves z into w and has no constant w term.
Which index that lands on depends on the storage convention, so both are tested:

| layout | signature |
| --- | --- |
| **ROW** (row-vector, D3D) | `m[11] = ±1`, `m[15] = 0`, `m[14] ≠ 0` |
| **COL** (column-vector, GL/HLSL default) | `m[14] = ±1`, `m[15] = 0`, `m[11] ≠ 0` |

`m[0]` and `m[5]` are then `1/tan(fovX/2)` and `1/tan(fovY/2)`, so every hit is reported as **an
angle a human can check against the game's own FOV** rather than as sixteen anonymous floats.

It rejects, deliberately and with tests for each: the all-zero block (what an untouched uniform slice
looks like — this alone would otherwise produce thousands of hits), identity (`m[15] = 1`), a
camera-to-world matrix (so `uniscan` cannot rediscover what `ringcam` already finds), a block that
satisfies *both* conventions (ambiguous ⇒ coincidence, not a projection), absurd scales, and NaN.

**Measured false-positive rate: 0 of 200,000 random 64-byte blocks.**
`[verified-numerically 2026-09-08]`

### Bounded, because the last blanket scan nearly froze the game

`camrescan` scanned 64 MB of write-combined memory at ~42 ms/MB — about 2.7 s of stalled reads,
user-observed twice `[verified-live 2026-09-01, n=2]`. `uniscan`:

- scans only the frame's own bound offset window (~3.78 MB measured) plus a slack;
- caps total bytes at **8 MB** and says so in the log if the cap bites;
- is **one-shot** — armed by a command, disarmed after a single frame;
- **never writes.**

One usability fix came with it: `ringcam` only collected dynamic offsets while a ringcam mode was on,
so `uniscan` would have needed an unrelated `ringlearn` first and an empty result would have read as
*"the game binds nothing"* rather than *"nobody was recording"*. It now also collects while `uniscan`
is armed.

## Verification

- Builds clean under `-Wall -Wextra`; 265 exports; covers all 96 imports `DOOMx64vk.exe` needs.
  `[compile-verified 2026-09-08]`
- Host suite **64 checks, 0 failures** (was 52) — 12 new for `proj_classify`, including one test per
  rejection case and the false-positive measurement above. `[verified-numerically 2026-09-08]`
- New accessor `camhunt_mappingAt()` beside the existing `camhunt_mappingCount()`, under the same
  lock as every other `g_maps` reader. `uniscan` needs *every* mapping, not "the biggest" or "the
  value-located one", because a bound offset is just a number and which mapping it lands in **is part
  of what is being measured**.

**Nothing here has been run in the game.**

## The next launch

```
backend sendinput ; typeroute sendinput      ← FIRST, or commands silently do nothing
uniscan                                       ← one frame, read-only
```

| what the log says | what it means |
| --- | --- |
| **hits at a small, stable delta above a bound offset** | **The successor to the ring route is live.** That matrix is what the GPU reads; submit the game's own command buffers twice and rewrite it between the submissions. Check the reported fov against the game's own before believing it. |
| **hits, but scattered / no bound offset below them** | Projection-shaped data is in the mapping but not in a slice any draw binds. Widen the slack and re-run before drawing a conclusion. |
| **nothing found** | It means no 4×4 in the bound window has the perspective *shape*. It does **not** mean the ring is unreachable — that was the 09-08c finding about camera *copies*, a different object in a different place. Cheapest next probes, in order: a wider slack, then dropping the `m[15] = 0` requirement to catch a pre-multiplied **view-projection**. |
| **`BYTE CAP REACHED`** | the scan is incomplete; raise the cap or narrow the slack. |

## What is NOT established

- That a projection is in the bound window. **That is what `uniscan` is for**, and it is untested.
- That the projection is stored as a plain 4×4 at all. It may be pre-multiplied into a
  view-projection, stored as 3×4, or split across bindings — the "nothing found" row above says what
  to do about each.
- That resubmission works. `ONE_TIME_SUBMIT=0` says it is *legal* `[measured 2026-09-01]`; nothing
  has submitted anything twice.
- ⚠️ A shape match is **not** proof. `proj_classify` is a filter with a measured false-positive rate
  of zero on random data, which is not the same as zero on structured engine data.
