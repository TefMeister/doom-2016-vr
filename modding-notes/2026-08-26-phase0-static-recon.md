# 2026-08-26 — Phase 0 static recon: the engine has a stereo path and names its own camera

**Machine:** dev PC · **Live testing:** none — the game was never launched this session.
Everything below is offline inspection of the installed files.

## Where we started

The repos were seeded on 2026-08-25 while the Steam copy was still downloading, so
`ENGINE-DOSSIER.md` was almost entirely `TBD`. The `-external-research` instance had meanwhile
posted four topics with a strong public-source head start (renderer/DRM/console basics, Vk3DVision
prior art, `g_fov` confirmation, the SIGGRAPH renderer talk + SnapMap). Those were read in full
before touching anything, per the standing rule.

The job this session: confirm the public priors against our own copy, and answer the Phase 0
questions the research side explicitly left to live/static verification.

## What the install looks like

68.7 GB, complete. Two executables, and this turned out to matter:

| exe | size | imports |
|---|---|---|
| `DOOMx64.exe` | 77.4 MB | `OPENGL32.dll`, **no** `vulkan-1.dll` |
| `DOOMx64vk.exe` | 101.5 MB | `vulkan-1.dll`, **no** `OPENGL32.dll` |

So the OpenGL/Vulkan choice is **an executable-level fork, not a runtime switch inside one
process**. That is better than expected: whichever we target, the other API is entirely absent
from the address space. `DOOMConfig.local` on this machine has `r_renderAPI "0"` → OpenGL is what
currently launches, and `r_fullscreen "0"` → it launches windowed, which is convenient for
debugging.

## Denuvo is gone — confirmed on our own copy, not just inferred

The research note flagged this as a strong public prior needing first-party confirmation. It's
confirmed. Both exes have textbook-clean MSVC sections
(`.text .rdata .data .pdata .mydata .gfids .giats .tls _RDATA .rsrc .reloc`) and a **complete,
readable import table**. Denuvo-protected binaries have neither. Nothing is packed.

Incidental findings from the same dump: `.reloc` present ⇒ ASLR is on, module base moves;
`.gfids`/`.giats` ⇒ **Control Flow Guard is enabled**, which constrains indirect-call hooking later.

**Injection foothold is easy and over-supplied.** `OPENGL32.dll` is imported directly by the GL
exe — a plain `opengl32` proxy puts us inside every GL call including `wglSwapBuffers`, with no
MinHook and no pattern scanning. `winmm.dll` is imported by *both* exes and is the same vector
already proven in `the-evil-within-vr-*`. `dinput8`, `dbghelp`, `wsock32`, `msimg32` are further
fallbacks.

## The actual find: id Tech 6 has an inherited stereo-3D render path

Present in **both** executables, so it's engine-level rather than renderer-specific:

- `stereoRenderMode_t` = { `STEREO_RENDER_OFF`, `STEREO_RENDER_LEFT_AND_RIGHT`,
  `STEREO_RENDER_TOP_AND_BOTTOM` }, plus `STEREO_MODE_WIDTH` / `STEREO_MODE_HEIGHT`
- a mode value list: `topBottomStereo`, `leftRightStereo`, `HDMI3D`, `HDMI3DtwoPlayer`
- and live cvars carrying the developers' own help text:

| cvar | engine's own description |
|---|---|
| `stereoRender_separation` | "world units from center to eyes" |
| `stereoRender_screenSeparation` | "screen units from center to eyes" |
| `stereoRender_guiOffset` | **"shift guis so they don't appear at infinity in HMDs"** |
| `stereoRender_swapEyes` | "swap target buffers for left and right eyes" |
| `multiView_60Hz` | "0 = alternate frame rendering, 1 = render both each frame" |

The engine says "HMDs" in its own cvar help. This is clearly inherited from the id Tech 5 /
Doom 3 BFG generation, which had real stereo support.

