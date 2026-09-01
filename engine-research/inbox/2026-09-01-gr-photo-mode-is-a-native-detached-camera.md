# `pm_photoMode*` is a shipped, ungated, detached free camera — and it explains why §6h's elevated view rendered correctly

**From:** `/gr doom-2016-vr`, 2026-09-01 (dev PC)
**For:** the modding session — fold into `ENGINE-DOSSIER.md` §6h, §9 and §13.
**Full write-up:** `external-research/topics/2026-09-01-retail-photo-mode-is-a-native-detached-camera.md`

## The dossier text this targets

§9: *"`pm_photoModeFriction`, `pm_photoModeMaxDist` — photo-mode camera tuning — **a native detached
camera exists** — unexplored."*

§6h: *"⭐ The elevated-camera test passes… no culling collapse and no black void. **Culling follows
the camera here for free**, which is exactly what Psychonauts spent weeks failing to get."*

## What public research found `[reported, community + games press, 2016–2017]`

Photo Mode is a **shipped, player-facing, ungated feature** — no console, no dev mode, no cheat
mode. Options → Game → **"DOOM Photo Mode [BETA]"**, reachable only from **Mission Select**, then
**`\`** in-game; must be re-enabled per level load.

- The camera **detaches and flies free with WASD**, away from the player.
- The **game keeps running** — `E` advances single frames, holding `E` runs at normal speed, and
  users report *"the demons will follow the cam in photomode."*
- **FOV is adjustable**; filters and lens effects exist; the on-screen GUI can be moved and hidden.
- **The player is invisible and has no character model at all** — reporting from the update's
  release states plainly that DOOM Guy has no third-person model.
- Restricted to **completed, non-Nightmare campaigns, in mission replay only** (an explicit
  anti-cheat decision), and camera control is refused during scripted animations and glory kills.

## Suggested dossier changes

1. **§6h — the elevated-camera result now has an explanation.** Culling follows the camera "for
   free" because id **built and shipped a detached camera**. That path was always designed to follow
   the camera rather than the player. Worth recording: it turns a piece of unexplained good luck
   into a designed-in engine property we can rely on.
2. **§9 — promote `pm_photoMode*` from "unexplored" to a live camera-decoupling lever.**
   `pm_photoModeMaxDist "5000"` is very likely the engine's own leash on how far the camera may
   travel from the player `[inferred-static]`. The proxy's `HOLD_MAX_DELTA` refuses jumps over
   **64 units**. The engine appears comfortable with roughly **eighty times** that. Not an argument
   for removing the clamp — an argument that a much larger safe envelope exists.
   `pm_photoModeFriction` is the shape of damping knob a comfortable VR camera wants.
3. **§13 — add two free observations to the next launch, which is already queued for the RVA
   re-measure.**
   - Enter Photo Mode, fly the camera, and check whether `getviewpos` and the twelve floats at
     `+0x360F6B0` **follow the photo camera rather than the player**. If they do, §6h's "it is the
     view, not the player body" is confirmed a second, independent way, with **no memory writes at
     all**.
   - Check whether **Photo Mode itself suppresses the HUD and the weapon**. That single observation
     discriminates between "our write breaks the HUD" and "the engine hides first-person elements
     whenever the view detaches" — two very different problems with two very different fixes. See
     the companion drop on the HUD.
4. **§10 — another instance of the scancode trap you recorded on 2026-09-01.** The activation key is
   documented as `\`, but a Spanish-keyboard user reports it arriving as **`ç`**. Same root cause as
   the console key: DOOM binds physical scancodes and the character reaching one is layout-dependent.
   Any automation opening Photo Mode must ask `MapVirtualKeyA` at the moment it needs the key.

## Caveats

Everything above is `[reported]`, from Steam Community threads and contemporary coverage, mostly
2016–2017, none of it on our `20240321` build and none of it tested by us. No source states the
actual distance limit, whether the camera can roll, or whether the weapon viewmodel is drawn — the
`5000` reading is ours, from a cvar name. The mission-replay restriction is a real constraint on
using Photo Mode as a development instrument: it cannot be entered from an arbitrary save.
