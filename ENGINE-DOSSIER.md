# Engine Dossier — DOOM (2016) (id Tech 6 engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** Phase 0 **static pass complete** (2026-08-26, dev PC) — install finished, both binaries
inspected offline. Nothing has been run live yet. ·
**VR-readiness verdict:** **unusually promising** — the engine ships a real, inherited stereo-3D
render path *and* a fully-named reflection/renderparm database. See §6 and §12.

## 1. Identity
- Game / build / version: DOOM (2016), id Software, published by Bethesda Softworks. Steam release.
  Both shipped executables carry FileVersion `1, 0, 0, 1`, ProductName `DOOM` (the real build number
  is not in the version resource — id versions elsewhere).
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
- Developer console / cvar system: **present**, confirmed statically — `listCvars`, `listCmds`,
  `devmode_enable`, `com_showfps`, `g_fov` all exist as literal strings in the binary. See §9.

## 4. DRM / anti-debug & injection foothold
- **Denuvo is confirmed GONE on this build** — and this is now first-party evidence, not just the
  public prior from `-external-research`. A Denuvo-protected binary has packed/obfuscated sections
  and a stripped import table; both exes here show textbook-clean MSVC sections and a **full,
  readable import table with real API names**. Nothing is packed. Steam DRM (`steam_api64.dll`)
  remains, which is normal and not an obstacle.
- Launch-time-debugger behaviour: **not yet tested live.**
- **Injection foothold — excellent, several options, all confirmed present in the import table:**
  - **`OPENGL32.dll` (GL exe only)** — imported directly. A classic `opengl32.dll` proxy is the
    single cleanest foothold available: it puts us in the middle of *every* GL call including
    `wglSwapBuffers`, with no MinHook, no pattern scanning, and no CFG concerns.
  - **`vulkan-1.dll` (VK exe only)** — a `vulkan-1` proxy or a proper `VK_LAYER_*` implicit layer.
  - **`winmm.dll`** — imported by *both* exes. This is the same proxy vector already proven in
    `the-evil-within-vr-*`, and it works regardless of which renderer we end up targeting.
  - Also imported and usable as fallbacks: `dinput8.dll`, `dbghelp.dll`, `wsock32.dll`,
    `msimg32.dll`.

## 5. Threading & frame structure
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

- Exact constant-buffer slot / byte offsets / handedness / row-major convention: **TBD** — needs
  live shader reflection or a GL/VK capture (Phase 2).
- The per-eye override maths (`K_eye = …`): **TBD**, pending 6c.

## 7. Constant-buffer fill mechanism
- TBD (Phase 2). Note the renderparm indirection: shaders consume *named renderparms*, so there is
  an engine-side table mapping renderparm → uniform/UBO/push-constant location. Finding that table
  is likely more productive than chasing raw buffer writes.
- The console command **`rp <renderParmName> [value]`** ("Displays or modifies a renderparm") is a
  built-in read/write window onto this system — an outstanding zero-code verification tool. A
  sibling command `renameRenderProg <renderProg> [newProg]` swaps shader programs live.

## 8. Pass inventory (by render target)
- TBD (Phase 2). Public head start: the renderer is a **hybrid clustered-forward + deferred**
  design with only **~100 unique shaders total** (SIGGRAPH 2016, per `-external-research`), and
  Adrian Courrèges' "DOOM (2016) — Graphics Study" is a frame-by-frame reference to read when this
  phase opens.
- Confirmed present from renderparms: virtual texturing (`vmtr*`), env probes
  (`envProbesMapArray`), an atlas-based light system (`lightsAtlasMap`, `channelLight0..8`),
  decals, SSS (`sssMap`), bloom, radial blur, PBR debug modes.

## 9. cvar / console cheat sheet
Console opens with `~`. All of the below are **confirmed present as strings in `DOOMx64.exe`**;
none have been executed yet.

| command / cvar | effect | use |
|---|---|---|
| `listCvars` / `listCmds` | dump all cvars / commands | **first move once live** — resolves the stereo-mode cvar name |
| `g_fov <n>` | field of view | quick "console actually works" confirmation |
| `noclip` | free movement, no collision | camera decoupling / test navigation |
| `devmode_enable` | developer mode | ⚠️ flags campaign saves — use a throwaway save |
| `com_showfps 3` | on-screen FPS | perf sanity |
| `r_renderAPI` | 0 = OpenGL, 1 = Vulkan | selects which exe launches |
| `stereoRender_separation` | world units center→eye | see §6a |
| `stereoRender_screenSeparation` | screen units center→eye | see §6a |
| `stereoRender_guiOffset` | GUI depth shift for HMDs | see §6a |
| `stereoRender_swapEyes` | swap eye buffers | see §6a |
| `multiView_60Hz` | AFR vs both-eyes-per-frame | see §6a |
| `rp <name> [value]` | display/modify a renderparm | read `viewMatrixX..W` etc. live |
| `renameRenderProg <prog> [new]` | swap a shader program live | Phase 2 |
| `screenshot [...]`, `envshot` | captures | harness/evidence |
| `testImage`, `r_pbrDebug*` | debug views | Phase 2 |

`god` was **not** found as an exact string (unlike `noclip`, which appears twice) — the
`-external-research` inference that both exist natively is only half-confirmed; don't rely on `god`.

## 10. Autonomous harness recipe (this game)
- Not yet established. Note the machine rule: **only the user launches the game.**
- Local config lives at `%USERPROFILE%\Saved Games\id Software\DOOM\base\` —
  `DOOMConfig.cfg` (cloud-synced) and `DOOMConfig.local` (machine-local, not synced).
  Current dev-PC `DOOMConfig.local`: `r_renderAPI "0"` (**OpenGL**), `r_fullscreen "0"`
  (**windowed** — helpful for debugging), `r_mode "7"`.
- The `.local` file is the right place to force renderer/window state for a test, since it is
  explicitly excluded from Steam Cloud sync and so cannot leak to the home PC.

## 11. Dead ends & false leads (save future time)
- *(none yet)*
- Caution carried from `-external-research`: **vorpX Geometry-3D is reported broken for this game**
  — don't plan around it.

## 12. Open risks toward the North Star
- **REVISED (2026-08-26).** The original entry assumed "id Tech 6 has no known prior turnkey VR
  injector, expect a fully manual camera-matrix hunt." That is now too pessimistic. The engine has
  a native stereo-3D path (§6a), named override fields (§6c), a named renderparm table (§6b), a
  built-in reflection database (§6d), an unprotected binary (§4), and a direct `OPENGL32.dll`
  import to proxy. The realistic risk profile has shifted from *"can we even find the camera"* to
  the questions below.
- **Is the inherited stereo path still wired up, or is it vestigial?** Strings prove the code was
  compiled in; they do not prove it still functions in a 2016 shipping build. **This is the #1
  question and it is cheap to answer live.**
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
  genuine design decision, not a detail — do it deliberately, with the stereo-path test result in
  hand.
