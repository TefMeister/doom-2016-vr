# A public tool already defeats the production-mode console gate — and the unlocked command list contains `rp` and `setviewpos`

**Status:** 🆕 new · **Priority:** highest this project has had. This targets
`ENGINE-DOSSIER.md` §12's biggest open question verbatim — *"are gated cvars merely HIDDEN or never
CONSTRUCTED?"* — and §9's "❌ NOT available in retail" list, which the dossier itself calls
**"the single most important line in the dossier."**

## What was found

**`DOOMLegacyMod`** — originally by the modder **emoose**, updated in April 2024 by **brunoanc**
after a game patch broke it — is a public, actively-hosted mod whose entire purpose is to *"readd
all the hidden console commands & cvars in the game"* on **retail DOOM (2016)**, and, per its own
public description, **without needing to be in any kind of "developer mode."**

The numbers it reports are the decisive detail `[reported, /gr 2026-09-01]`:

| | commands | cvars |
|---|---|---|
| retail, as shipped | **39** | **170** |
| with the mod | **290** | **6592** |

Our own first-party live console session measured **40 commands / 171 cvars** on 2026-08-26
(`[verified-live 2026-08-26, n=1]`, dossier §4a). Those are the same two numbers to within one each
— almost certainly an off-by-one in how a header line of `listCmds` / `listCvars` output is counted
on one side or the other. **The tool is describing exactly the gate we measured**, which is strong
independent corroboration that both readings are of the same real thing.

**How it works, per its public description** `[reported]`: a **proxy `dinput8.dll`**, with
*"patching, restrictions removal and other modifications happening the moment the game is started,
before the Engine is even initialized."* It also **reimplements** a handful of commands that were
stripped rather than merely hidden — `noclip`, `infiniteHealth`, `noPlayerDeath`, `noPlayerKill`,
`noTarget`.

That timing detail independently matches our own §11 lesson: *"anything that must observe engine
initialisation has to hook from the earliest API call, not from the first frame."* Two parties
arrived at the same constraint on this game separately.

## The published command list — read directly, in full, this session

The repository ships **`doom_cmds.txt` (25 KB, 377 commands)** and **`doom_cvars.txt` (695 KB,
11,103 lines)** as plain text — a published enumeration of the unlocked interface, requiring no
download and no execution to read. `doom_cmds.txt` was fetched and read **in full** this pass,
verified by checking both ends of its alphabetical range (it begins at `aas_findArea` and ends at
`writeImage`).

Lines quoted verbatim, every one of them a name the dossier already cares about:

```
rp                               Displays or modifies a renderparm
renameRenderProg                 temporarily replace a renderProg with a different one
setviewpos                       sets the current view position
setplayerviewpos                 sets the current view positon for a given player
getviewpos                       prints the current view position
where                            prints the current view position
envshot                          takes an environment shot
testImage                        displays the given image centered on screen
demo_nextPerspective             goes to the next viewing perspective
spectator_localPerspective       goes to the perspective of the local player
```

Two of those change the shape of this project.

- **`rp <renderParmName> [value]` is real, and it is in the unlockable set.** Dossier §7 already
  calls this *"an outstanding zero-code verification tool"*; §9 lists it under "NOT available in
  retail". It is a **read/write window onto the engine's own named renderparms** — including
  `globalViewOrigin`, `globalViewFwd` / `Left` / `Up`, `viewMatrixX/Y/Z/W`,
  `projectionMatrixX/Y/Z/W`, and the override-shaped `explicitProjectionMatrix` / `explicitFov_x` /
  `explicitFov_y` family named in §6c. Everything §6h currently achieves by writing twelve floats
  into `DOOMx64vk.exe + 0x360F6B0` has a **typed, named, engine-sanctioned equivalent** here.
- **`setviewpos` exists.** The project has leaned on `getviewpos` as its ground-truth instrument
  since Phase 0. The *setter* was sitting in the gated set the whole time. An engine-native view
  teleport is both a control point and — more immediately — a way to **cross-check the `+0x360F6B0`
  finding**: call `setviewpos`, then read the twelve floats and see whether they follow.

## What this says about §12's open question

