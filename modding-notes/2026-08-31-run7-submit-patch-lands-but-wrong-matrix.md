# 2026-08-31 (run 7) — Submit-time patching works; we were patching the wrong matrix

**Mode:** user launched, handed off, driven unattended. Clean graceful shutdown, no corruption.

## The mechanism is proven

Everything in the write path now works:

- `camseed` locked on a verified position and **held** (the run-4 clobber bug is fixed).
- **Discovery located 131 camera copies** at fixed offsets in one pass.
- The **`vkQueueSubmit` hook fires** and **72 of 131 copies are patched every submit**, with the
  translation re-verified before each write.

So we can find the camera, hold a lock on it, and write to it every frame, safely. That is the
whole machinery working end to end.

## But the rendered image does not change

`camyaw 20` → **1.31 %** pixel change. `camyaw 90` → **2.07 %**. For comparison, a real 90° turn via
mouse look changed the image beyond recognition. 1–2 % is the level's animated dust and smoke.

**We are writing to a matrix the renderer does not use for geometry.**

## Why: it is the camera-to-world matrix, not the view matrix

The matrix we found and patched is:

```
 0.867  -0.499   0.000   1728.000
 0.499   0.867   0.000   5440.000
 0.000   0.000   1.000   6372.160
```

A pure Z rotation of 29.9° (matching `getviewpos` exactly), with **the raw eye position in column
3**. That makes it **camera-to-world** — `inverseViewMatrix`, one of the renderparms the binary
names. Vertices are transformed by the **view/MVP** matrix, which is its inverse.

**The value search could never have found the view matrix**, because a view matrix's translation is
`-Rᵀ·t`, not the eye position — a different number entirely.

## The prediction that failed, and what it tells us

Computed both inverse conventions from the measured matrix and searched for each:

| Predicted view translation | Result |
|---|---|
| `-Rᵀ·t` = `(-4212.74, -3854.21, -6372.16)` | **0 hits** |
| `-R·t` = `(1216.38, -5578.75, -6372.16)` | **0 hits** |

Neither exists anywhere in memory. `[measured 2026-08-31]`

**That absence is the finding.** It says the view matrix does not carry a world-space translation at
all — which points hard at **view-origin-relative rendering**: id Tech keeps **`globalViewOrigin`**
as its own uniform (exactly the packed `vec4` with `w=1.0` we found first), and builds the view/MVP
matrices for geometry **already translated relative to that origin**. It is the standard defence
against float precision loss far from the world origin, and it explains why the binary names
`globalViewOrigin` as a first-class renderparm.

## ⇒ The consequence, and it is slightly embarrassing

If that is right, **the real view matrices have ~zero translation** — which means they are the
**437 near-origin orthonormal matrices I filtered out as "identity junk" in run 4**. The magnitude
floor I added to fix the lock-on is now excluding exactly the thing we want.

The run-4 fix was still correct for what it did (it stopped the *position* lock latching onto
zeros). But the conclusion drawn alongside it — that near-origin transforms are noise — was wrong.

## Next session: search by ROTATION, not by translation

1. Add `findrot` — locate matrices whose 3×3 matches a given basis, **ignoring translation**. Seed
   it with the camera's own `R` (and `Rᵀ`), which we can read exactly from the camera-to-world copy
   we already know how to find.
2. Expect hits among the near-zero-translation cluster. Confirm by checking that the 3×3 tracks
   `getviewpos`'s yaw as the player turns.
3. Patch those, with the same verify-before-write discipline, and re-run the yaw test. A working
   patch should be unmistakable — the mouse-look comparison gives us the bar.

Also worth trying, cheaply: patch `globalViewOrigin` (the packed vec4) **and** the view rotation
together, since under origin-relative rendering both are needed to move the eye.

## Kept for the record

- Submit-time patching costs nothing measurable: 131 offsets revisited per submit, no frame-rate
  complaint, no crash across the session.
- Discovery took one pass and found copies at **fixed** offsets that stayed valid — the ring-buffer
  worry from the previous session did not materialise (72/131 matched steadily).
