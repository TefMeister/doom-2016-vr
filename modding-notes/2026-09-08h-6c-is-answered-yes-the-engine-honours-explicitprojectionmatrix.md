# 2026-09-08h — §6c is ANSWERED **YES**: the engine honours `explicitProjectionMatrix`

*Session: `/lm doom-2016-vr`, dev PC, one launch, fully autonomous. Both starred rows were run in
that single session.*

**⭐⭐ DOOM reads `renderView_t::explicitProjectionMatrix` and renders with it. Per-eye projection is
a supported input to this engine.** That is the outcome the row called "the categorically easier
project", and it has been the open question since §6c was written.

`uniscan`, the other starred row, returned a clean negative that narrows the next step.

---

## 1. ⭐⭐ `rvhold` — §6c is answered, and the answer is yes

The 2026-09-08c session could not ask this question: a one-shot write was erased before any frame
consumed it, and the matrix was all zeros at rest, so setting the flag alone aimed the engine at a
degenerate projection. `rvhold` writes **matrix and flag every frame**, which is what makes a
negative meaningful — and what produced a positive.

Address: **`base + 0x360F6B0`**, derived rather than re-hunted (see §3), `rvcheck` confirming
`confidence 100/100`, `vieworg = (1728.00, 5440.00, 6372.16)` = the save's start position.

### The measurements

Mean absolute luma delta between full frames, same stationary viewpoint:

| comparison | delta |
| --- | --- |
| **scene-animation floor** (baseline vs baseline a minute later) | **7.24** |
| fov 40 held vs baseline | **24.24** |
| fov 40 released → baseline again | 7.24 |
| fov 140 held vs baseline | **25.83** |
| fov 140 released → baseline again | **4.39** |
| **fov 40 held vs fov 140 held** | **26.42** |

`[verified-live 2026-09-08, n=2 arms, each with its own release control]`

Every "changed" reading is ~3.5× the animation floor, and **each change reverted when the hold was
released.** The picture changes only while the hold is armed. That is the causal chain the row asked
for, and the tool's own reading table is explicit: *"Picture CHANGED at all (even wrongly) ⇒ 6c is
ANSWERED YES."*

### The two values give DIFFERENT pictures, which rules out "it only reacts to the flag"

`fov 40 held vs fov 140 held = 26.42` — the two held states differ from each other as much as each
differs from baseline. So the engine is reading **our matrix**, not merely responding to a boolean.

### ⚠️ The mapping is INVERTED, and that is a tuning detail rather than a blocker

- `fov 40` (narrow — should zoom **in**) produced a **wide, hazy, washed-out** view.
- `fov 140` (wide — should show **more**) produced a view **zoomed in**, a narrow magnified slice.

That inversion is the signature of a reciprocal/convention mismatch in the focal term — `tan(fov/2)`
where `1/tan(fov/2)` is wanted, or a row/column-major or reverse-Z difference. **The engine honours
the field; our constructed matrix simply is not yet the right one.** Getting it right is arithmetic
against a working feedback loop, which is a completely different situation from the last three days.

### Counters, and one thing they do not say

```
arm 1 (fov 40):  at present writes=3599 HELD=3555 ZEROED=44   REWRITTEN=0
                 at submit  writes=7200 HELD=3756 ZEROED=3443 REWRITTEN=0
arm 2 (fov 140): at present writes=3599 HELD=3598 ZEROED=1    REWRITTEN=0
                 at submit  writes=7200 HELD=3620 ZEROED=3579 REWRITTEN=0
```

`REWRITTEN=0` throughout — the engine never puts a *different* matrix back; it zeroes. At **present**
the hold is almost perfect (3598/3599 on arm 2); at **submit** it is roughly half zeroed. So the
engine clears the field between those two points each frame, and the hold is winning at the point
that matters. ⚠️ **NOT established: which of the two write points the render actually consumes.**
The picture changed, so at least one of them is early enough; nothing here says which.

## 2. `uniscan` — a clean negative that narrows the next probe

