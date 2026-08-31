# 2026-08-31 — CORRECTION: the differential test that "disproved" camhunt had no movement in it

**Prompted by the user**, who asked whether early results might be wrong because the game was
stalled or otherwise not in the state I assumed. That instinct was right, and it found a real
error — though the confound turned out to be a different one than expected.

## What I claimed

That camhunt's address-based differential **cannot discriminate camera motion**, on the evidence:

| Run | changed | still orthonormal |
|---|---|---|
| `snapa` → **walk** → `snapb` | 2780 / 4096 | **319** |
| `snapa` → **stand still** → `snapb` | 2820 / 4096 | **331** |

"Standing still scores the same as walking" — so the differential is measuring buffer recycling,
not the camera. That went into the dossier and STATUS as a `[disproved]` fact.

## Why it is wrong

From `session-2026-08-31-run2.log`:

```
14:11:51  backend inproc
14:11:55  SNAPSHOT A
14:11:59  move keys=0x1 for 150 frames via inproc-keystate
14:12:04  SNAPSHOT B: 2780 changed; 319 orthonormal
14:12:48  SNAPSHOT A            <- control
14:12:51  SNAPSHOT B: 2820 changed; 331 orthonormal
14:14:05  move ... via inproc-keystate   <- isolated test: player moved ZERO units
```

**`inproc-keystate` does nothing** — established at 14:14:05, three minutes *after* the conclusion
was already drawn, and confirmed again the next run when `sendinput` moved the player 40 m under
identical conditions.

So the "walk" run and the "stand still" control were **the same condition**. Two identical
conditions scoring the same is not evidence about the differential; it is evidence that the test
had no independent variable.

## Status now

**The address-based differential is UNTESTED on DOOM, not disproved.** The dossier entry is
withdrawn with its own `[disproved]` tag rather than deleted, so the reasoning stays visible.

**What does NOT change:** the conclusion that the GPU-side camera is downstream of rendering stands,
because it rests on independent evidence — searches for both predicted inverse-view translations
returned zero hits, the transposed rotation basis does not exist as consecutive floats anywhere, and
patching the camera-to-world copy across 72 per-draw blocks moved the image by 1–2% (dust). None of
those depend on the broken differential.

## The method rule this earns

**A test whose independent variable is applied through an unverified mechanism proves nothing.**

I varied "movement" using an input backend I had not yet confirmed could move anything, and then
drew a conclusion about a *different* system from the result. The right order is: verify the knob
turns, *then* trust what the dial says.

This is the same family as the attribution trap recorded earlier the same day (crediting
`sendinput`'s 15 m walk to `inproc` because the probe changed three things before I looked). Both
are failures to establish that the thing I thought I was manipulating was actually being
manipulated. Worth stating as one rule rather than two anecdotes:

> Before believing a measurement, confirm that the condition you think you varied actually varied.
> Prefer a control you can see — a screenshot, an on-screen readout — over an assumption that a
> command did what its name says.

## Re-test, if wanted

Cheap now: scans take ~4 s and run off the render thread. `backend sendinput` → `snapa` → `move fwd
200` → `snapb`, against a stand-still control. Low priority, since the GPU-side copy is downstream
regardless, but it is the honest way to settle what the differential can actually do.
