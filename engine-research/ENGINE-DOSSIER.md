# Engine Dossier — DOOM (2016) (id Tech 6 engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** ✅ **PHASE 0 COMPLETE** (2026-08-26, dev PC) — static pass *and* live console session
both done. ·
**VR-readiness verdict:** **good, with the route now settled.** The engine ships a real inherited
stereo-3D render path and a fully-named renderparm database (§6) — but that path is **not reachable
from a retail console** (§4a), so the injection route is the only door. Camera convention is
already known (§6e). Next: build the `opengl32` proxy.

## 1. Identity
- Game / build / version: DOOM (2016), id Software, published by Bethesda Softworks. Steam release.
  Both shipped executables carry FileVersion `1, 0, 0, 1`, ProductName `DOOM` — useless. The **real**
  build identity comes from the console's own `BuildInfo` command:
  **Version `6.1.1`, Target `shippingretail`**, binary build `20240321-104810-ginger-fuchsia`
  (2024-03-21), disc layout `20240321-110110-rutherfordium-mousse`, candidate
  `20240321-110145-gentle-wolf`. `BuildInfo` also reports **`Cheat Mode: OFF`** (see §4a).
- **Internal codename: "Zion"** — confirmed twice over: leaked source paths in the binary
  (`l:\zion\code\shared\idlib\...`) and `BuildInfo`'s map-set list ("MP Orbis Zion Build",
  "Zion Phoenix SP MP").
- Platform & store; unofficial port? (extra fragility/legal notes): Steam (PC), app 379720.
  No unofficial-port concerns.
- Legitimacy: owned copy, installed at
  `D:\Program Files (x86)\Steam\steamapps\common\DOOM` (68.7 GB).

## 2. Engine lineage
- **id Tech 6**, id Software's successor to id Tech 5 (used in The Evil Within — our own
  `the-evil-within-vr-*` project; cross-reference that dossier). Lineage is **directly visible in
  the binary**: engine-level class names (`idRenderModel`, `idSWFEditText`, `idMapEntity`,
  `idPlayer*`, `idHands`, `idMenuWidget_*`) and the classic id cvar/console conventions are all
  present as plain strings.
- The stereo-3D subsystem (§6) is visibly **inherited from the id Tech 5 / Doom 3 BFG era** —
  cvar names and help strings match that generation's stereo support closely.
