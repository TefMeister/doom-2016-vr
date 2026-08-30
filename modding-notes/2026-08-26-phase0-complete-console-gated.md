# 2026-08-26 — Phase 0 complete: the console is gated, but it handed us the camera

**Machine:** dev PC · **Live testing:** yes — the user drove the game and typed every console
command by hand. Companion to the same day's
[static pass](./2026-08-26-phase0-static-recon.md).

## What this session was for

The static pass had found a **dormant, inherited stereo-3D subsystem** in the binary —
`stereoRenderMode_t`, the `stereoRender_*` cvars, one of which mentions HMDs in the developers' own
help text. That produced a single sharp question worth answering before writing any code:

> Is that path still wired up, or is it vestigial?

The plan was to reach it from the developer console. That turned out not to be possible, for a
reason worth documenting properly.

## The answer: two gates, neither reachable

`~` opens the console and it works — `g_fov 110` was set and verified. But:

| measured | result |
|---|---|
| `listCvars` (bare) | **171 cvars.** id Tech 6 has thousands. |
| `listCmds` | **40 commands.** |
| `listCvars stereo` | **nothing.** |
| `com_production` | **not in the visible 171.** |
| `devMode_enable` | exists, reads `0` … |
| `devMode_fatalErrorOnEnter` | … but reads **`1` by default** |
| `BuildInfo` | **`Cheat Mode: OFF`** |

The startup log shows `idLib::SetProduction( PROD_PRODUCTION )`, and the binary describes the switch
in its own words: *"Used to enable and/or inhibit specific behaviour during production building mode.
**All demo and retail builds are built with this on.**"*

So there are **two independent gates** — production mode and cheat mode — and the master switch for
the first is itself gated. The stereo cvars aren't hidden; they're **never registered**.

`devMode_enable` looked like a way in until we read the cvar sitting next to it.
`devMode_fatalErrorOnEnter` means *"FatalError rather than enter Dev Mode"*, and it defaults to `1`.
We checked before flipping anything, so nothing was flipped and nothing crashed. **If anyone retries
this: set it to `0`, then read it straight back.** If it still reads `1` it's read-only or
shipping-disabled, and the next command takes the game down.

**Net result: the console is closed as a route to the stereo path.** That makes the injection route
not one option among several but the only door — which is worth knowing for certain, cheaply, before
committing weeks to a proxy built on a wrong assumption.

## The consolation prize is better than what we were chasing

`listCmds` turned up **`getviewpos`**, and it gave us the camera convention outright. Four readings,
deliberately shaped so translation and rotation could be separated:

```
X     Y        Z         pitch  yaw
1728  5440     6372.16   357.1  352.7
2135  5721.26  6331.63   357.2  352.8    <- walked; angles ~unchanged
2135  5721.26  6331.63   354.6  299.2    <- same spot; looked around
2135  5721.26  6331.63   350.8  14.2     <- same spot; looked around
```

- **Format `X Y Z pitch yaw`.**
- **Z is up** — walking moved X +407 and Y +281 but Z only −40.5, a sloping floor rather than a
  horizontal axis. Classic id/Quake convention, and consistent with what's recorded for id Tech 5.
- **Yaw is column 5** — it wraps through 360→0 (299.2 → 14.2).
- **Pitch is column 4** — steady near 357 (≈ −3°, a slightly downward gaze).
- **Roll isn't printed**; degrees, 0–360.

That's normally a session's work on its own, and it means the console is still useful — just as a
**ground-truth instrument** rather than a control surface. Any camera hypothesis the proxy produces
can be checked against `getviewpos` with no test code written. `com_showCameraPosition 1` gives the
same data continuously on screen.

Also newly visible and unexplored: **`pm_photoModeFriction` / `pm_photoModeMaxDist "5000"`** — the
game ships a **photo mode with a detached free camera** whose parameters are cvar-exposed *in
retail*. For a project whose whole problem is decoupling the camera, a native detached camera that
survived the gating is worth a proper look. Likewise `demo_nextPerspective` and
`spectator_localPerspective`.

And `exec` / `resourceExec` / `verifiedExec` are all registered, while the file-system search path
puts `Saved Games\id Software\DOOM\base\` **ahead of** the install directory — so a `.cfg` can be
executed from outside the game folder entirely. Whether an `exec`'d config can set cvars the
interactive console refuses is **untested**, and it's the one cheap probe left before writing code.

## Build identity, finally

The version resource says `1, 0, 0, 1` and is useless. `BuildInfo` says:

```
Version: 6.1.1     Target: shippingretail
Binary:  20240321-104810-ginger-fuchsia   (2024-03-21)
```

Internal codename **"Zion"**, confirmed twice: leaked source paths in the binary
(`l:\zion\code\shared\idlib\...`) and BuildInfo's own map-set list ("MP Orbis Zion Build",
"Zion Phoenix SP MP"). `jobs_numThreads` reads `6`, which fills in a threading detail for §5.

## Two corrections to yesterday's static write-up

**`God` is a registered command; `noclip` is not.** The static pass reported the exact opposite.

The cause is worth more than the correction: strings were extracted with **`llvm-strings -n 4`**, a
**4-character minimum**, which silently dropped every 3-character token — `God`, `rp`, and any
others. Every short-name conclusion from that sweep is unreliable and needs re-checking with a lower
threshold.

This is a **general trap, not a DOOM quirk** — it would bite any static pass on any engine whose
console commands have short names, which is most of them. It's been recorded in the dossier's dead
ends and is worth carrying up into the shared cross-engine library.

## Where Phase 0 lands

Complete. Renderer API, DRM state, injection foothold, threading, console access — and the camera
convention, which is really Phase 1 material arriving early.

**Next:** the cheap `exec`-a-cfg probe, then build the `opengl32.dll` proxy. One open question the
proxy will have to answer that the console couldn't: are gated cvars merely *hidden*, or never
*constructed*? If the latter, in-process registration won't resurrect them either and the stereo
path has to be driven by calling the render code directly.

Still nothing written to the game directory, and no mod code yet.
