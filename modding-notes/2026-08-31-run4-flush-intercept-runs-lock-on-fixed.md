# 2026-08-31 (run 4) — The flush intercept runs; the lock-on picked the wrong cluster

**Mode:** user launched, handed off, driven unattended. Clean graceful shutdown. No writes were
made to game memory this run — the intercept was left in **watch-only** mode, which is exactly why
the fault was caught harmlessly.

## What worked

The mechanism itself is sound. `camwatch` processed **~19,850 flushes live**, found **437 repeated
orthonormal transforms per flush**, and cost no visible performance or stability — no crash, no
artefacts, clean exit. Intercepting at `vkFlushMappedMemoryRanges` is a viable place to sit.

The camera was independently re-confirmed present during the same session: `getviewpos` gave
`1728 5440 6372.16 30.0 -0.0`, and `findvec` on those numbers returned **64 hits in region 2**.

## What failed, and why staging it mattered

`camstat` reported the tracked position as **`(-0.00 -0.00 -0.00)`**.

The modal-translation idea is fine — the camera *is* the most replicated transform. But **identity
matrices outnumber it**, and my guard rejected only *exact* zeros, so values like `-1e-8` passed
straight through and won the vote with 437 copies.

**Had this been armed to write, it would have applied a yaw rotation to several hundred identity
matrices every frame** — corrupting whatever they belong to, across the whole scene, with no
obvious link back to the cause. Watch-first cost one run and turned a potentially confusing mess
into a one-line log reading.

## Fixes (built, installed, needs a relaunch)

- **Reject near-origin transforms** (`|x|+|y|+|z| < 10`). Real positions here are in the thousands.
- **Prefer continuity over popularity once locked:** pick the cluster nearest the last known
  position. The camera moves smoothly frame to frame, which identifies it far more reliably than
  being popular — and popularity is precisely what mis-fired.
- **`camseed <x> <y> <z>`** — bootstrap the lock straight from `getviewpos`, so the first write
  targets matrices we have already confirmed by value rather than a guess.

## Next session

1. `getviewpos` → `camseed` those numbers → `camstat` to confirm the lock reads the real position.
2. `camyaw 15`, screenshot, check the view actually turned.
3. Ramp and reverse it, the way mouse-look was verified — proportional and reversible, or it is not
   really under control.