- Middleware confirmed from imports: **Bink 2** video (`bink2w64.dll`), **Steamworks**
  (`steam_api64.dll`), **DirectInput 8** + **XInput 1.4** for input, `superscriptx64.dll`
  (id's own "SuperScript" system — `idSuperScriptSystem` appears in the reflection table).
- Virtual texturing ("MegaTexture" successor) is present and heavily parameterised — `vmtr*`
  renderparms and `vt_*` cvars; the install has a top-level `virtualtextures\` directory.

## 3. Binary & memory
- **64-bit**, two separate executables, both standard MSVC-linked PE32+:
  | exe | size | renderer | evidence |
  |---|---|---|---|
  | `DOOMx64.exe` | 77.4 MB | **OpenGL** | imports `OPENGL32.dll`, no `vulkan-1.dll` |
  | `DOOMx64vk.exe` | 101.5 MB | **Vulkan** | imports `vulkan-1.dll`, no `OPENGL32.dll` |
- **The renderer is chosen at the executable level, not at runtime inside one process.** Each exe
  links only its own API. This is a much cleaner situation than a single dual-path binary: whichever
  we target, the other API is simply absent from the process.
- Sections (both exes): `.text .rdata .data .pdata .mydata .gfids .giats .tls _RDATA .rsrc .reloc`
  — completely ordinary MSVC output. `.gfids`/`.giats` = **Control Flow Guard is enabled** (relevant
  to any indirect-call hooking strategy). `.reloc` present ⇒ **ASLR on, module base will move**.
- Preferred image base `0x140000000`; `.text` ≈ 32 MB in both.
- Developer console / cvar system: **present and confirmed live.** Opens with `~`. `g_fov 110` was
  set and verified to take effect. **But it is heavily gated — see §4a.**

## 4. DRM / anti-debug & injection foothold
- **Denuvo is confirmed GONE on this build** — and this is now first-party evidence, not just the
  public prior from `-external-research`. A Denuvo-protected binary has packed/obfuscated sections
  and a stripped import table; both exes here show textbook-clean MSVC sections and a **full,
  readable import table with real API names**. Nothing is packed. Steam DRM (`steam_api64.dll`)
  remains, which is normal and not an obstacle.
- Launch-time-debugger behaviour: **not yet tested live.**
- **✅ INJECTION VECTOR THAT WORKS — `vulkan-1.dll` proxy, VERIFIED IN-GAME 2026-08-26.** Our M0
  proxy (`-staging/proxy-vulkan/`) loaded into `DOOMx64vk.exe`, resolved **246/246 exports with none
  missing**, observed instance/device/swapchain creation, and forwarded **4866 frames** of real
  gameplay with no crash and no visual artefact. Uninstall is deleting one file. **We are inside
  DOOM's Vulkan renderer.**

### 4a. Two runtime gates on the console (live-confirmed 2026-08-26) — the decisive Phase 0 result

The retail build boots into **production mode** (`idLib::SetProduction( PROD_PRODUCTION )`, visible
in the startup log) and reports **`Cheat Mode: OFF`**. These are **two independent gates**, and
together they close the console as a route to anything interesting:

| measured | result |
|---|---|
| `listCvars` (bare) | **171 cvars total.** id Tech 6 has thousands. |
| `listCmds` | **40 commands.** |
| `listCvars stereo` | **nothing** — the §6a stereo cvars are *not registered at runtime*. |
| `com_production` | **not in the visible 171** — the master switch cannot be flipped from the console. |
| `devMode_enable` | exists, reads `0` … |
| `devMode_fatalErrorOnEnter` | …but reads **`1` by default** — entering dev mode would **FatalError**. Not attempted. |
| `noclip` | **not a registered command.** `God` *is* (capital G) — presumably cheat-gated. |

The binary describes `com_production` in its own words: *"Used to enable and/or inhibit specific
behaviour during production building mode. **All demo and retail builds are built with this on.**"*
The engine also carries a `CVAR_SHIPPINGDISABLED` flag.

**Conclusion: the dormant stereo path is real but console-unreachable on retail.** The injection
route is not one option among several — it is the only door. Evidence:
`-dev-archive/recon/2026-08-26-phase0-live-console/`.

**Still worth trying later, cheaply:** `Saved Games\id Software\DOOM\base\` sits **ahead of** the
install directory in the file-system search path, and `exec` / `resourceExec` / `verifiedExec` are
all registered — so a `.cfg` dropped there can be executed without touching the game folder. Whether
an `exec`'d config can set gated cvars that the console rejects interactively is **untested** and is
the one remaining cheap probe before writing code.
- **Injection foothold — excellent, several options, all confirmed present in the import table:**
  - **`vulkan-1.dll` (VK exe only) — ⭐ THE RECOMMENDED TARGET (revised 2026-08-26).** The Vulkan
    build imports **~96 entry points statically and directly**, and **does *not* import
    `vkGetInstanceProcAddr`/`vkGetDeviceProcAddr`** — so a plain `vulkan-1` proxy intercepts **100%
    of Vulkan traffic** with no dispatch-table or proc-address funnel to chase. The imported set is
    exactly the VR surface: `vkQueuePresentKHR` (frame boundary), `vkCreateSwapchainKHR` /
    `vkGetSwapchainImagesKHR` (submission), `vkMapMemory` / `vkFlushMappedMemoryRanges` /
    `vkUpdateDescriptorSets` / `vkCmdBindDescriptorSets` (**uniform delivery — the §7 question**),
    `vkCmdSetViewport` (per-eye), `vkCmdDrawIndexed`, `vkCreateShaderModule`. Full analysis:
    `-dev-archive/recon/2026-08-26-injection-surface/`.
  - **`OPENGL32.dll` (GL exe only) — ⚠️ EARLIER LEAN, NOW DEMOTED.** The claim that this was "the
    single cleanest foothold" was **wrong on two counts**, corrected here: (a) only **42** functions
    are imported and they are all **legacy GL 1.x + WGL** — every modern GL 4.x call is resolved
    through **`wglGetProcAddress`**, so the real surface is hundreds of functions behind a funnel we
    would have to build; (b) **`wglSwapBuffers` is NOT imported at all** — the frame boundary is
    **`gdi32!SwapBuffers`**, so an `opengl32` proxy never sees end-of-frame without a second hook
    into GDI32 or an IAT patch. Still viable as a fallback; no longer the default choice.
  - **`winmm.dll`** — imported by *both* exes; the proven `the-evil-within-vr-*` vector, and
    renderer-agnostic.
  - Also imported and usable as fallbacks: `dinput8.dll`, `dbghelp.dll`, `wsock32.dll`,
    `msimg32.dll`.

## 5. Threading & frame structure
- **`jobs_numThreads` reads `6`** on this machine (4 physical / 8 logical cores) — the job system
  sizes its worker pool from the CPU. `jobs_drawDebugGUI` exists but is a no-op without dev mode.
- Not yet mapped live. Known from public developer material (SIGGRAPH 2016, see `-external-research`):
  id Tech 6 is a genuinely job-based multithreaded engine whose job system had known scheduling
  "bubbles" later rewritten for id Tech 7 — **do not assume even frame-to-frame CPU scheduling**
  when choosing a hook point.
- One-frame walkthrough: TBD (Phase 2).

## 6. Camera & projection delivery (the crucial section)

**This section went from empty to substantially answered in one static pass, because the binary
ships its own names.**

### 6a. The engine has a built-in stereo-3D render path
Present in **both** executables (so it is engine-level, not renderer-specific):

- Enum `stereoRenderMode_t` with values `STEREO_RENDER_OFF`, `STEREO_RENDER_LEFT_AND_RIGHT`,
  `STEREO_RENDER_TOP_AND_BOTTOM`, plus `STEREO_MODE_WIDTH` / `STEREO_MODE_HEIGHT`.
- A mode value-name list: `topBottomStereo`, `leftRightStereo`, `HDMI3D`, `HDMI3DtwoPlayer`.
- Live cvars, with the engine's own help text:
  | cvar | engine's own description |
  |---|---|
  | `stereoRender_separation` | "world units from center to eyes" |
  | `stereoRender_screenSeparation` | "screen units from center to eyes" |
  | `stereoRender_guiOffset` | **"shift guis so they don't appear at infinity in HMDs"** |
  | `stereoRender_swapEyes` | "swap target buffers for left and right eyes" |
  | `multiView_60Hz` | "0 = alternate frame rendering, 1 = render both each frame" |
- Engine doc-comments confirming the view model: *"There is normally just one \[world view], but
  there will be two unique ones in split-screen multiplayer and two identical ones in stereo-3D
  (both centered between the eyes)"*, and *"for stereo 3D, the guis can be offset differently in
  each screenView"*, and a note that scanout width/height *"can be larger than GetWidth() /
  GetHeight() when in stereo 3D modes"*.

**⚠️ SUPERSEDED 2026-09-01 — this passage was wrong, and the correction matters more than the
original claim.** It read: *the doc-comment says the two stereo world views are "identical and
centered between the eyes", so eye separation is applied downstream of view setup (a projection
skew), not by building two different view matrices — our per-eye override probably belongs at the
projection stage.*

**id's own published source says the view ORIGIN is moved per eye** `[reported 2026-09-01, from id's own
published GPL source, via /gr]`. `neo/renderer/RenderWorld.h` in id Software's GPL
release of Doom 3 BFG declares `renderView_t` with the comment
`idVec3 vieworg;  // has already been adjusted for stereo world seperation`, alongside a
*separate* `float stereoScreenSeparation;  // projection matrix horizontal offset`. Two distinct
steps — which is exactly why the engine ships **two** separately-named cvars:

| cvar | engine's own help text | what BFG's source shows it doing |
|---|---|---|
| `stereoRender_separation` | "world units from center to eyes" | **moves `vieworg`** — a real per-eye world-space camera translation |
| `stereoRender_screenSeparation` | "screen units from center to eyes" | shifts the projection matrix horizontally (convergence) |

Also worth knowing: `int viewEyeBuffer;  // -1 = left eye, 1 = right eye, 0 = monoscopic view or GUI`
— a one-integer eye selector with the GUI as a first-class member of the same enum.

**Why this changes the plan:** §6h's control point writes exactly `globalViewOrigin` + basis. Under
this reading that is **not a workaround for a missing stereo path — it is the same lever the
engine's own stereo code pulls**, reached from another direction. A per-eye IPD offset along the
basis's `left` vector is the operation the engine performs on itself. **Confirmed live the same
day** — see §6h's stereo-pair result.

**Both readings kept, both tagged:** DOOM 2016's own compiled-in comment is `[inferred-static,
2026-08-26]` (id Tech 6 text about id Tech 6); BFG's `renderView_t` is `[reported 2026-09-01,
from id's own published GPL source]` (one generation earlier). Possible reconciliations, none
established: the id Tech 6 comment may describe the view list *as constructed*, before per-eye
adjustment; it may be stale commentary carried forward; id Tech 6 may have simplified; or
"identical" may mean "of the same scene" rather than "of the same camera".

**The method lesson, sharpened rather than discarded:** a compiled-in doc-comment is primary-source
engine documentation and is cheap to read — *and it can be stale, generation-shifted, or narrower in
scope than it looks.* Where an engine family has a **published** ancestor, check the ancestor's
source before building a plan on the descendant's comment.

**The engine explicitly names HMDs in its own cvar help.** But **there is no stereo *mode* cvar to
find** `[measured 2026-09-01]`. The full retail cvar list was read: all four `stereoRender_*`
parameters are present, `multiView_60Hz` and `com_production` are present, and **nothing selects
`stereoRenderMode_t`**. An earlier version of this section said the name "was not resolvable
statically — find it live via `listCvars`"; that advice pointed at nothing and is **withdrawn**
`[disproved 2026-09-01]`. It is recorded rather than deleted because it would otherwise have cost a
future live session.

**What the switch is instead — a call argument, not a mode.** id's published GPL source for the
previous generation threads the eye through the render call rather than reading a mode global at
draw time:

```c
void RB_DrawView( const void *data, const int stereoEye );   // 0 = mono, -1 / +1 = eyes
```

Downstream it does what our cvar names imply: the per-eye GUI shift is
`guiScreenOffset = stereoEye * viewDef->renderView.stereoScreenSeparation`, and `renderView_t`
carries **`viewEyeBuffer`** as first-class state (`-1` left, `+1` right, `0` for a mono view *or* a
GUI). `stereoRender_swapEyes` is consulted only when comparing a shader's eye to the current one
— a late cosmetic flip, not the switch.

`[reported 2026-09-01, from id's own published GPL source]` for **id Tech 4/5**; **`[hypothesis]` for
id Tech 6** — one generation and several years separate them. What lifts it above a guess is
that it *explains our own cvar inventory*: every stereo parameter live as a cvar while no mode cvar
exists is exactly what a call-site argument looks like. Nothing was stripped; the switch was never a
cvar in this generation.

**So the shape to hunt is a function taking a small signed eye argument, called twice per frame,
plus an eye field on the view object — not a global to flip.** See §6d for the static search.

**⚠️ Consequence for the console gate:** opening it would hand us the stereo *parameters*,
**not the on-switch**. §11 and §13 should not be read as "open the gate and stereo
unblocks". Source:
`external-research/topics/2026-09-01-there-is-no-stereo-mode-cvar-so-what-turns-it-on.md`.

### 6b. The full renderparm table is named in the binary
id Tech 6 exposes shader constants as named "renderparms", and the complete name table is a plain
string block. The camera-relevant entries, in binary order:

```
viewMatrixX/Y/Z/W                  inverseViewMatrixX/Y/Z/W
modelMatrixX/Y/Z/W                 inverseModelMatrixX/Y/Z/W
                                   inverseMVPMatrixX/Y/Z/W
projectionMatrixX/Y/Z/W            inverseProjectionMatrixX/Y/Z/W
mvpMatrixX/Y/Z/W                   mvpMatrixDeterminantSign
mvpMatrixNoJitterX/Y/Z/W           mvpMatrixLastX/Y/Z/W
viewProjectionMatrixX/Y/Z/W
globalViewOrigin  globalViewFwd  globalViewLeft  globalViewUp
lastFrameViewMatrix  lastFrameProjectionMatrix
lastFrameWorldSpaceInverseMVPMatrix
mvpIsIdentity  mvpIsOrthographic  mvpIsAutoMap  mvpIsWorldGui  mvpIsSunFlare
```

Matrices are delivered **as four separate row/column vec4 renderparms** (`…X/Y/Z/W`), not as one
opaque blob. `mvpMatrixNoJitter*` + `mvpMatrixLast*` confirm **TAA with jittered projection** and
motion-vector reprojection — both are known VR hazards and will need handling later.

### 6c. Candidate override levers already named by the engine
These are field names from the reflection table (§6d) and are the most promising leads:
- **`explicitProjectionMatrix`** — an explicit, settable projection override on a view.
- **`explicitFov_x` / `explicitFov_y`** — explicit per-axis FOV override.
- **`forceIdentityViewMatrix`** — forces the view matrix to identity.
- `mapViewMatrix`, `mapViewToPlayerViewMatrix`, `camFov` / `cameraFOV`, `blendFOV`.

If `explicitProjectionMatrix` / `explicitFov_x/y` are genuinely honoured on the main world view,
**the per-eye projection override may be a supported engine input rather than something we have to
patch in** — which would be a categorically easier project than the manual camera-matrix hunt this
dossier originally assumed. **Unverified. This is the single highest-value thing to test live.**

### 6d. The binary ships a reflection database with doc comments
Large string blocks contain fully-qualified C++ class/enum/field names *with the developers' own
human-written descriptions* (e.g. `idPlayerMechanicRailRide::enum_1259`,
`idHands::HANDSACTION_VIRTUAL_GUI_ROTATE_UP`, `CAM_FOCUS_PLAYER`, `VIEW_MOTION_ACTION_*`,
`idList < idMapEntity *, TAG_IDLIST, false >`). This is effectively a built-in symbol source — the
same structural advantage REFramework provides on RE Engine, except it is native to the binary.
Mining this table properly is its own high-value task (see §12).

**Concrete first query, handed over by §6a:** search the table for an **eye-buffer field on the
view object**. BFG's is `viewEyeBuffer` on `renderView_t`, and id names things consistently across
generations. A named field on the view struct would be a far better switch than any cvar — and
unlike the cvar hunt this is a **static** search needing no launch. `[hypothesis]`, but cheap and
available right now.

### 6e. Camera convention — MEASURED LIVE (2026-08-26)

The console command **`getviewpos`** prints the live camera. Four readings were taken, shaped so
translation and rotation could be separated (first two differ only by walking; last three share an
identical position and differ only by looking around):

```
X     Y        Z         pitch  yaw
1728  5440     6372.16   357.1  352.7
2135  5721.26  6331.63   357.2  352.8    <- walked; angles ~unchanged
2135  5721.26  6331.63   354.6  299.2    <- same spot; looked around
2135  5721.26  6331.63   350.8  14.2     <- same spot; looked around
```

- **Format: `X Y Z pitch yaw`.**
- **Z is up.** Walking moved X +407 and Y +281 but Z only −40.5 (a sloping floor). Classic id/Quake
  convention — and consistent with what is recorded for id Tech 5.
- **Yaw is column 5** — swings widely and wraps through 360→0 (299.2 → 14.2).
- **Pitch is column 4** — stayed near 357 (≈ −3°, a slightly downward gaze).
- **Roll is not printed**, presumably pinned at 0 for the player view.
- Angles are **degrees, 0–360**. Units are id units (uncalibrated to metres; map coordinates run to
  the thousands).

**Why this matters:** it gives §6b's `viewMatrixX/Y/Z/W` and `globalViewOrigin/Fwd/Left/Up` a known
basis to be validated against, and it makes the console a **ground-truth instrument** — any camera
hypothesis can be checked against `getviewpos` with no test code written. `com_showCameraPosition 1`
(*"Shows the camera's position and rotation"*) gives the same data continuously on screen.

- Exact constant-buffer slot / byte offsets / row-major convention: **TBD** — needs live shader
  reflection or a GL/VK capture (Phase 2). Handedness/up-axis now known (above).
- The per-eye override maths (`K_eye = …`): **TBD**, pending 6c.

> ⚠️ **6e ORDER CORRECTED 2026-08-31 `[verified-live, derived from the matrix]`: `getviewpos`
> prints **yaw then pitch**, not pitch then yaw. A reading of `... 34.3 3.4` corresponds to a
> rotation about **Z of 34.3 deg** (`cos=0.826`, `sin=0.563`, exactly the row-0/row-1 values) and a
> tilt of `asin(0.060)=3.44 deg`. **Column 4 = yaw, column 5 = pitch.** A swapped pitch/yaw produces
> a plausible-looking but wrong camera, so this matters before any head-tracking work.

## 6f. 🎯 THE CAMERA TRANSFORM — FOUND AND CONFIRMED (2026-08-31)

`[verified-live 2026-08-31, n=2 independent positions]` Located by **value search**, not by
address, and confirmed against the game's own `getviewpos` twice.

```
 0.825  -0.563   0.049   2731.799
 0.562   0.826   0.034   6212.317
-0.060   0.000   0.998   6355.658
```

- **Column 3 = world position**, matching `getviewpos` exactly.
- 3x3 is a true orthonormal basis (row 0: `0.825^2+0.563^2+0.049^2 = 1.0000`).
- Row 2 ~ `(0,0,1)` — **Z-up confirmed independently** of the static reading.
- **Region 2**, the high-flush per-frame uniform buffer (24806 -> 29331 flushes across one session).
- **Replicated per draw** — a search caps at 64 hits, all in region 2; every draw's uniform block
  carries a copy. That is an *advantage* for stereo, since each eye needs its own view.
- Also present: the position as a packed **`vec4` with `w=1.0`** — that is **`globalViewOrigin`**,
  one of the renderparms the binary names.

**Method that worked, after the address-based hunt failed:** drive the console -> `getviewpos` ->
screenshot the numbers -> search memory for those floats -> **move, re-read, search again**. Two
matching positions is what makes it a finding rather than a coincidence.

**Controlling it is a different problem.** The transform is rewritten every frame across 64+ blocks,
so poking an address does nothing. Control belongs at the **write path**: the buffer is
`HOST_VISIBLE` and CPU-written (no `vkCmdPushConstants`/`vkCmdUpdateBuffer` imported), so hook
**`vkFlushMappedMemoryRanges`** — already hooked for the flush counter — and rewrite the transform in
the flushed range before it reaches the GPU.

## 6g. 🚨 The camera buffer is HOST_COHERENT — the flush path is NOT its update route

`[measured 2026-08-31]` With the tracker locked on a verified position, the flush-path intercept
reported the camera present in **ZERO flushed ranges**, and only **7 flushes in ~10 s of gameplay**
against 24,155 accumulated mostly during level load. **Under one flush per second at 60 fps** means
no flush is needed for the GPU to see writes: the memory is **`HOST_COHERENT`**, and
`vkFlushMappedMemoryRanges` never carries the camera. The flushes we do see belong to other,
non-coherent buffers.

**Consequence:** `vkFlushMappedMemoryRanges` is the wrong interception point for anything
per-frame here, despite being the obvious one. **`vkQueueSubmit` is the real gate** — by then the
game has written the frame's camera and the GPU has not read it yet.

**Cost constraint that shapes any solution:** reading this memory measures **~42 ms per MB**
(write-combined), so scanning per frame is impossible. Learn the copies' **offsets once**, then
revisit only those each submit — a few hundred 64-byte reads. Always re-verify the translation
still matches before writing, since a ring slot may have been reused.

## 6h. 🎯 THE UPSTREAM SOURCE — one static global holds origin + basis (2026-09-01)

`[verified-live 2026-09-01, n=1 process instance]` The per-draw GPU copies in §6f are downstream
replicas. The **authoritative** value sits in the executable's own static data:

**`DOOMx64vk.exe + 0x360F6B0`** — absolute `0x00007FF75092F6B0` at module base `0x7FF74D320000`,
region type **image**, not heap.

Twelve contiguous floats, dumped with the player standing at `getviewpos` = `799.93 4673.61 6407.39
219.3 7.4`:

```
+0    799.926  4673.610  6407.388      <- origin      (globalViewOrigin)
+3     -0.767    -0.629    -0.129      <- forward     (globalViewFwd)
+6      0.634    -0.773     0.000      <- left        (globalViewLeft)
+9     -0.099    -0.082     0.992      <- up          (globalViewUp)
+12     0.000     0.000     0.000
```

Every row is unit length and mutually perpendicular to within 5e-4, and the basis reproduces the
console's own yaw/pitch arithmetically: `cos(7.4°)·cos(219.3°) = -0.767` = forward.x,
`cos(7.4°)·sin(219.3°) = -0.628` = forward.y, `sin(7.4°) = 0.129` = forward.z; left =
`(sin, -cos)(219.3°)` exactly, roll zero. The layout is the renderparm quartet the binary names
`[measured 2026-09-01]`; the naming itself is `[inferred-static]`.

**It is the view, not the player body.** The stored basis carries **pitch** (7.4° of it). The player
body does not pitch in this game; the view does. That settles run 12's open question, which the
HUD-and-weapon-vanishing-together symptom had left ambiguous.

**Writing it works, and the control proves the write itself is inert.** Holding the address at the
value it **already holds** changes nothing — HUD, crosshair and weapon all stay. Holding it displaced
moves the view and drops the HUD, crosshair and weapon. So the HUD loss is caused by *displacement*,
not by writing into engine memory.

**⭐ The elevated-camera test passes.** Lifting the origin **+60 units on Z** renders the world
correctly from a position the player is not at — geometry, lighting and the cave ceiling all resolve,
**no culling collapse and no black void**. Culling follows the camera here for free, which is exactly
what Psychonauts spent weeks failing to get (§1 of that project's board).

**What is NOT established:**
- **RVA stability across restarts is `[inferred-static]`, not verified** — it follows from the image
  region but has been seen in one process instance. **Re-measure on the next launch.** If it holds,
  this project never needs the value hunt again.
- Whether writing the **basis** (a rotation) behaves as well as writing the origin. `phold` writes
  three floats; a yaw needs `forward` and `left` rotated together — a small code change.
- Why the HUD and weapon drop out under displacement at all. A VR camera that costs the HUD is not
  finished.

**Practical limit:** `HOLD_MAX_DELTA` clamps a single jump to **64 units**; a 150-unit jump is
refused. Larger displacements must be walked up in steps.

### 6h-2. Second session, same day: confirmed at n=2, and STEREO CONFIRMED LIVE (2026-09-01, afternoon)

**The address survived a restart** `[verified-live 2026-09-01, n=2 process instances]`. On a fresh
launch, fresh level load, the basis was **predicted arithmetically from `getviewpos` before the dump
was read**, and matched exactly:

```
getviewpos  1731.42 5441.92 6371.72  yaw 30.0  pitch -0.0
+0   1731.418  5441.916  6371.721      <- origin   (matches)
+3      0.866     0.500     0.000      <- forward  (predicted 0.866 0.500 0.000)
+6     -0.500     0.866     0.000      <- left     (predicted -0.500 0.866 0.000)
+9      0.000     0.000     1.000      <- up       (exactly Z-up at pitch 0)
```

**⚠️ Caveat that keeps this short of "RVA is stable":** the module loaded at the **same base**
(`0x7FF74D320000`) both times, so this confirms reproducibility across a restart but **does not test
ASLR rebasing**. Windows randomises image base per boot, so the rebase test needs a **reboot**, not a
relaunch. Until then, resolve the address as `GetModuleHandle(NULL) + 0x360F6B0` rather than
hardcoding the absolute value — correct either way, and free.

**⭐ STEREO WORKS FROM THIS ADDRESS** `[verified-live 2026-09-01, n=1 pair]`. Holding the origin at
`origin ± 32·left` produced a correct **stereo pair**: same scene from two laterally-offset
viewpoints, **depth-correct parallax** (a nearby crate swings hugely between frames while distant
towers barely move), both frames rendering cleanly. This is the operation §6a says
`stereoRender_separation` performs on `vieworg`. **Per-eye rendering does not require reviving the
dormant stereo path.** Caveat: these were two *sequential* frames, not two eyes within one frame —
the geometric primitive is proven, the per-frame delivery is not.

**Rotation needs the whole basis, and partial writes shear** `[verified-live 2026-09-01, n=1]`.
Holding **only** `forward` rotated 20° about Z (leaving `left`/`up` alone) produced a badly sheared,
washed-out image with the HUD displaced rather than a clean turn. Proof the vector is consumed by the
renderer, but a coherent rotation must write `forward` and `left` together — which is why
`pholdyaw <addr> <deg>` was added the same day (rotates the engine's live basis each frame about Z,
origin untouched, with a runaway guard).

**❌ `setviewpos` is NOT registered on retail** `[verified-live 2026-09-01, n=1]` — `Unknown command
'setviewpos'`. It exists in the engine (it is in `DOOMLegacyMod`'s published 377-command list, §9),
but the proposed "free cross-check of §6h via `setviewpos`" is **not free on retail**; it needs the
console gate opened first.

**Why the elevated-camera test worked at all — it is a designed path, not luck** `[reported,
2026-09-01, via /gr]`. DOOM 2016 ships **Photo Mode**: a player-facing, ungated, detached free camera
(Options → Game → "DOOM Photo Mode [BETA]", from Mission Select, then `` ` ``). The camera flies free
with WASD while the game keeps running, and **the player is invisible with no third-person model**.
So the engine was built to render correctly from a camera that is not the player's. Note
`pm_photoModeMaxDist "5000"` — very likely the engine's own leash `[inferred-static]`, roughly
**eighty times** our 64-unit `HOLD_MAX_DELTA`. Not an argument for removing the clamp; an argument
that a far larger safe envelope exists.

**The HUD loss is NOT a culling effect** `[reported, 2026-09-01, via /gr]` — ruled out by a
frame-by-frame graphics study: the UI is drawn to **its own render target** and composited **last**,
so a screen-space overlay cannot be culled by moving the world camera. (The *weapon* is the ordinary
case — it is in the world depth pre-pass, so a displaced camera plausibly puts it out of frame.)
Leading hypothesis `[hypothesis]`: the HUD loss is a **game-state response** — either the engine has
a first-class "the view is not the player's" state that suppresses first-person elements (which is
precisely what Photo Mode does), or the address is read by **game code as well as the renderer**,
which the image-region location makes plausible and which would make it more powerful *and more
dangerous* than §6h claims. **Cheapest test, no code: enter Photo Mode and see whether the HUD and
weapon disappear the same way.**

**✅ CONFIRMED BY THE USER IN-GAME (2026-09-01) — Photo Mode removes the weapon and HUD altogether**
`[verified-live 2026-09-01, n=1, user-observed]`. That closes the question. The HUD/weapon loss under
our displacement is **not damage we cause** — it is **the engine's own designed behaviour whenever
the view stops being the player's**. Hypothesis (1) above is upheld; hypothesis (2) (game code reads
the address) is neither needed nor excluded.

**What that changes:**
- **Nothing is broken, so there is nothing to repair.** "Fix the HUD" was the wrong framing — the
  right one is "choose which of the engine's two behaviours we want".
- **But it is a real constraint for VR, not a curiosity.** A VR build wants a (VR-adapted) HUD *and*
  a displaced camera, and §6h's global gives you the second only by triggering the first. The global
  is therefore the right lever for a **photo-mode-like detached camera** and the wrong one for
  **stereo**, where only the picture should move.

**If it is state, §6f and §6h are a division of labour, not rivals:** write §6h's global when the
engine *should* know the camera moved; write §6f's per-draw GPU copies when **only the picture**
should move — and "only the picture moves, and differently per eye" is exactly the stereo
requirement.

### 6h-3. ROTATION WORKS — the camera transform is complete (2026-09-01, late)

`[verified-live 2026-09-01, n=1 at 20° and 90°]` `pholdyaw <addr> <deg>` writes the basis
coherently — `forward` and `left` rotated together about Z, origin untouched — and produces a
**proper camera turn**: correct geometry, lighting and perspective, **no shear, no culling collapse,
no void**, at both 20° and 90°. Release restores the engine's own basis exactly.

The contrast with §6h-2's forward-only write is the whole point: **same address, same kind of write,
and the only difference is whether the basis stays orthonormal.** Partial writes shear; coherent
writes turn the camera.

**⭐ With this, every component of the view transform is known writable and renders correctly:**

| component | status |
|---|---|
| position — translate the camera anywhere | ✅ §6h |
| per-eye offset along `left` — i.e. **stereo** | ✅ §6h-2 |
| orientation — turn the camera | ✅ **§6h-3** |
| fully reversible, engine's values restored | ✅ every test |

That is the entire camera side of a VR mod, from **one static address**, with no engine cooperation
and the dormant stereo path (§6a) untouched.

**🔎 The HUD responds DIFFERENTLY to rotation than to translation** — a distinct result from
§6h-2's, and a useful one:

- **Translating** the origin removes HUD, crosshair and weapon **entirely** (Photo Mode confirms this
  is designed behaviour when the view stops being the player's).
- **Rotating** the basis **keeps them drawn but displaces them** — at 20° the crosshair and health
  bar slide across the frame; by 90° they have left it.

So the two operations trip different engine responses, and under rotation the first-person layer is
still being drawn, merely anchored to a view that no longer matches. `[hypothesis]` The HUD's
placement derives from this same basis, which suggests a VR build might keep its HUD by rotating
what the **renderer** reads while leaving what the **HUD** reads alone — the §6f / §6h division of
labour again, now with a concrete lever.

**Also this session:** the address held a **third** time `[verified-live 2026-09-01, n=3 process
instances]`, basis again predicted from `getviewpos` before dumping. Load base was **the same
again**, so ASLR rebasing remains untested — it needs a **reboot**, not a relaunch. And **`scan 0x29`
works in-game**: the console opens and types cleanly with no virtual key anywhere in the path, so
§10's layout-dependence is now routed around rather than worked around.

Evidence: `dev-archive/recon/2026-09-01-rotation-completes-the-transform/`.

## 7. Constant-buffer fill mechanism
- TBD (Phase 2). Note the renderparm indirection: shaders consume *named renderparms*, so there is
  an engine-side table mapping renderparm → uniform/UBO/push-constant location. Finding that table
  is likely more productive than chasing raw buffer writes.
- The console command **`rp <renderParmName> [value]`** ("Displays or modifies a renderparm") is a
  built-in read/write window onto this system — an outstanding zero-code verification tool. A
  sibling command `renameRenderProg <renderProg> [newProg]` swaps shader programs live.

## 8. Pass inventory (by render target)
- **✅ SWAPCHAIN MEASURED IN-GAME (2026-08-26, via our own proxy):**
  `vkCreateSwapchainKHR -> VK_SUCCESS, 1280x720, format=44, minImageCount=2`, and
  `vkGetSwapchainImagesKHR -> imageCount=2`. Format **44 = `VK_FORMAT_B8G8R8A8_UNORM`**;
  **double-buffered**. Dimensions match `r_windowWidth`/`r_windowHeight`, so the swapchain follows
  the window, not a fixed internal resolution. This is the surface a VR submission path will have to
  either read from or replace.
- Rest TBD (Phase 2). Public head start: the renderer is a **hybrid clustered-forward + deferred**
  design with only **~100 unique shaders total** (SIGGRAPH 2016, per `-external-research`), and
  Adrian Courrèges' "DOOM (2016) — Graphics Study" is a frame-by-frame reference to read when this
  phase opens.
- Confirmed present from renderparms: virtual texturing (`vmtr*`), env probes
  (`envProbesMapArray`), an atlas-based light system (`lightsAtlasMap`, `channelLight0..8`),
  decals, SSS (`sssMap`), bloom, radial blur, PBR debug modes.

## 9. cvar / console cheat sheet
Console opens with `~`. **Verified live 2026-08-26.** Full captured lists in
`-dev-archive/recon/2026-08-26-phase0-live-console/`.

### ✅ Actually available in retail (of 171 cvars / 40 commands)

| command / cvar | effect | use |
|---|---|---|
| `getviewpos` | prints `X Y Z pitch yaw` | **the camera ground-truth instrument** — see §6e |
| `com_showCameraPosition 1` | *"Shows the camera's position and rotation"* | same data, continuous, on screen |
| `where` | position readout | second opinion on the above |
| `listCvars [str]` / `listCmds [str]` | enumerate | takes an optional search string; `^`/`$` anchor |
| `conDump <file>` | dump console buffer to file | **how every capture here was made** |
| `g_fov <n>` | field of view | verified working (`g_fov 110` took effect) |
| `BuildInfo` | build identity + `Cheat Mode` state | see §1, §4a |
| `exec` / `resourceExec` / `verifiedExec` | run a `.cfg` | scripting foothold — see §4a and §10 |
| `bind` / `unbind` / `listBinds` | key binding | makes live testing tolerable |
| `screenshot` | capture | evidence |
| `writeConfig <file>` | dump current config | snapshot before/after changes |
| `vid_restart`, `vt_restart` | reinit video / virtual texturing | may be needed after render changes |
| `demo_nextPerspective`, `spectator_localPerspective` | perspective switching | **unexplored — worth a look** |
| `God` | god mode (capital G) | test survivability during camera work |
| `com_skipGameRenderView` | *"skip generating the GUIs"* | possible HUD-suppression lever |
| `menu_advanced_AllowAllSettings 1` | *"allow all settings to be picked for testing purposes"* | set; effect not yet examined |
| `pm_photoModeFriction`, `pm_photoModeMaxDist` | photo-mode camera tuning | **a native detached camera exists** — unexplored |
| `com_capturePath`, `com_captureTGA`, `com_captureSamples` | frame capture | harness plumbing |
| `r_renderAPI` | *"Graphics API to use. 0 = OGL, 1 = Vulkan"* | ⚠️ **does NOT choose the executable** — see §11. Setting it to `1` while Steam launches the GL exe **breaks the launch.** |
| `jobs_numThreads` | reads `6` here | §5 |

### ❌ NOT available in retail (present in the binary, never registered)

`stereoRender_separation` · `stereoRender_screenSeparation` · `stereoRender_guiOffset` ·
`stereoRender_swapEyes` · `multiView_60Hz` · `com_production` · `noclip` ·
`rp <name> [value]` · `renameRenderProg` · `envshot` · `testImage` · `r_pbrDebug*` ·
`com_showfps` (the visible one is `com_showFPS`, capital FPS)

**This is the single most important line in the dossier:** everything in §6a and §7 that looked like
a free zero-code lever is gated off by production mode. See §4a.

### Corrections to the earlier static-only pass
- **`God` IS a registered command** (capital G). The earlier entry said it wasn't in the binary and
  that `noclip` was — **exactly backwards at runtime**. Cause: `llvm-strings -n 4` has a
  **4-character minimum** and silently dropped every 3-character string (`God`, `rp`, …). Re-run any
  short-token question with a lower threshold. See §11.
- **`noclip` is NOT registered**, despite appearing in the binary — presumably cheat-gated.

## 10. Autonomous harness recipe (this game)

- **⚠️ DRIVING THE CONSOLE: the toggle key is layout-dependent AND it is a dead key
  `[measured 2026-09-01]`.** Two separate traps, either of which makes a working input backend look
  broken.

  **(a) Which key.** On this machine (layout `0x0425`):

  | VK | scancode | |
  |---|---|---|
  | `VK_OEM_3` (0xC0) | 0x1A | what the proxy's `console` command sends — **the wrong key** |
  | `VK_OEM_8` (0xDF) | **unmapped** | what the 2026-08-31 note recorded — sends nothing at all |
  | `VK_OEM_7` (0xDE) | **0x29** | the key DOOM's console is actually on, here |

  **⚠️ CORRECTED LATER THE SAME DAY — both readings are right, and the LAYOUT is what moved.** A
  relaunch a few hours later reported layout **`0x08090809`**, under which scancode `0x29` is reached
  by **`VK_OEM_8` (0xDF)** — exactly what the 2026-08-31 note recorded — while `VK_OEM_3` (0xC0)
  maps to `0x28`, also as recorded. Nobody mis-measured; **the active layout differed between two
  launches of the same game on the same machine, hours apart.** So:

  | | morning launch | afternoon launch |
  |---|---|---|
  | layout | `0x04250425` | `0x08090809` |
  | VK reaching scancode `0x29` | `0xDE` | `0xDF` |
  | `VK_OEM_3` (0xC0) → | `0x1A` | `0x28` |

  **The rule this earns is stronger than "layouts differ between machines":** anything cached — a
  constant in code, a value in this dossier, a helper script written earlier in the same session —
  can be stale by the next launch. DirectInput binds the physical **scancode 0x29**; that is the
  stable fact, and the VK that reaches it is not. **Send the scancode** (`scan 0x29`, added to the
  proxy 2026-09-01) or resolve the VK at the moment of use from the layout of the **game's own UI
  thread**: `GetKeyboardLayout(GetWindowThreadProcessId(hwnd, NULL))` then
  `MapVirtualKeyExA(0x29, MAPVK_VSC_TO_VK, hkl)`.

  **The dead-key behaviour is layout-dependent too:** on the morning layout the console key composed
  with the next character; on the afternoon layout it did not. Keep the space-then-backspace flush
  anyway — two keystrokes, harmless when unnecessary, and you cannot know in advance.

  **(b) It is a DEAD KEY.** Opening the console leaves an accent pending, and the **first character
  typed afterwards composes with it**: `getviewpos` arrives as `Çgetviewpos`, `com_...` as `*om_...`.
  **Fix: after opening the console send space, then backspace** — the space absorbs the composition,
  the backspace removes it, and the command types clean.

  **(c) Console toggling has state.** A helper that toggles open/closed must be entered with the
  console **closed**, or it closes it and types the command into the game as movement keys. Make the
  helper open-read-capture-close as one unit so its pre- and post-state match.
- **✅ HOW TO LAUNCH THE VULKAN BUILD (verified working 2026-08-26).** Two things are required
  together — either alone fails:
  1. **`r_renderAPI "1"`** in `DOOMConfig.local` (must match the build; see §11).
  2. **Launch `DOOMx64vk.exe` directly with `SteamAppId=379720` set in the environment.** Steam
     normally passes the app id to the process it starts; launched by hand there is nothing to tell
     `steam_api64.dll` which app this is, and there is **no `steam_appid.txt`** in the game folder,
     so `SteamAPI_Init` fails and the game exits instantly — no window, no log, no crash entry.
     Setting the env var for that one process is enough; it writes nothing to the game folder.

  **Verified:** `DOOMx64vk.exe` running on Vulkan, user reports *"runs just fine, smooth fps"* on
  the dev PC (GTX 1660 SUPER) — so the Vulkan target is confirmed viable, not merely inferred.
  ⚠️ **Caveat on a related claim:** the same session's "GL fails when launched directly" observation
  came from a **flawed control** — the GL attempt did not set `SteamAppId` while the Vulkan attempt
  did, so two variables differed. **Do not conclude the GL build is broken**; the likeliest reading
  is that `SteamAppId` is simply required for *any* direct launch. Untested either way.
- **✅ EXTERNAL COMMAND CHANNEL + FOUR-BACKEND INPUT BUILT (2026-08-31, dev PC).**
  `[built-not-proven 2026-08-31 -- clean build, off-game smoke test passes, NEVER RUN AGAINST DOOM]`
  Commands are appended to **`doom_automation_cmds.txt`** beside the exe and answered in
  `doom_vk_proxy_log.txt`; helper `scripts/doom-auto.ps1`. Opt-in (`DOOM_AUTOMATION=1` or a
  `doom_automation_enable.txt` marker), off by default. Commands: `status help mappings snapa
  snapb dump tol <f> backend <name> move <keys> [frames] look <dx> <dy> [frames] probe stop`.
  This replaces the NUMPAD-only trigger that left M1 built-but-never-run for five days.
  - **`tol` is runtime for a reason:** the expected first result is an unusable or empty candidate
    count, and retuning a `#define` would need a rebuild, which needs a relaunch, which is the
    user's to give.
  - **Four input backends, because "the API succeeded" is not "the game reacted"** -- the
    distinction that cost XIII a session (600 px of `SendInput` = **0.0deg** yaw, exclusive-mode
    DirectInput) and RE Village another (`SendInput` ignored outright, `PostMessage` honoured).
    **`inproc` REBUILT 2026-08-31** after the import table disproved its premise (S11): it now
    answers the calls DOOM actually makes -- `GetAsyncKeyState` / `GetKeyState` /
    `GetKeyboardState` for keys, and the `Get`/`SetCursorPos` pair for look, feeding back
    centre+delta in the shape the game expects. Being in-process means the game asks *us*, not the
    OS, so focus and DirectInput's exclusive mode stop mattering. `DirectInput8Create`'s
    `CreateDevice` is instrumented to **log** whether DI8 carries keyboard/mouse here or only
    controllers -- measure before building the harder path. Then `sendinput` (a real chance for
    keys, since the key-state calls do reflect it; the mouse is likely lost to DI8 exclusive mode),
    `postmessage` (DOOM does pump messages, so menus may answer), and `vigem` (**the best bet** --
    XInput is imported directly).
  - **`probe` runs a no-input CONTROL first** and scores each backend against it. The control is
    the whole point: idle sway and TAA jitter move the camera on their own, so "something changed"
    is not evidence. A backend counts only on a clear margin over the control.
  - **Hooking is IAT patching, not an inline trampoline** -- it writes a data page rather than
    code, so it needs no disassembler and does not argue with **Control Flow Guard** (S3, on).
  - **Known open risk:** if DOOM reads input through `GetRawInputBuffer` rather than
    `GetRawInputData`, the hook installs and still produces nothing. `autoinput_init` logs whether
    that import is present, so the log says which case we are in.
  - **ViGEm reports unavailable rather than pretending.** The driver needs an elevated install
    (still an open user action) and writing its report path blind would be unverifiable code.
- Note the machine rule: **only the user launches the game.**
- Local config lives at `%USERPROFILE%\Saved Games\id Software\DOOM\base\` —
  `DOOMConfig.cfg` (cloud-synced) and `DOOMConfig.local` (machine-local, not synced).
  Current dev-PC `DOOMConfig.local`: `r_renderAPI "0"` (**OpenGL**), `r_fullscreen "0"`
  (**windowed** — helpful for debugging), `r_mode "7"`.
- The `.local` file is the right place to force renderer/window state for a test, since it is
  explicitly excluded from Steam Cloud sync and so cannot leak to the home PC.

## 11. Dead ends & false leads (save future time)

- **🚨 `postmessage` IS UNTESTED, NOT DISPROVED `[disproved 2026-08-31, audit]`.** The earlier
  "no effect" result was taken **while the player was jammed against a cave wall**: the `sendinput`
  move four seconds earlier managed only **1.2 m** (257.0 -> 255.8) for exactly that reason. A
  working backend and a dead one look identical when the player cannot move. **Re-test from open
  ground.**

- **🚨 STANDING RULE, earned three times today: before recording a NEGATIVE result as fact,
  confirm the test could have produced a positive one.** Check that (a) the mechanism applying the
  variable actually works, (b) only one thing changed before the observation, and (c) the game was
  in a state where the expected effect was possible. All three of today's withdrawn claims were
  setup failures, not analysis failures " + DASH + " the measurement and the reasoning were fine; the state
  of the world when the measurement was taken was not. Cheapest guard: a screenshot **before** the
  test, not only after.

- **✅ INPUT: `sendinput` DRIVES DOOM COMPLETELY `[verified-live 2026-08-31, run 2 --
  movement n=2, look n=3 including a reversal]`.** Movement: waypoint **271.9 m -> 232.7 m** (~40 m).
  Look: a large injection swung the view right round, and an **equal-and-opposite injection returned
  it to the same compass position** -- so yaw is controllable and reversible, not a one-off.
  **Caveat: `sendinput` needs the game to be the FOREGROUND window.**

- **🚨 CORRECTION `[disproved 2026-08-31, run 2]`: `inproc-keystate` does NOT work.** An earlier
  note credited it with a 15 m walk; that was a **misattribution** -- the probe ran control -> inproc
  -> sendinput and was screenshotted only after the whole sequence. Two isolated tests of `inproc`
  alone produced **zero** movement, while `sendinput` moved 40 m under identical conditions.
  **Why it cannot work:** the early hook logs `DirectInput8 CreateDevice(SysKeyboard)` --
  **gameplay keyboard goes through DirectInput 8**, not the Win32 key-state calls. Our hooks install
  correctly and patch functions the game never consults. `sendinput` works because it feeds the real
  OS input stack, which DI8 reads in non-exclusive mode -- the same reason it reaches the mouse.
  `postmessage`: no effect. `vigem`: still untested (driver).
  **Method lesson: an experiment that changes two things and is measured once cannot attribute the
  result.** One isolated test per backend, screenshotted immediately, beat the elaborate instrument.

- **A too-small injection reads exactly like failure.** ~5,400 px of mouse motion gave a few degrees
  and nearly had mouse-look written off; ~36,000 px swung the view fully round. **Saturate first,
  then tune down.**

- **DI8 mouse uses BUFFERED `GetDeviceData`** `[measured 2026-08-31]`, so immediate-mode `lX`/`lY`
  injection is ignored -- now moot, since `sendinput` reaches the device anyway.

- **🚨 WITHDRAWN `[disproved 2026-08-31, later the same day]`: the entry below claiming the
  address-based differential cannot discriminate movement **was itself produced by a broken test**,
  and is not supported.
  **The "walk" condition never walked.** The log is unambiguous: `backend inproc` at 14:11:51,
  `move keys=0x1 ... via inproc-keystate` at 14:11:59 " + DASH + " and at **14:14:05, after the conclusion
  had already been drawn**, an isolated test proved `inproc-keystate` moves the player **zero**
  units. So the walk run and the stand-still control were **the same condition**, which is exactly
  why they scored 319 vs 331.
  **The differential is therefore UNTESTED here, not disproved.** Re-running it with `sendinput`
  (the backend since verified to work) is cheap now that scans take ~4 s and no longer freeze the
  game " + DASH + " though its practical value is low, since the GPU-side copy was independently shown to
  be downstream of rendering (S6f/S6g), and that finding does **not** rest on this one.
  **The method rule this earns: a test whose independent variable is applied through an unverified
  mechanism proves nothing.** I varied "movement" using a backend I had not yet confirmed could
  move anything. Verify the knob turns before trusting what the dial says " + DASH + " sibling to the
  attribution trap recorded in the cross-engine library the same day.

- **🚨 camhunt's ADDRESS-BASED DIFFERENTIAL IS INVALID HERE `[disproved 2026-08-31, run 2,
  paired control]`.** Proven directly:
  | Run | changed | still orthonormal |
  |---|---|---|
  | `snapa` -> **walk** -> `snapb` | 2780/4096 | **319** |
  | `snapa` -> **stand still** -> `snapb` | 2820/4096 | **331** |
  **Standing still scores the same as walking.** DOOM writes uniforms into **per-frame dynamic/ring
  buffers**, so a given address holds a different object's matrix every frame and "the bytes changed"
  measures buffer recycling. The premise behind camhunt -- a matrix at a stable address -- does not
  hold. Same root cause as the earlier `probe` failure, now demonstrated rather than inferred.
  Orthonormality is also weak here: the list fills at **4096 even at `tol 1e-5`**, because a 64 MB
  uniform buffer legitimately holds thousands of orthonormal transforms.
  **Translation sits in COLUMN 3** (row 3 read 0,0,0 throughout); survivor values are plausible world
  positions in the thousands, matching the Phase 0 `getviewpos` scale.
  **Replacement plan -- search by VALUE, not by address:** add a `key`/`type` command to drive the
  console, `com_showCameraPosition 1` to put live position+rotation on screen, screenshot it for
  ground truth, then search the buffer for those floats. A known value is a far stronger filter than
  a numeric property and needs no stable address.

- **🐌 Scanning mapped Vulkan memory directly is pathological `[measured 2026-08-31]`.** One
  `snapshotA` took **3 min 45 s** and froze the game for its duration. `HOST_VISIBLE` memory is
  typically **write-combined** — built for streaming CPU writes, brutally slow to read — and the
  scan did ~24 million small strided reads out of it, for an effective **~430 KB/s**.
  **Fix:** bulk `memcpy` into ordinary cached RAM, then scan the copy; 16-byte stride (uniform
  matrices are at least 16-byte aligned); a six-multiply early reject before the expensive checks;
  and regions scanned in **flush-count order**. Live `budget <MB>` / `stride <n>` commands added so
  tuning never costs a relaunch.

- **⏰ Hook timing matters more than it looks `[measured 2026-08-31]`.** `autoinput_init` at frame
  120 logged **no** `DirectInput8Create` at all: DOOM builds its input devices during startup,
  `vkCreateInstance` at 13:24:51 versus first presented frame at 13:25:51 — **a full minute apart**.
  Anything that must observe engine initialisation has to hook from the earliest API call, not from
  the first frame.

- **🗺️ Where the camera almost certainly is `[measured 2026-08-31]`:** 7 live `vkMapMemory` regions
  (2 are `VK_WHOLE_SIZE`, skipped as unknown-extent). **`map 2`, 64 MB, 27,907 flushes** dwarfs
  everything else (`map 6`: 2,983; the three 75 KB regions: 0). That is the per-frame uniform
  buffer. Scan it first.


- **🚨 DISPROVED `[disproved 2026-08-31]`: "DOOM 2016 uses Raw Input."** I wrote that into this
  dossier, STATUS, and the cross-engine library on 2026-08-31, reasoning that a 2016 engine would
  not use the exclusive-mode DirectInput that beat XIII (2003) and Psychonauts. **It is wrong.**
  `llvm-objdump -p` on both shipped executables shows **zero** raw-input imports — no
  `GetRawInputData`, no `GetRawInputBuffer`, no `RegisterRawInputDevices`.
  - **What DOOM actually imports for input** `[measured 2026-08-31]`: **`DINPUT8.dll` →
    `DirectInput8Create`**; **`XINPUT1_4.dll`** (ordinals 2/3) linked directly; Win32 key state
    **`GetAsyncKeyState` / `GetKeyState` / `GetKeyboardState`** (+ `MapVirtualKeyA`, `ToUnicode`,
    `ToAsciiEx`); and **`GetCursorPos` + `SetCursorPos`**, the classic centre-the-cursor-and-read-
    the-drift mouse-look pattern. Plus a real message pump and its own `SetWindowsHookExA`.
  - **Cost:** a whole in-process input backend was designed and built around posting `WM_INPUT`
    and answering `GetRawInputData` — for a function this game never calls. Rebuilt the same day,
    before any live run, because the import table was checked before asking for one.
  - **The rule this earns: read the import table before designing an input layer.** One
    `llvm-objdump -p` decides the entire approach. And *"the game is from year N, therefore it
    uses API X"* is not evidence — DOOM 2016 is on the same input path as XIII (2003).
  - **Consequence:** the ViGEm backend went from weakest to **most likely to work**, because
    XInput is imported directly, so a virtual pad is seen as a genuine controller and DirectInput's
    exclusive mode never enters into it. The ViGEmBus install is now the highest-value unblock.

- **🚨 `r_renderAPI "1"` ALONE BREAKS THE LAUNCH — the cvar does not pick the executable
  (confirmed 2026-08-26 by a failed launch).** The two executables are **separate build
  configurations**, proven by their own PDB paths:
  - `DOOMx64.exe` → `L:\zion\code\build\bam-output\Zion\`**`x64_gl`**`\shippingretail\DOOMx64.pdb`
  - `DOOMx64vk.exe` → `L:\zion\code\build\bam-output\Zion\`**`x64_vulkan`**`\shippingretail\DOOMx64vk.pdb`

  `r_renderAPI` exists in **both** binaries because the cvar lives in shared code — but the GL build
  has **no `vulkan-1` import and no Vulkan backend compiled in**, and it contains **no reference to
  `DOOMx64vk.exe`**, so it cannot hand off either. Steam launches `DOOMx64.exe` (confirmed from a
  working session's own `------ Command Line ------` log). Setting `r_renderAPI "1"` therefore asks a
  GL-only binary for a renderer it does not contain: it aborts during renderer init and exits
  **before writing any log**, leaving *no* crash entry in the Windows Application event log and *no*
  `qconsole.log` — which is exactly the signature observed.

  **To actually run Vulkan: launch `DOOMx64vk.exe` directly** (with the Steam client running — there
  is no `steam_appid.txt`, so it relies on the live client, the same pattern as the Far Cry 2
  launch-directly note). **To restore the working state: set `r_renderAPI` back to `0`.**

  *Dossier §3 stated the exe-level fork correctly from the start; the §9 cheat-sheet row contradicted
  it and said the cvar "selects which exe launches". That row was wrong and is now corrected.*
- **❌ The console is not a route to the stereo path.** Fully closed 2026-08-26 (§4a). The
  `stereoRender_*` cvars are in the binary but never registered in a retail build, and
  `com_production` — the switch that would change that — is itself not registered. Don't re-attempt
  this from the console; it costs a session and the answer is already known.
- **⚠️ `devMode_enable` is a trap as shipped.** It exists and reads `0`, but
  `devMode_fatalErrorOnEnter` reads **`1` by default** — flipping dev mode would FatalError rather
  than enter it. If anyone retries this, **read `devMode_fatalErrorOnEnter` back after setting it to
  `0`** before touching `devMode_enable`; if it still reads `1` it is ROM/shipping-disabled and the
  next command crashes the game.
  - **Public precedent points the other way, and the tension is unresolved.** `[reported, /gr
    2026-08-27]` Multiple independent sources (2016-2020: a Steam guide updated 2020 with dated
    comments, Shacknews' launch-week guide, several Steam threads) describe `devMode_enable 1` --
    including a **`+devMode_enable 1` command-line launch option** -- as a routinely used,
    **non-fatal** unlock, with one well-documented but non-fatal side effect: the save is
    cheat-flagged and Steam Cloud sync can then make it look corrupted. No source reports a crash.
    **Neither reading disproves the other:** those sources predate our build (`20240321-...`) by
    years, so either a tripwire was added later or `devMode_fatalErrorOnEnter` gates something
    narrower than its name suggests. Our own reading of `1` is `[verified-live 2026-08-26, n=1]`.
    If tested: use the **launch-option route on a throwaway save**, back the save folder up first,
    and if it works check `listCvars stereo` and `com_production` visibility immediately -- no
    public source covers that part, and it is the question standing between this project and
    knowing whether the gated cvars are merely hidden or never constructed. Launching is the
    user's call. Full write-up: `external-research/topics/2026-08-27-devmode-enable-public-precedent-and-the-fatal-error-tension.md`.
- **❓ UNTESTED GATE CANDIDATE — `+com_allowconsole 1`, a name from this engine's own
  family.** `[reported]` for **id Tech 5** (The Evil Within, one generation earlier): the console is
  opened by that launch option, after which `noclip`, `God`, `g_stoptime` and `devmapjump` work,
  with no mod and no developer mode. **Untested on id Tech 6.** Better shaped than the community
  guesses above on two counts: the name comes from this lineage rather than a forum, and it applies
  at **launch time**, before the process can guard itself — the pattern this estate already
  records as beating in-process attempts at gates. Costs one line in the launch script.
  **Run it so the result means something:** read `listCvars` / `listCmds` counts before and after
  (retail baseline **171 / 40** `[verified-live 2026-08-26]`) — a changed count is the only
  unambiguous positive; **change one thing at a time**, never combined with `+devMode_enable 1`, or
  a positive cannot be attributed to either. If the count moves, check `listCvars stereo` and
  `com_production` immediately. Note §6a: even a won gate yields parameters, not the stereo
  on-switch. Via `/sr`, 2026-09-01.
- **🪤 METHOD TRAP — `strings -n 4` hides short tokens.** The static pass used
  `llvm-strings -n 4`, whose 4-character minimum silently dropped `God`, `rp`, and every other
  3-character name, producing a confidently-stated wrong conclusion (§9). **Any static string sweep
  on any project should use `-n 2`/`-n 3` for command/cvar-name questions**, or cross-check against
  a live `listCmds`. Generalisable beyond this game — worth carrying to the shared library.
- Caution carried from `-external-research`: **vorpX Geometry-3D is reported broken for this game**
  — don't plan around it.

## 12. Open risks toward the North Star

- **✅ LARGELY ANSWERED (2026-09-01) — gated cvars are HIDDEN, not absent** `[reported, via /gr]`.
  The long-open question ("are the gated cvars merely hidden or never constructed?") now has a
  strong public answer: **`DOOMLegacyMod`** (emoose, updated 2024 by brunoanc) re-adds the hidden
  console on **retail without dev mode**, via a `dinput8.dll` proxy that patches before the engine
  initialises, and reports **39/170 → 290/6592** commands/cvars. Our own live measurement was
  **40/171** `[verified-live 2026-08-26]` — the same gate, to within one each. 6,592 cvars *with
  help text* is an enumeration of structures that exist, not an invention. Not `[verified]`:
  untested on our build. Caveats: closed source, no licence stated, targets "the April 2024 Update"
  while we run `20240321-104810-ginger-fuchsia`, and it hooks early — as does our `vulkan-1` proxy,
  so run either alone first. **Whether to install it is the user's call, not a session's.**
- **The gated command set includes the camera tools** `[reported]`: `rp` ("Displays or modifies a
  renderparm"), `renameRenderProg`, `setviewpos`, `setplayerviewpos`, `envshot`, `testImage`. `rp`
  would be a **typed, named** read/write window onto `globalViewOrigin`, `viewMatrix*`,
  `projectionMatrix*` and the `explicitProjectionMatrix` / `explicitFov_*` family — the sanctioned
  equivalent of what §6h does by writing twelve raw floats. **⚠️ But `setviewpos` is confirmed NOT
  registered on retail** `[verified-live 2026-09-01]`, so none of this is reachable until the gate
  is opened.
- **✅ RESOLVED 2026-09-01 (afternoon) — the full cvar list WAS read, and the dormant stereo cvars
  ARE in it** `[verified from published source, 2026-09-01, whole file]`. The "needs a human with a
  browser" note is withdrawn. The obstacle was never the file — it was using a *page fetch* (which
  truncates) instead of a *download*. `curl -L` retrieved all **711,227 bytes / 11,103 lines /
  6,572 cvars** in one call.
  - **Control first, since the earlier negative died on exactly this:** `g_fov` — verified live on
    our own build — is present at line 3791 ("camera field of view"). The read is sound, so a
    negative from it now means something.
  - **`stereoRender_*` — PRESENT, all four**, help text matching our static pass word for word:
    `stereoRender_separation` "world units from center to eyes" · `stereoRender_screenSeparation`
    "screen units from center to eyes" · `stereoRender_guiOffset` "shift guis so they don't appear
    at infinity" · `stereoRender_swapEyes` "swap target buffers for left and right eyes".
    **The morning claim that they are absent is `[disproved 2026-09-01]`** — truncated read.
  - **`multiView_60Hz` — PRESENT**: "0 = alternate frame rendering, 1 = render [both each frame]" —
    precisely the **two-eyes-in-one-frame** switch §13 names as the real remaining stereo question.
  - **`com_production` — PRESENT**, and so is **`com_forceProductionCvars`** ("Set to force
    production cvars to specific values during build"), a second lever adjacent to the master gate
    that we did not know existed.
  - **⚠️ `explicitProjectionMatrix` / `explicitFov_x|y` / `forceIdentityViewMatrix` — ABSENT.** Not
    cvars at all; every `explicit*` hit belongs to `ai_`, `pm_`, `fs_` or `prowler_`. §6c's named
    override fields are **renderparms or code-level fields**, so the route to them is **`rp`** (which
    IS in the command list), not a cvar set. A valid negative this time — the control passed.
  - **🚨 The nuance that matters most: there is NO stereo MODE cvar.** Searching the whole file for
    `stereo` returns those four plus one unrelated sound cvar — nothing selecting
    `stereoRenderMode_t`, and no `hdmi3d` / `topBottom` / `leftAndRight`. §6a noted the mode cvar's
    name was unresolvable statically and said "find it live via `listCvars`"; this indicates it is
    **not a cvar at all**. **Opening the console gate would therefore hand us the stereo path's
    PARAMETERS but not its ON-SWITCH** — enabling stereo may still require calling engine code. That
    is a materially different problem from "set a cvar", and it should be settled before anyone
    treats the gated console as the route to stereo.
  - **No HMD/Oculus/Rift VR cvars exist** (the `rift` hits are AI demon-spawn resource cvars).
  - **Method note worth carrying:** `curl -L` the raw file and grep locally. A page fetch that read
    only the head of the alphabet produced a confident, wrong negative here.
- **REVISED (2026-08-26).** The original entry assumed "id Tech 6 has no known prior turnkey VR
  injector, expect a fully manual camera-matrix hunt." That is now too pessimistic. The engine has
  a native stereo-3D path (§6a), named override fields (§6c), a named renderparm table (§6b), a
  built-in reflection database (§6d), an unprotected binary (§4), and a direct `OPENGL32.dll`
  import to proxy. The realistic risk profile has shifted from *"can we even find the camera"* to
  the questions below.
- **~~Is the inherited stereo path still wired up?~~ PARTLY ANSWERED (2026-08-26).** It is **not
  reachable from a retail console** — the cvars are never registered (§4a). Whether the underlying
  *render code* still functions when driven some other way (in-process cvar registration, or
  bypassing cvars entirely and calling the stereo render path directly) is **still open**, and is now
  a question for the proxy to answer, not the console.
- **Two identical centered views (§6a) means separation happens downstream.** If it is a pure
  screen-space/projection-skew trick, it gives correct *stereo* but not correct *per-eye
  positional* geometry — good enough for comfort-3D, not automatically good enough for 6DOF.
  Verify what the separation actually does to the projection before building on it.
- **Head tracking is still entirely ours to build.** Nothing in the binary suggests a pose input
  path; `stereoRender_guiOffset` mentioning HMDs is about GUI depth, not tracking. Confirmed open
  by `-external-research` too (the Vk3DVision "FullVR" head-tracking question is still unresolved).
- **TAA jitter + motion-vector reprojection** (`mvpMatrixNoJitter*`, `mvpMatrixLast*`) are known VR
  artifact sources and will need addressing.
- **Control Flow Guard is on** (§3) — plan hooking accordingly.
- **Renderer choice is a real fork.** OpenGL is the current default here and offers the cleanest
  proxy; Vulkan has proven third-party per-eye prior art (Vk3DVision). Deciding between them is a
  genuine design decision, not a detail — do it deliberately.
- **The two gates may also bite the proxy.** Production mode and cheat mode are runtime state, not
  console decoration. If gated cvars are never *constructed* (rather than merely hidden), then
  in-process cvar registration won't resurrect them either and the stereo path must be driven by
  calling the render code directly. **Unknown which of those two it is** — determining that is a
  good early proxy milestone.

## 13. Next steps

### Current order (as of 2026-09-01, evening — rewritten when the inbox was drained)

The camera is found, confirmed across a restart, steerable in translation **and rotation**, and
**stereo has been produced from it live**. Three items from the afternoon list are now closed, and
one was withdrawn; what remains is below.

**Closed since the afternoon list:** Photo Mode was entered and answered the HUD question
(§6h-2, `[verified-live 2026-09-01, n=1, user-observed]`); `pholdyaw` ran and **rotation works**,
completing the transform (§6h-3); and the cvar list was read in full, which **withdrew** the
"ask the user for two minutes with a browser" item — the obstacle was the fetch tool, not the
file, and one `curl` did it `[measured 2026-09-01]`.

1. **Two eyes in ONE frame.** The stereo pair so far is two **sequential** frames, so per-frame
   delivery is now the real question, and §6f's per-draw GPU copies are the likely layer.
   **Start with `multiView_60Hz`** — its own help text is *"0 = alternate frame rendering,
   1 = render both each frame"*, which is the engine's own name for exactly this question. It is a
   **registered, ungated** cvar, so it needs no gate work at all.
2. **Mine the reflection database for the eye field — static, no launch needed** (§6d,
   §6a). Look for an eye-buffer field on the view object (BFG's is `viewEyeBuffer`). Since
   §6a established the stereo switch is a **call argument, not a cvar**, this is now the most
   promising route to the on-switch, and it costs no in-game time.
3. **Test the rebase after a reboot**, not a relaunch — still the only thing between
   `[verified-live n=2]` and "the RVA is stable". Use `GetModuleHandle(NULL) + 0x360F6B0` meanwhile.
4. **One cheap launch probe: `+com_allowconsole 1`** (§11). A gate name from this engine's own
   family, applied at launch. Read `listCvars`/`listCmds` counts before and after against the
   **171 / 40** baseline; change one thing only. Ranked last deliberately — §6a means even
   a won gate yields stereo *parameters*, not the on-switch, so it no longer blocks the North Star.

### Superseded order (as of 2026-09-01, morning)

The camera is found, isolated to a single static global, and provably steerable in translation
(§6h). What is open is no longer *where* it is but *how much control it gives*.

1. **Re-measure the RVA on the very next launch** (`DOOMx64vk.exe + 0x360F6B0`). One command's worth
   of work, and it decides whether this project ever needs the value hunt again. Stability is
   `[inferred-static]` until then.
2. **Extend the hold to write the basis, not just the origin.** A yaw needs `forward` and `left`
   rotated together; `phold` writes three floats. This is the real test of whether the address is a
   control point or only a read-back. Needs a rebuild — therefore a relaunch — therefore the user.
3. **Fix the `console` command's key** while that rebuild is happening: send scancode `0x29`
   directly instead of a VK constant (§10), and flush the dead key automatically.
4. **Then** decide the stereo strategy: drive the dormant path, or override projection (§6c) — and
   find out why the HUD and weapon drop out under displacement, since a VR camera that costs the HUD
   is not finished.

**Also still open, unchanged:** the cheap `.cfg` + `exec` gate-bypass probe; the
`+devMode_enable 1` launch-option test with its public-precedent tension (§11); a baseline
proxy-free quit timing (is the ~60 s shutdown ours or DOOM's?); and the question the proxy must
eventually answer — **are gated cvars merely HIDDEN or never CONSTRUCTED?**

### Superseded order (as of 2026-08-31)

The blocker is no longer "what do we build" -- it is one live run. Everything below needs the
game started by the user; nothing here starts it.

1. **Reinstall the current build.** The game folder still holds an OLD proxy
   (94 KB, 2026-08-26 18:03). `scripts/install-and-launch.bat` installs the current one, sets both
   halves of the launch recipe, enables automation and launches.
2. **Get into a level, then hand off** ("all yours"). From there the whole hunt is drivable from
   outside: `probe` to learn which input backend this game obeys, then `snapa` / `look` / `snapb`.
3. **If `probe` says every backend is dead:** read the `[autoinput]` line for whether
   `GetRawInputBuffer` is imported. If it is, that is the likely cause and the hook needs to move
   there. If no backend works at all, the fallback is unchanged -- the user moves, NUMPAD still works.
4. **Tune `tol` live** if the candidate count is unusable, then confirm a survivor
   **arithmetically** against `getviewpos` (S6e: `X Y Z pitch yaw`, Z-up).
5. **Then** decide stereo strategy: drive the dormant path, or override projection (S6c).

*(Superseded list retained above for the record; its items 1-3 are done.)*

### Original list (as of 2026-08-26, Phase 0 complete)
0. **⚠️ USER DECISION PENDING: confirm the Vulkan target** (§4, and
   `-dev-archive/recon/2026-08-26-injection-surface/`). Requires flipping `r_renderAPI` to `1` and
   checking the Vulkan build runs acceptably on this machine — **untested**. OpenGL stays the
   fallback and no camera knowledge is wasted either way.
1. **One cheap probe:** drop a `.cfg` in `Saved Games\id Software\DOOM\base\` (which precedes the
   install dir in the search path) and `exec` it, to see whether config-file cvar sets bypass the
   interactive gate. Costs minutes; would change the plan if it works.
2. **Build the `vulkan-1.dll` proxy** — forward all ~96 exports, log
   `vkCreateInstance`/`vkCreateDevice`/`vkCreateSwapchainKHR`, count `vkQueuePresentKHR`. Load, log,
   survive: the M0 equivalent of every other project in this portfolio. Fail-safe passthrough on
   every path.
3. **Find how `viewMatrix*` reaches the GPU** (§7) — instrument `vkMapMemory` /
   `vkFlushMappedMemoryRanges` / `vkUpdateDescriptorSets` and look for a per-frame buffer whose
   contents track the camera. **Validate against `getviewpos` (§6e) as ground truth** — we know the
   basis is Z-up and the angle order, so a candidate matrix can be checked arithmetically rather
   than by eye.
4. Only then decide stereo strategy: drive the dormant path, or override projection ourselves (§6c).