The dossier asks whether the gated cvars are *hidden* or *never constructed*, and correctly notes
that if they are never constructed, in-process registration will not resurrect them and the dormant
render code would have to be driven directly.

**The public evidence points hard at "hidden, and constructible."** 6,592 cvars and 290 commands are
far too many to be hand-authored by a modder; a published 695 KB dump of names *with their help
text* is what you get by enumerating structures the binary already contains, not by inventing them.
Combined with the mod's own claim that it works **without dev mode**, the most economical reading is
that the objects exist and that production mode suppresses their registration or their visibility,
not their construction.

`[reported, /gr 2026-09-01]` — and deliberately **not** upgraded past that tag. Nobody has tested
this on our build, and "a tool exists which says it does X" is not "X happened here."

## Honest caveats, stated plainly

- **It is closed-source.** The README says so directly: *"The source code isn't available,
  unfortunately."* So this is **prior art and a feasibility proof, not something to study
  line-by-line** — the same category as Vk3DVision. The repository also commits a `dinput8.dll.i64`
  **IDA database** beside the binary; that is someone else's reverse-engineering work and is not
  ours to mine.
- **No licence is stated** on the repository. Whether to *use* the tool is the user's call, not this
  session's — and using a tool is a different act from copying from one.
- **Build compatibility is unverified.** brunoanc's update targets *"the April 2024 Update."* Our
  copy reports binary `20240321-104810-ginger-fuchsia` (§1). Those are plausibly the same release —
  a March build stamp shipping in April is ordinary — but *plausibly* is not *verified*, and a patch
  that misses a build by one revision fails the way patches of hardcoded offsets always fail.
- **Two proxies, no filename collision.** The tool proxies `dinput8.dll`; ours proxies
  `vulkan-1.dll`. DOOM imports both (§11), so both can sit beside the exe. But **both hook early on
  purpose** — ours from `vkCreateInstance`, theirs explicitly *"before the Engine is even
  initialized"* — so if they are ever run together, run each alone first and establish what each
  does by itself.
- **The cvar list was NOT fully read, and the first attempt produced a false negative.** An
  automated fetch of the 695 KB `doom_cvars.txt` returned only the head of the alphabet and reported
  "no `stereoRender_*` found". **That negative is invalid** — and it is provable, because the same
  pass also failed to find `g_fov`, which we have verified live ourselves. Recorded here as a worked
  instance of the dossier's own standing rule: *before recording a negative as fact, confirm the
  test could have produced a positive one.*

## Concrete next steps

1. **The cheapest possible win, and it needs a human browser rather than a session:** open
   `doom_cvars.txt` on GitHub and Ctrl-F for **`stereoRender`**, **`multiView`**,
   **`com_production`**, and **`explicitProjection`**. Two minutes of looking either confirms or
   kills the dormant stereo path's reachability (§6a, §12) from a public source, before anything is
   installed or run.
2. If `stereoRender_*` is in that list, the ordering of this project's whole stereo strategy
   changes: driving the engine's own path moves back ahead of building per-eye projection ourselves.
3. Whether to install and run the tool on our copy is **the user's decision.** If it is taken, the
   first three things to try are `listCvars stereo`, `rp globalViewOrigin`, and `setviewpos` — in
   that order, because the first costs nothing, the second confirms the read/write window, and the
   third is the one that moves the camera.
4. Either way, `rp`, `renameRenderProg`, `setviewpos`, `envshot` and `testImage` should move out of
   §9's flat "not available" list into an "available *if* the gate is opened" row. They are now
   known to be real engine commands with real help text, not strings of uncertain status.

## Sources

- [DOOMLegacyMod — GitHub (brunoanc, updating emoose's original)](https://github.com/brunoanc/DOOMLegacyMod)
  — README, `doom_cmds.txt`, `doom_cvars.txt`, and the repository file listing
- [Console Command Cheats — Doom Nexus Mods](https://www.nexusmods.com/doom/mods/96) (403 to automated fetch; cited from search snippet only)
- [DoomLegacyMod v201901 — ModDB](https://www.moddb.com/games/doom-4/downloads/doomlegacymod-v201901) (403 to automated fetch; cited from search snippet only)
- [emoose — GitHub profile](https://github.com/emoose)