| slack | window | scanned | result |
| --- | --- | --- | --- |
| 64 KB (default) | 996 KB | 2217 KB | **0 projection-shaped blocks** — scan COMPLETE |
| 1024 KB | 4138 KB | 8192 KB | 0 — ⚠️ **BYTE CAP REACHED, incomplete, proves nothing** |
| 256 KB | 3370 KB | 6965 KB | **0** — scan COMPLETE |

`[measured 2026-09-08, n=2 complete scans]`

So **no 4×4 anywhere in the bound uniform window has the strict perspective shape** (`m[15]=0` with
±1 at `m[11]` or `m[14]`), across a 3.37 MB window.

⚠️ Read the middle row carefully: the 1024 KB attempt hit the byte cap and is **not** evidence. Only
the 64 KB and 256 KB runs completed, and it is those two that carry the negative.

⚠️ This does **not** revive or refute the ring finding — that was 09-08c, about camera *copies*, in a
different region. The tool says so itself, and it is right to: the projection could still be present
in a form the shape test does not recognise — premultiplied into a view-projection, stored as 3×4,
or split across two bindings. **The next probe is a `[PD]` change: drop the `m[15]=0` requirement.**

**And the priority of that probe has dropped sharply**, because §1 gives a supported, engine-blessed
input that does not require finding the matrix in memory at all.

## 3. The §6h RVA holds across a third module base

`base + 0x360F6B0` was **derived, not re-hunted** — no `psearch`/`pnarrow` chain this session — and
`rvcheck` confirmed a `renderView_t` at `confidence 100/100` with the correct `vieworg`. Module base
this run: `0x00007FF7BFDA0000`, against `0x00007FF7646B0000` this morning and `0x00007FF74D320000`
on 2026-08-25. `[verified-live 2026-09-08, n=3 distinct bases]`

That turns a ~4-minute chain into two commands, and it is now the recommended way to reach the
struct.

## 4. ⚠️ A mistake I made, recorded because the shape of it recurs

The first `fov 140` arm used a **600-frame budget ≈ 10 s**, and my capture landed *after* it expired
— so I measured a released frame and read "fov 140 does nothing", which sat oddly beside fov 40's
large change. I nearly wrote that up as "the effect is value-dependent in a strange way".

The log settled it: `ARMED ... for 600 frames` at `18:19:00.471`, `released (frame budget expired)`
at `18:19:10.470`, capture after that. Re-run with 3600 frames and the effect reproduced at 25.83.

**The lesson is about arming windows, not about this game:** when a probe self-expires, the capture
must be inside the window, and the log timestamp is what proves it was. Check the arm/release
timestamps against the capture time before believing any null from a timed probe.

## 5. Automation

| capability | status |
| --- | --- |
| 1. menu → gameplay | ✅ proven again |
| 2. console / exec commands | ✅ file channel; ⚠️ `backend sendinput` + `typeroute sendinput` first — the default `inproc-keystate` does not reach this game |
| 3. character + camera | not exercised (not needed; the player stood still throughout, which is what made the frame deltas clean) |
| 4. self-close | ✅ graceful through the game's own menu, no `taskkill` |

⚠️ The automation channel does not start draining until the game is fully loaded (~2 min here);
commands sent earlier queue silently. Wait for `[auto] automation ON` before expecting answers.

## 6. What to run next time

**Fix the projection convention.** The engine honours the field and the mapping is inverted, so this
is now arithmetic with a live feedback loop: build the matrix the engine's own `fov_x`/`fov_y` imply,
hold it, and confirm the picture is *unchanged* — that proves the convention is right. Then, and only
then, apply a per-eye off-axis shift, which is the actual VR goal.

That is a `[PD]` build plus one launch, and it is the first time this project has had a route with a
working feedback loop at the end of it.

Evidence: `dev-archive/recon/2026-09-08h-6c-is-answered-yes-the-engine-honours-explicitprojectionmatrix/`
— the full proxy log plus the five frames (baseline, fov 40 held, released, fov 140 held, released).
