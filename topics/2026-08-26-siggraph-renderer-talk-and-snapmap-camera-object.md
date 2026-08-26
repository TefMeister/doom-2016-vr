# A legitimate developer-authored renderer talk exists (SIGGRAPH 2016), and official SnapMap docs confirm a real Camera object with FOV — plus a community tool that already unlocks extra console commands

**Status:** 🆕 new · **Priority:** medium — this project is still pre-M0 (Steam install was still
downloading as of the last STATUS.md update), so nothing here is urgent, but all three findings are
genuine primary/near-primary sources worth having on record before Phase 0/2 work starts, rather
than rediscovering them cold later.

## 1. A real developer-authored architecture talk exists for this exact renderer

**"The Devil is in the Details: idTech 666"** — a SIGGRAPH 2016 "Advances in Real-Time Rendering"
talk by **Tiago Sousa** (id Tech 6's lead rendering architect, ex-Crytek) and **Jean Geffroy** — is
a legitimate, developer-authored technical talk about DOOM (2016)'s own renderer, in the same
"primary source, not reverse-engineering" category this library already values (REAC/GDC Vault
talks). Slides are publicly hosted (SlideShare) and a text write-up exists (80.lv). Confirmed
technical facts:

- The renderer is a **hybrid**: "opaque passes and deferred for a nice quality/performance ratio"
  — not pure clustered-forward as some secondary summaries claim, and not pure deferred either.
  The deferred stage outputs only the minimal data needed for reflections/specular occlusion, with
  opaque geometry and decals going through the clustered-forward path (light/decal/cubemap
  culling done via a 3D grid of view-frustum clusters).
- Only **~100 unique shaders total** — a deliberately small, curated shader set (relevant context
  for eventual shader-reflection work in Phase 2: this is not a sprawling shader library to search
  through blind).
- id Tech 6's CPU **job system had known "bubbles"/latency gaps** that id Tech 7 (DOOM Eternal)
  later rewrote to remove a dedicated scheduling core — i.e. this engine's multithreading, while
  real and designed-in from the start, was not fully optimized in its first (this) iteration. Worth
  keeping in mind for frame-timing/hook-injection-point work later: don't assume perfectly even
  frame-to-frame CPU scheduling.
- This pass did **not** find the specific camera/view-matrix delivery mechanism (constant buffer
  vs. push constants, register/binding numbers) — the public talk material doesn't go that deep.
  That remains genuinely open, correctly deferred to this project's own Phase 2 live/shader work
  once M0 is done.

## 2. SnapMap's official documentation confirms a real, developer-defined Camera object — with FOV as a simple property

The **official Bethesda SnapMap editing wiki** (`wiki.bethesda.net/wiki/snapwiki/Doom/`, confirmed
live, official Bethesda-branded content) documents a placeable **Camera** object in SnapMap's
visual-scripting object model:

- **Properties:** Name, Rotation (separate Pitch/Yaw), Hide Player (bool), **FOV (integer,
  degrees)**, Environment (an enum applying post-process visual effects), and "Stay in Camera on
  End Game."
- **Inputs:** Enable/Disable Camera, Fade Camera, Fade From-To Camera, Set Environment, Shake
  Camera. **Outputs: none documented.**
- This is a **static, placed** camera object (set rotation at placement, no documented free-movement,
  path/spline-following, or player-attach mode) — it's a cutscene/security-camera-style tool for
  level designers, **not** evidence of an accessible free/flying camera the way Manhunt's PluginMH
  or Alan Wake's `-freecamera` launch option are for those other projects in this portfolio. Don't
  over-read this as a shortcut to camera decoupling.
- Still genuinely useful: it confirms **FOV is treated as a simple top-level integer property** in
  this engine's own data model (not a derived/computed value), consistent with `g_fov` already
  being a plain top-level cvar (prior topic) — two independent confirmations of the same simple
  FOV representation, for what that's worth. The "Environment" post-process enum is also worth
  remembering later: if the world camera route eventually needs to disable/adjust post-processing
  for VR comfort, this confirms the engine has a first-class concept for that, not just raw
  shader flags.

## 3. A real community tool already unlocks/adds console commands for this exact game — access-gated, noted honestly

**SnapHak** (also called "Bubblebear"), created by modder **Chrispy** and shared via an unofficial
SnapMap Discord community (first revealed 2020-07-13, code last updated 2021-02-02, still actively
hosted/used per DoomWiki), is a real, working, Windows-only tool that **extends SnapMap beyond the
in-game editor and unlocks/adds console commands** on the retail build. A partial public reference
of its commands exists (`wiki.eternalmods.com`), though marked incomplete — the one fully
documented command, `sh_spawn`, casually references **`god mode` and `noclip`** as commands the
user would already be enabling alongside it, implying **both are real, pre-existing vanilla console
commands** on this game, not SnapHak additions — a plausible, though not 100%-explicit, positive
signal for a free/no-collision movement mode once console access is live-confirmed.

**Access caveat, stated plainly:** SnapHak itself is distributed only via an unofficial Discord
server, not a public repo or download page — this pass could not access or verify its actual
command list beyond the one partially-documented command above. Per this repo's own rule (public
info only, read online, never joined/downloaded to study), this is flagged as a lead for a human
to check directly (joining the Discord is a user decision, not something to do automatically) —
not something to treat as verified.

## Concrete next step

Nothing urgent — this project is still pre-M0. Once the Steam install is confirmed and static/live
recon begins: (1) try `noclip`/`god` directly via console as an early test (per the SnapHak-command
inference above), alongside the already-confirmed `g_fov`; (2) keep the SIGGRAPH talk's hybrid
clustered-forward/deferred description and ~100-shader count in mind once Phase 2 shader-reflection
work starts, rather than assuming a single monolithic forward or deferred pipeline; (3) the SnapMap
Camera object is filed as background only — not a lead to actively pursue for the free-camera
problem.

## Sources

- ["The Devil is in the Details: idTech 666" — SIGGRAPH 2016 (Tiago Sousa & Jean Geffroy), slides](https://www.slideshare.net/TiagoAlexSousa/siggraph2016-the-devil-is-in-the-details-idtech-666)
- [idTech 666: The Secret of DOOM's Render — 80.lv (text summary)](https://80.lv/articles/idtech-666-the-secret-of-dooms-render)
- [Official DOOM SnapMap Editing Wiki — Bethesda](https://wiki.bethesda.net/wiki/snapwiki/Doom/)
- [SnapHak — The Doom Wiki at DoomWiki.org](https://doomwiki.org/wiki/SnapHak)
- [SnapHak/Bubblebear commands — Doom Eternal Modding Wiki](https://wiki.eternalmods.com/books/3-command-console/page/snaphakbubblebear-commands)