**The important caveat, and it's in the engine's own doc-comment:** the two stereo world views are
*"two identical ones in stereo-3D (both centered between the eyes)"*. So separation is applied
**downstream** of view setup — a projection/screen-space step, not two different view matrices.
Which means: our per-eye override probably belongs at the projection stage. And it means the
built-in path may give correct *stereo* without correct *per-eye positional* geometry. Worth
knowing before anyone gets excited.

## The binary names its own camera

id Tech 6 exposes shader constants as named "renderparms", and the whole table is a plain string
block:

```
viewMatrixX/Y/Z/W          inverseViewMatrixX/Y/Z/W
modelMatrixX/Y/Z/W         inverseModelMatrixX/Y/Z/W
projectionMatrixX/Y/Z/W    inverseProjectionMatrixX/Y/Z/W
mvpMatrixX/Y/Z/W           inverseMVPMatrixX/Y/Z/W
mvpMatrixNoJitterX/Y/Z/W   mvpMatrixLastX/Y/Z/W
viewProjectionMatrixX/Y/Z/W
globalViewOrigin  globalViewFwd  globalViewLeft  globalViewUp
```

Matrices arrive as four separate vec4 renderparms, not one opaque blob. `mvpMatrixNoJitter*` +
`mvpMatrixLast*` confirm TAA-with-jitter and motion-vector reprojection — both known VR hazards,
noted for later.

Better still, there's a console command **`rp <renderParmName> [value]` — "Displays or modifies a
renderparm"**, plus `renameRenderProg <renderProg> [newProg]` to hot-swap shader programs. That's a
built-in, zero-code read/write window onto the exact values we care about.

And there are already-named override-shaped fields sitting in the reflection table:
**`explicitProjectionMatrix`**, **`explicitFov_x` / `explicitFov_y`**, **`forceIdentityViewMatrix`**.
If those are honoured on the main world view, the per-eye projection override could be a *supported
engine input* rather than something we patch in. Completely unverified — but it is the highest-value
thing on the board.

## Bonus: there's a reflection database with the developers' comments in it

Large string regions contain fully-qualified C++ class/enum/field names alongside human-written
descriptions — `idHands::HANDSACTION_VIRTUAL_GUI_ROTATE_UP`, `CAM_FOCUS_PLAYER`,
`VIEW_MOTION_ACTION_*`, `idList < idMapEntity *, TAG_IDLIST, false >`, and doc-comments like *"For
cinematics, we often want to set ZNear much lower, at the expense of depth precision in the
distance."*

This is effectively a built-in symbol source — structurally the same advantage REFramework gives us
on RE Engine, except native to the binary. Mining it properly is its own task and probably worth a
session.

## Corrections to the dossier

§12 previously read "id Tech 6 has no known prior turnkey VR injector — expect Phase 3–4 to be a
fully manual camera-matrix hunt." That framing is now **too pessimistic** and has been rewritten.
The risk has moved from *"can we find the camera at all"* to *"is the inherited stereo path still
wired up, or is it vestigial?"* — a much better problem to have, and a cheap one to answer.

Also corrected: `god` does **not** appear as an exact string in the binary, though `noclip` appears
twice. The `-external-research` inference (from SnapHak's docs) that both exist natively is only
half-confirmed. Don't rely on `god`.

## Next

All of the following need the game *running*, so they wait for the user:

1. `listCvars` / `listCmds` — dump everything. Specifically resolves the **stereo-mode cvar name**,
   which static analysis couldn't recover (linker string dedup separated it from its value list).
2. `g_fov <n>` as the cheap "console actually works" confirmation.
3. **The big one:** set a `stereoRender_*` mode and see whether the inherited stereo path still
   renders. This single test reshapes the whole project either way.
4. `rp viewMatrixX` etc. to read the live camera values with zero code written.
5. Debugger-attach test to confirm the no-Denuvo finding dynamically.

Nothing has been written to the game directory. No code exists yet — deliberately, until the
stereo-path question is answered, because the answer changes what we'd build.
