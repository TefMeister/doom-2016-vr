# 2026-09-01 — the authoritative view address, isolated to one static global

Live session on the dev PC. The game was launched by the user and handed over ("all yours");
everything below was driven autonomously through the proxy's command channel.

## Result

The bisection begun on 2026-08-31 completed. The authoritative address is

**`DOOMx64vk.exe + 0x360F6B0`** — absolute `0x00007FF75092F6B0` at module base `0x7FF74D320000`
`[verified-live 2026-09-01, n=1 process instance]`

It is in the executable's **image** region, not the heap.

## What lives there

`pdump` of the address, with the player standing still at `getviewpos` = `799.93 4673.61 6407.39 219.3 7.4`:

```
+0    799.926  4673.610  6407.388      <- origin
+3     -0.767    -0.629    -0.129      <- forward
+6      0.634    -0.773     0.000      <- left
+9     -0.099    -0.082     0.992      <- up
+12     0.000     0.000     0.000
```

Twelve contiguous floats: **an origin plus a full orthonormal basis**, then zeros. Every row is unit
length and mutually perpendicular to within 5e-4. This is the quartet the binary names in its own
renderparm table — `globalViewOrigin`, `globalViewFwd`, `globalViewLeft`, `globalViewUp`
`[inferred-static]` for the naming, `[measured 2026-09-01]` for the layout.

It cross-checks against the game's own readout arithmetically:

- `cos(7.4°)·cos(219.3°) = -0.767` = forward.x
- `cos(7.4°)·sin(219.3°) = -0.628` = forward.y
- `sin(7.4°) = 0.129` = forward.z (sign per the engine's pitch convention)
- left = `(sin, -cos)(219.3°) = (0.633, -0.774)`, roll zero — matches row 2 exactly.

## It is the VIEW, not the player body

Run 12 left this open, since losing the HUD and the weapon together looked like the player entity
being displaced. The dump settles it: **the basis carries PITCH** (7.4° of it, in `forward.z` and in
the `up` row). A player body does not pitch in this game; the view does. What is stored here is the
camera's own origin and orientation.

## Evidence, in order

| file | what it shows |
|---|---|
| `01-ground-truth-getviewpos.jpg` | the console read that seeded the search |
| `02-control-hud-and-weapon-present.jpg` | control frame — HUD, crosshair, super shotgun all present |
| `03-holdall-697-effect.jpg` | all 697 narrowed candidates held at +40 X — HUD, crosshair and weapon gone, view displaced |
| `04-single-isolated-address-effect.jpg` | the **one** address held at +40 X — same effect, alone |
| `05-control-zero-delta-hud-intact.jpg` | **the control that matters**: the same address written every frame with the *identical* value — nothing changes, HUD intact |
| `06-camera-raised-60-units.jpg` | the view lifted 60 units on Z — a clean elevated camera, world rendering correctly |
| `07-restored-getviewpos-identical.jpg` | after release, `getviewpos` reads exactly what it read before |

## The control is the point

Writing the address every frame with **the value it already holds** produces **no change of any kind** —
the HUD, crosshair and weapon stay put. So the HUD/weapon loss is a **consequence of displacing the
view**, not an artefact of our writing to engine memory. Without that control, "holding this address
breaks the HUD" would have been ambiguous between the two.

## The elevated-camera frame is the project-relevant one

At +60 units on Z the world renders **correctly** from a position the player is not at: geometry,
lighting and the cave ceiling all resolve, no culling collapse, no black void. That is the property
this whole portfolio needs and the one Psychonauts spent weeks failing to get — here the culling
follows the camera for free.

## Bisection path

2280 (`psearch`, tol 1.0) → 697 (`pnarrow`, tol 0.5) → 349 → 175 → 88 → 44 → 22 → 11 → 5 → 3 → **1**.

Ten halvings plus three single-address tests. Every round judged by opening the screenshot, never by
a pixel metric. `pother` earned its keep three times (348, 174, 87, 6 and 2 all tested negative and
cost one command each instead of a full rebuild).

## Guards

Every hold auto-expired at 599 frames and restored originals — 697/697, 348/348, 349/349 and so on
down. `getviewpos` read identically before and after the whole sequence. The 64-unit clamp
(`HOLD_MAX_DELTA`) refused a 150-unit jump, exactly as designed after the 2026-08-31 freeze.

## Not yet known

- **Whether the RVA is stable across restarts is `[inferred-static]`, NOT verified.** It follows from
  the address being in the image region, but it has been measured in one process instance only.
  Re-measure on the next launch before relying on it.
- Whether writing the **basis** (rotation) behaves as well as writing the origin. `phold` writes three
  floats; a yaw needs `forward` and `left` rotated together, which needs a code change.
- Why the HUD and weapon drop out at all when the view is displaced.
