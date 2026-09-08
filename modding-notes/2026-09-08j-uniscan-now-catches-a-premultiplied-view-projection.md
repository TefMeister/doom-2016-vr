# `uniscan` now catches a premultiplied view-projection

`/pd`, dev PC, 2026-09-08j. **The game was not launched. Nothing here has been run.**

Source: `staging/doom-2016-vr/proxy-vulkan/`. Deployed `vulkan-1.dll` md5 `fd5b745c…`, 205,312 B,
dated backup kept.

## The hole was real, and it is now measured rather than argued

`proj_classify` required `m[15] == 0`. That is right for a **bare** projection and wrong for a
**combined** one: premultiplying a rigid view `V` by a projection `P` gives

```
(V*P)[3][3] = V.row3 · P.col3 = -tz
```

— the camera's distance along view z. So every premultiplied view-projection was rejected **by
construction**, and many engines upload only the combined matrix.

Built by actually multiplying a view by a projection rather than hand-writing what one "looks like",
the test matrix comes out with **`m[15] = -900.0000`** against a view translation of `tz = 900`.
Exactly `-tz`, so the prediction is confirmed numerically rather than asserted.
`[verified-numerically 2026-09-08]`

## The discriminator changes shape too

A bare projection has a single ±1 in the w column. Premultiplying **rotates** that column, so the
±1 is spread across it and what survives is the norm:

| quantity | value for a rigid view |
| --- | --- |
| `\|(m[3], m[7], m[11])\|` | ≈ 1 |
| `\|(m[0], m[4], m[8])\|` | `p00` — the focal scale |

`PROJ_VIEWPROJ` tests those two norms instead of looking for a literal ±1. On the test matrix it
recovers **fov (90.00, 60.00)** from the values it was built with.

## It is a weaker filter, so it is measured separately

Two norms are a looser test than an exact ±1, so the false-positive rate could not be assumed to
match the bare forms' `0 of 200,000`. Measured: **1 of 200,000 random 64-byte blocks (0.0005%)** —
low enough that a 3.4 MB live scan stays readable. `[verified-numerically 2026-09-08]`

And loosening a rule is exactly where a filter starts accepting everything, so the old rejections are
re-asserted: **all-zero, identity and a camera-to-world matrix are all still rejected** — identity
because its w column is `(0,0,0)` rather than unit length, camera-to-world because its w column is
huge.

`uniscan`'s "nothing found" advice is updated too: it used to name *"drop the `m[15]=0`
requirement"* as the next probe. That is now spent, so it says so, and points at the one thing still
uncovered — **a 3×4 (48-byte) layout, which has no `m[15]` at all and is matched by no branch here.**

## Verification

- Builds clean; 265 exports; covers all 96 imports `DOOMx64vk.exe` needs. Reproducible: two builds
  hash identically. `[compile-verified 2026-09-08]`
- Host suite **98 checks, 0 failures** (was 88).
- Deployed byte-identical; `deployed.sh record` re-run.

**Nothing here has been run in the game.**

## Honest priority

⚠️ **This row was marked ⬇️ by `/lm` and that judgement stands.** The explicit-matrix route needs no
memory hunt at all, and it is the live path. This is the fallback if the convention work stalls —
it is now a *better* fallback, not a reason to prefer it.

The next launch's `uniscan` costs one command and, unlike before, a null result now genuinely means
"no projection-shaped block here" rather than "we only looked for bare projections".

## What is NOT established

- That a view-projection is in the bound window. Two complete scans found nothing under the old
  filter; this widens what would be caught, and has not run.
- The 3×4 case. Named, not handled.
