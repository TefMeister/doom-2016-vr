# 2026-09-01 — the camera is one static global, and the elevated-camera test passes

Live autonomous session, dev PC. The user launched DOOM and handed it over; the bisection left open
on 2026-08-31 was completed in one sitting, as it had to be.

## The headline

**`DOOMx64vk.exe + 0x360F6B0`** (absolute `0x00007FF75092F6B0`, module base `0x7FF74D320000`)
holds the camera's **origin plus a full orthonormal basis** — twelve contiguous floats matching the
engine's own `globalViewOrigin` / `Fwd` / `Left` / `Up` renderparm quartet
`[verified-live 2026-09-01, n=1 process instance]`.

Holding that one address displaces the view. Raising it 60 units on Z gives a **clean elevated
camera: the world renders correctly from a position the player is not at** — no culling collapse, no
void, geometry and lighting all resolve. Evidence:
`doom-2016-vr-dev-archive/recon/2026-09-01-camera-address-isolated/`.

## It answers run 12's open question

Run 12 could not tell whether the effect was the camera or the player entity's origin, because the
HUD *and* the weapon vanished together. The struct dump settles it: **the stored basis carries
pitch** (7.4° of it). The player body does not pitch in this game; the view does. It is the camera.

## The control that makes the finding safe

Writing the address every frame with **the value it already holds** changes nothing at all — HUD,
crosshair and weapon stay exactly where they were. So the HUD/weapon loss under displacement is
**caused by displacing the view**, not by our writing into engine memory.

This is the standing rule from 2026-08-31 applied in the other direction. That rule said a negative
result is only evidence if the test could have produced a positive one. The mirror image is just as
important: **a positive result is only attributable if you have shown the mechanism alone does
nothing.** One extra frame of work, and it converts "holding this address breaks the HUD" from
ambiguous into a specific claim about displacement.

## Bisection, and what made it cheap

2280 (`psearch` tol 1.0) → 697 (`pnarrow` tol 0.5) → 349 → 175 → 88 → 44 → 22 → 11 → 5 → 3 → **1**.

Ten halvings plus three single-address tests, about twenty minutes end to end. `pother` — added at
the end of the last session precisely because a discarded half had cost a full rebuild — was used
five times and saved a rebuild each time.

Every round was judged by **opening the screenshot**. The HUD strip was cropped out of each capture
so the check stayed a direct look at the image while costing almost nothing, rather than becoming a
number standing in for one. That is the fourth run in a row where the image was unambiguous.

Halfway through, the culprit had been in the upper half three rounds running, so the remaining
rounds tested the second half **first**. That is a scheduling choice, not an assumption: a wrong
guess costs exactly one `pother`, and it halved the number of captures.

## Traps found, both about the keyboard

**1. The console key on this machine is a DEAD KEY.** The layout here reports `0x0425`, and on it:

| VK | scancode | |
|---|---|---|
| `VK_OEM_3` (0xC0) | 0x1A | what the proxy's `console` command sends — **wrong key** |
| `VK_OEM_8` (0xDF) | **unmapped (0)** | what the 2026-08-31 note recorded — sends nothing at all |
| `VK_OEM_7` (0xDE) | **0x29** | the key DOOM's console is actually on, here |

This **supersedes** the 2026-08-31 dossier note that gave `VK_OEM_3 → 0x28` and the console as
`VK_OEM_8`/`0xDF`. Neither number reproduces on this machine today. The durable lesson is not the
numbers — it is that **you must ask the running system, not a remembered table**:
`MapVirtualKeyA(vk, 0)` forward and `MapVirtualKeyA(scan, 1)` backward, at the moment you need it.

**2. That key composes with the next character.** After opening the console, the first character
typed gets combined with a pending dead-key accent: `getviewpos` arrived as `Çgetviewpos` and
`com_...` as `*om_...`. Two failed commands looked exactly like a broken input backend.

Fix, now baked into the session helper: after opening the console send **space, then backspace** —
the space absorbs the composition, the backspace removes it, and the real command types clean.

## Housekeeping that bit once

The `getviewpos` helper toggles the console open and closed, so it must be entered with the console
**closed**. Called with it already open, it closed the console and typed `getviewpos` into the game
as movement keys. No harm, but the helper now opens, reads, captures and closes as one unit so its
pre- and post-state are the same.

## Next

1. **Re-measure the RVA on the next launch.** Stability across restarts is `[inferred-static]` from
   the region type and has been seen in exactly one process. If it holds, this project never needs
   the value hunt again — which would be worth more than the address itself.
2. **Write the basis, not just the origin.** A yaw needs `forward` and `left` rotated together;
   `phold` writes three floats and the code needs a small extension. This is the real test of
   whether the address is a control point or only a read-back.
3. Find out why the HUD and weapon drop out under displacement — it matters, because a VR camera
   that costs the HUD is not finished.
