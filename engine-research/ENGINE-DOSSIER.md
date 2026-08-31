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

**Read carefully — the doc-comment says the two stereo world views are *identical and centered
between the eyes*.** So the eye separation is applied downstream of the view setup (a projection
skew / screen-separation step), not by building two different view matrices. That is the id Tech 5
/ BFG-era approach and it matters: our per-eye override probably belongs at the projection stage,
not the view stage.

**The engine explicitly names HMDs in its own cvar help.** The name of the mode cvar that selects
`stereoRenderMode_t` was not resolvable statically (linker string dedup separates it from its value
list) — **find it live via `listCvars`**.

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
- **🪤 METHOD TRAP — `strings -n 4` hides short tokens.** The static pass used
  `llvm-strings -n 4`, whose 4-character minimum silently dropped `God`, `rp`, and every other
  3-character name, producing a confidently-stated wrong conclusion (§9). **Any static string sweep
  on any project should use `-n 2`/`-n 3` for command/cvar-name questions**, or cross-check against
  a live `listCmds`. Generalisable beyond this game — worth carrying to the shared library.
- Caution carried from `-external-research`: **vorpX Geometry-3D is reported broken for this game**
  — don't plan around it.

## 12. Open risks toward the North Star
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

### Current order (as of 2026-08-31)

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

**Also still open, unchanged:** the cheap `.cfg` + `exec` gate-bypass probe; the
`+devMode_enable 1` launch-option test with its public-precedent tension (S11); a baseline
proxy-free quit timing (is the ~60 s shutdown ours or DOOM's?); and the question the proxy must
eventually answer -- **are gated cvars merely HIDDEN or never CONSTRUCTED?**

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
