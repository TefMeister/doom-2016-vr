# Phase 0 live console session — DOOM (2016), 2026-08-26 (dev PC)

The live half of Phase 0, run the same day as the
[static pass](../2026-08-26-phase0-static/). The user drove the game; every command below was
typed by hand at the in-game console and captured with the engine's own `conDump`.

Personal paths, the machine hostname, and id's internal build-requestor token have been redacted
(`<USER>`, `<STEAM>`, `<HOSTNAME>`, `<redacted>`). Nothing else was altered.

## Files

| file | what it is | why it matters |
|---|---|---|
| `startup-log-excerpt.txt` | first 40 lines of the console buffer from process start | Shows `idLib::SetProduction( PROD_PRODUCTION )` — the retail build boots into **production mode**. Also confirms the file-system search path puts `Saved Games\...\base\` **ahead of** the install dir. |
| `visible-cvars-production-mode.txt` | the complete output of bare `listCvars` | **171 cvars.** id Tech 6 has thousands, so this is the measure of how much production mode hides. Contains no stereo, camera, or debug-render cvars. |
| `registered-commands.txt` | the complete output of `listCmds` | **40 commands.** Includes `getviewpos`, `God`, `where`, `exec`, `bind`, `screenshot`, `demo_nextPerspective`, `spectator_localPerspective`. Notably **no `noclip`**. |
| `getviewpos-readings.txt` | four `getviewpos` readings | The camera-convention experiment — see below. |
| `buildinfo.txt` | output of `BuildInfo` | Version **6.1.1**, target **shippingretail**, and **`Cheat Mode: OFF`** — a second gate independent of production mode. Internal codename **Zion** appears throughout the map-set list. |

## The camera-convention experiment

Four `getviewpos` readings, deliberately shaped so translation and rotation could be separated —
the first two differ only by walking, the last three share an identical position and differ only
by looking around:

```
X     Y        Z         pitch  yaw
1728  5440     6372.16   357.1  352.7
2135  5721.26  6331.63   357.2  352.8    <- walked; angles ~unchanged
2135  5721.26  6331.63   354.6  299.2    <- same spot; looked around
2135  5721.26  6331.63   350.8  14.2     <- same spot; looked around
```

Conclusions:

- **Z is the up axis.** Walking moved X by +407 and Y by +281, but Z by only −40.5 — consistent
  with a sloping floor, not a horizontal axis. This is the classic id/Quake convention and matches
  what is already recorded for id Tech 5.
- **Column 5 is yaw** — it swings widely and **wraps through 360→0** (299.2 → 14.2).
- **Column 4 is pitch** — it stays near 357 (≈ −3°, a slightly downward gaze).
- **Roll is not printed**, presumably pinned at 0 for the player view.
- Angles are **degrees, 0–360**.

Format: `X Y Z pitch yaw`.

This gives the statically-discovered renderparms (`viewMatrixX/Y/Z/W`,
`globalViewOrigin/Fwd/Left/Up`) a known basis to be validated against later, and makes the console
a **ground-truth instrument** — any camera hypothesis can be checked against `getviewpos` without
writing test code.

## The headline negative

**`listCvars stereo` returned nothing.** The dormant stereo subsystem found in the static pass
(`stereoRenderMode_t`, the `stereoRender_*` cvars) is **not registered at runtime** in a retail
build. `com_production` — the master switch, described in-binary as *"All demo and retail builds
are built with this on"* — is not in the visible 171 either, so it cannot be flipped from the
console.

`devMode_enable` exists and reads `0`, but `devMode_fatalErrorOnEnter` reads `1` **by default**,
meaning an attempt to enter dev mode would FatalError rather than succeed. That was checked before
anything was flipped, and nothing was flipped.

**Net: two independent gates (production mode and cheat mode), neither reachable from the
console.** This closes the console as a route to the stereo path and makes the injection route the
only door — see `ENGINE-DOSSIER.md` §12.

## Method note / correction

The static pass extracted strings with `llvm-strings -n 4`, a **4-character minimum**, which
silently dropped every 3-character string. That produced one wrong conclusion in the earlier
write-up — `God` was reported absent from the binary when it is in fact a registered command (as
is `rp`). Any short-token conclusion from that static sweep should be re-checked with a lower
threshold. Recorded here because it is a reusable trap, not a one-off slip.
