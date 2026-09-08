# The inversion is a reciprocal — and success is now *nothing happening*

`/pd`, dev PC, 2026-09-08i. **The game was not launched. Nothing here has been run.**

Source: `staging/doom-2016-vr/proxy-vulkan/`. Deployed `vulkan-1.dll` md5 `6c061c13…`, 204,288 B,
dated backup kept.

## The diagnosis, and it is checkable rather than asserted

2026-09-08h ran `rvhold` live and **the engine honours `explicitProjectionMatrix`** — but inverted:

| we sent | the picture rendered |
| --- | --- |
| fov **40** (narrow, should zoom in) | **WIDE** and hazy |
| fov **140** (wide) | **ZOOMED IN** |

That is exactly a reciprocal swap in the focal term, and the arithmetic covers **both** probes from
one cause:

```
sent fov  40  ->  m[0] = 1/tan(20°) = 2.7475  ->  2·atan(2.7475) = 140.0°   (WIDE, as seen)
sent fov 140  ->  m[0] = 1/tan(70°) = 0.3640  ->  2·atan(0.3640) =  40.0°   (ZOOMED, as seen)
```

Both land within a degree of what was observed. That is now **test 16** in the host suite, so the
diagnosis is a check that could fail rather than a story that sounds right.
`[verified-numerically 2026-09-08]`

⚠️ **A transpose cannot explain it.** `m[0]` and `m[5]` are on the diagonal, and a row/column-major
swap leaves them exactly where they are. The focal term really is reciprocal, not merely re-indexed
— which removes one of the three candidate causes the board listed.

## Two candidate fixes, and they differ in what else they change

| convention | focal term | depth row | explains |
| --- | --- | --- | --- |
| `std` | `1/tan` | standard | *nothing* — this is what rendered inverted |
| `tan` | `tan` | **unchanged** | the FOV inversion only |
| `inv` | `tan` | **inverted too** | the FOV inversion **and** the "hazy" half of fov 40 |

**`inv` is the default**, because one hypothesis — *the field is consumed as an inverse projection* —
explains both symptoms, where `tan` explains one and leaves the haze unaccounted for. `tan` is the
fallback if depth then looks right and the FOV is still wrong. `[hypothesis]` — neither has run.

The inverse is the closed form of

```
[ a 0 0  0 ]                     [ 1/a  0   0    0  ]
[ 0 b 0  0 ]   whose inverse is  [  0  1/b  0    0  ]
[ 0 0 c -1 ]                     [  0   0   0   1/d ]
[ 0 0 d  0 ]                     [  0   0  -1   c/d ]
```

and it is **not asserted from the algebra** — test 18 multiplies `M · M⁻¹` out and requires the
identity to 2×10⁻⁴. If the closed form were wrong, holding it would send the engine a matrix that is
not any projection at all and the launch would be spent on nothing.

## ⭐ The default changed, and the change *is* the experiment

`rvhold`'s default fov used to be **half** the live `fov_x` — a deliberate 2× zoom, because the
question was *"does anything change at all"*. 09-08h answered that **yes**.

So the question is now *"is our matrix **right**"*, and the sharpest form of it is to hold the
projection the engine's **own** fov implies and see nothing happen:

> **SUCCESS IS AN UNCHANGED PICTURE.**

`rvhold <addr>` with no fov now builds from the live `fov_x`/`fov_y` and says so in the log. Passing
a fov explicitly still gives a deliberate visible change.

⚠️ **fov 90 is a useless test value** and there is a test asserting why: `tan(45°) = 1`, so `std` and
`tan` produce an identical matrix there. A convention test that passed only at 90 would prove
nothing.

## Carried forward from 09-08h's own warning

The arm line now prints a reminder to **check the arming window before believing a null**. That
session had a 600-frame hold expire *before* its capture, which read as "fov 140 does nothing" and
nearly became a finding — the ARMED/released timestamps against the capture time are what caught it.

## Verification

- Builds clean; 265 exports; covers all 96 imports `DOOMx64vk.exe` needs. `[compile-verified 2026-09-08]`
- Host suite **88 checks, 0 failures** (was 64) — 24 new, covering the diagnosis reproducing both
  live probes, `tan` touching *only* the focal term, `M · M⁻¹ = I` multiplied out, `inv` and `tan`
  agreeing on the focal term and differing only in depth, the fov-90 degeneracy, and refusal of an
  unknown convention rather than silently falling back to `std`.
- Reproducible build: two builds hash identically. Deployed byte-identical; `deployed.sh record`
  re-run.
- The deployed DLL before this session was **exactly** the 09-08e build the `/lm` session ran
  (`0b666197…`), so the live result and this fix are on the same code lineage.

**Nothing here has been run in the game.**

## The next launch

```
backend sendinput ; typeroute sendinput     ← FIRST; the default backend does not reach this game
                                              (and the channel does not drain until fully loaded, ~2 min)
rvscan                                       ← or derive the address from §6h's RVA, which held across 3 bases
rvhold <addr>                                ← no fov, no convention: the engine's own fov, inverse form
rvholdoff                                    ← read the counters
```

| what you see | what it means |
| --- | --- |
| **the picture does not change** | **the convention is right.** The next step is a per-eye off-axis shift — the actual VR goal, and the first time this project has had one within reach. |
| **FOV correct, depth/haze wrong** | the focal fix landed and the depth row did not: re-run with `rvhold <addr> 0 0 tan` and compare. |
| **still inverted** | the reciprocal reading is wrong despite fitting both probes; read *which way* it moved and correct again — the loop is cheap now. |
| **`REWRITTEN` non-zero** | new behaviour: 09-08h saw `REWRITTEN=0` throughout, the engine only ever *zeroes* the field. |

⚠️ **Still not established: which write point the render consumes.** 09-08h measured a near-perfect
hold at *present* (3598/3599) and roughly half zeroed at *submit*. If a correct-looking matrix still
produces a wrong picture, that is the next thing to isolate, not the maths.

## What is NOT established

- That either fix is correct. **Neither has been run.**
- That the field is an inverse projection. It is the single hypothesis that covers both symptoms,
  which is why it is the default — not evidence that it is true. `[hypothesis]`
- Anything about depth correctness. "Hazy" is one word from one observation, and it is doing a lot
  of work in choosing `inv` over `tan`; if it turns out to have been fog or a load transition, the
  reasoning behind the default weakens even though the focal fix stands.
