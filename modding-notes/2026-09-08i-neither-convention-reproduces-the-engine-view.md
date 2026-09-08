# 2026-09-08i — neither convention reproduces the engine's view, and guessing should stop

*Session: `/lm doom-2016-vr`, dev PC, one launch, fully autonomous including the launch.*

**The row's success condition — an unchanged picture — was not met by either convention.** §6c stays
answered YES (the engine reads the field; now n=4 arms across two sessions), but constructing the
matrix from `fov_x`/`fov_y` does not reproduce what the engine itself draws.

## What the two conventions did

Both held the projection the engine's own `fov (90.00, 58.72)` implies, on `base + 0x360F6B0`
(derived, not re-hunted). Mean absolute luma delta against the baseline:

| convention | delta vs baseline | what it looked like |
| --- | --- | --- |
| — | **6.08** (release control) | the scene-animation floor |
| `inverse` (default) | **52.21** | ⛔️ **the world went BLACK** — HUD and viewmodel still drew, the 3D scene did not |
| `tangent` (`0 0 tan`) | **23.31** | the world renders, but warped — see below |

`[verified-live 2026-09-08, n=2 conventions, one release control]`

**The release control is what makes these causal:** after `rvholdoff` the frame returned to **6.08**
from baseline while the two held frames sat 52.96 and 22.76 away from it. The changes were the holds.

## The `tan` result is NOT simply "wrong FOV"

I searched uniform zoom factors to map the `tan`-held frame onto the baseline. **Best fit is ×1.00
with a correlation of only 0.378** — i.e. it does not match at *any* zoom. A projection differing
only in focal length would match well at some scale; this one does not. So the frame is **warped,
not merely rescaled**, and the focal term is not the only thing wrong.

⚠️ I nearly reported this as "FOV too wide" from the screenshot alone — it does look wider. The zoom
search is what showed that reading is not supported.

## What this means: stop guessing conventions, read the real matrix

Four conventions have now been tried across two sessions (fov 40, fov 140, `inverse`, `tangent`) and
none reproduces the engine's own view. The space of remaining guesses — reverse-Z, infinite far,
row/column major, handedness, and their combinations — is large, and each costs a launch.

**The cheap way out is already on the board and just became the priority:** the queued `[PD]` row to
**drop `uniscan`'s `m[15]=0` requirement**. `uniscan` found nothing because it demanded the strict
perspective shape; a premultiplied view-projection, a 3×4, or a reverse-Z form would all have been
skipped. **If the engine's actual projection can be READ out of the bound uniform window, the
convention stops being a guess** — hold exactly what was read, confirm the picture is unchanged, and
only then apply a per-eye shift.

That reverses the priority recorded on 2026-09-08h, which demoted `uniscan` on the grounds that the
explicit-matrix route needed no memory hunt. It does not need one to *write* — but it does to know
**what** to write.

## Automation — five capabilities

| capability | status |
| --- | --- |
| 1. self-launch | ✅ |
| 2. menu → gameplay | ✅ |
| 3. console / exec commands | ✅ file channel (⚠️ `backend sendinput` + `typeroute sendinput` first; the channel does not drain until the game is fully loaded, ~2 min) |
| 4. character + camera | not needed this run — the player stood still, which is what kept the frame deltas clean |
| 5. self-close | ✅ graceful through the game's menus, both dialogs verified |

⚠️ `rvscan` needs a `psearch`/`pnarrow` chain and refuses without one. **Deriving the address as
`module base + 0x360F6B0` skips that entirely** and worked again this session — a fourth distinct
module base (`0x7FF7BFDA0000`), `rvcheck` confirming confidence 100/100 with the right `vieworg`.

Evidence: `dev-archive/recon/2026-09-08i-neither-convention-reproduces-the-engine-view/`.
