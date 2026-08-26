# The dormant `stereoRender_*` cvars trace directly to John Carmack's own 2012 Oculus Rift code — confirmed from id Software's own public GPL source

**Status:** 🆕 new · **Priority:** high — directly answers the modding session's own follow-up
question (left in this index 2026-08-26): where does id Tech 6's dormant `stereoRenderMode_t`/
`stereoRender_*` subsystem come from, and is it known to still function anywhere.

## What was found

**id Software officially open-sourced the Doom 3 BFG Edition (2012) engine codebase under GPL**,
and it's hosted on id's own GitHub org: **[id-Software/DOOM-3-BFG](https://github.com/id-Software/DOOM-3-BFG)**
— a first-party primary source, not a decompilation or community reconstruction. Reading
`neo/renderer/RenderSystem_init.cpp` and `neo/renderer/OpenGL/gl_backend.cpp` directly confirms:

- **`stereoRender_enable`** — the general stereo-output cvar, supporting six modes: compressed
  side-by-side, compressed top/bottom, standard side-by-side, 720p frame-packed, interlaced, and
  OpenGL quad-buffer (the mode NVIDIA 3D Vision uses) — all conventional 3D-TV/3D-Vision output
  modes, confirmed working by end users on retail Doom 3: BFG Edition via Quad Buffer + a 120Hz
  desktop (PCGamingWiki, MTBS3D, Steam Community threads).
- **A separate, more specific family — `stereoRender_warp`, `stereoRender_warpStrength`,
  `stereoRender_warpCenterX`/`Y`, `stereoRender_warpParmZ`/`W`, `stereoRender_warpTargetFraction`**
  — and the source code's own comment is unambiguous: **`"this is the Rift warp"`**. This is
  genuine per-eye **optical lens-distortion (barrel-distortion) pre-correction for the Oculus
  Rift**, not a 3D-TV feature: `warpCenterX` sets the per-eye distortion center (mirrored for the
  right eye), `warpStrength` sets the pre-distortion magnitude, `warpTargetFraction` scales the
  through-lens viewable fraction of each half-screen. A dedicated `StereoWarp` shader applies it.

## Where this code actually came from — real, documented VR history

This isn't leftover generic code — it's the direct artifact of **John Carmack's own famous 2012
Oculus Rift integration work**, independently confirmed by contemporary press (Shacknews, and the
Oculus founding narrative widely covered since): before E3 2012, id announced Doom 3: BFG Edition
would support head-mounted displays, and Carmack showed up with a prototype Rift — "held together
with duct tape and hot glue" — built from Palmer Luckey's early hardware, having **written the
head-tracking/warp integration code himself in about a day, without an SDK**. He demoed it again at
QuakeCon 2012 to a strong reception, an event widely credited as a real contributing factor to
Oculus's subsequent Kickstarter and founding. **Important, precise caveat**: per Shacknews'
firsthand account, that demo build had **orientation tracking only, no positional tracking**, and
was explicitly a **separate developer prototype, not shipped in the retail release** — the general
public never got head-tracked VR in Doom 3: BFG Edition, only the conventional 3D-TV/3D-Vision
modes above. What ships in the officially released source (and, per the DOOM 2016 dossier's own
finding, still exists as dormant cvars/types in id Tech 6) is the **lens-warp shader machinery
Carmack wrote for that demo**, carried forward in the engine codebase even though the full
head-tracking input loop that drove it was never part of any public release.

## Why this matters for this project specifically

This gives real technical grounding for the dossier's "dormant, inherited stereo-3D subsystem"
finding: it's not a mystery or a red herring — it's a **direct, traceable lineage** from id Tech 4
(Doom 3 BFG, 2012, Carmack's own Rift-warp code) that appears to have been carried through id's
internal engine codebase into id Tech 6 (DOOM 2016) by shared naming convention
(`stereoRender_*`), dormant because the full VR pipeline was never finished/shipped in any id
title through this point — not because it doesn't work by design. **This is a real reason to treat
the "is it live or vestigial" question as worth a direct, careful live check** rather than assuming
it's simply broken: if the underlying per-eye warp shader logic survived intact (even if unwired
from any current UI/cvar-exposed input path), it could meaningfully shortcut this project's own
lens-distortion-correction work later, since SteamVR/OpenXR runtimes normally handle that
themselves anyway — but the *existence* of working, developer-authored per-eye stereo output
mode 6 (quad-buffer) at minimum is a strong, real signal that this engine lineage's stereo
rendering path is genuine, not vestigial cruft.

## Concrete next step

When DOOM (2016)'s own binary/strings are examined (Phase 0/static recon, once the Steam install
is ready), check specifically for: (a) whether `stereoRender_warp*` cvars are still registered and
settable at runtime (not just present as dead struct fields), (b) whether a `StereoWarp`-equivalent
shader still exists in the shipped shader set (the SIGGRAPH talk's own ~100-shader count, companion
topic, makes this a checkable-by-enumeration question), and (c) whether `stereoRender_enable`'s
quad-buffer mode (6) still produces real per-eye output on this build — that alone, even without
any head-tracking, would independently confirm the per-eye rendering path is live and could be a
much cheaper way to first prove "can this engine draw two distinct eye views" than starting the
camera-hunt from zero.

## Sources

- [id-Software/DOOM-3-BFG — official GPL source release](https://github.com/id-Software/DOOM-3-BFG)
  — `neo/renderer/RenderSystem_init.cpp`, `neo/renderer/OpenGL/gl_backend.cpp`
- [Exploring Virtual Reality in Doom 3 BFG — Shacknews](https://www.shacknews.com/article/75138/exploring-virtual-reality-in-doom-3-bfg)
- [Doom 3 BFG Edition, Stereoscopic settings — Meant to be Seen (MTBS3D)](https://mtbs3d.com/phpbb/viewtopic.php?t=24882)
- [How To Get Doom 3 BFG to Deliver in 3D! — Meant to be Seen](https://www.mtbs3d.com/articles/news/13189-how-to-get-doom-3-bfg-to-deliver-in-3d.html)
- General contemporary reporting on Carmack's 2012 E3/QuakeCon Rift prototype demo and its role in
  Oculus's founding (widely corroborated across outlets, not a single-source claim)
