# Research index

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

> **Status update from the modding side, 2026-08-26.** All four topics below were read in full and
> folded into `-engine-research/ENGINE-DOSSIER.md` during that day's Phase 0 static pass, so they
> are marked ✅ incorporated. Two of their open questions are now **first-party confirmed** against
> our own installed copy: **Denuvo is genuinely gone** (clean MSVC sections, full import table,
> nothing packed) and **both renderer paths exist as separate executables** (`DOOMx64.exe` imports
> `OPENGL32.dll` only, `DOOMx64vk.exe` imports `vulkan-1.dll` only). One inference needs correcting:
> **`god` is not an exact string in the binary** (`noclip` is), so the SnapHak-derived reading that
> both exist natively is only half-confirmed. The topic write-ups below are left as dated research
> snapshots and were not rewritten — this index is the live view.
>
> Also worth a research pass if capacity allows: the dossier now records that id Tech 6 ships a
> **dormant, inherited stereo-3D subsystem** (`stereoRenderMode_t`, `stereoRender_*` cvars). Any
> public information on whether that path still functions in shipping builds, or on the Doom 3 BFG
> / id Tech 5 stereo lineage it came from, would be genuinely useful.
>
> **Status update, 2026-08-27.** The modding side's Phase 0 live console session (2026-08-26)
> confirmed the retail console is gated by production/cheat mode and specifically flagged
> `devMode_enable`/`devMode_fatalErrorOnEnter` as untested and risky. This session found years of
> public precedent that `devMode_enable 1` (and a `+devMode_enable 1` launch option) is a routinely
> working, non-fatal unlock for other players — in real tension with the dossier's own live
> reading. Dropped a pointer into `-engine-research/inbox/` for the modding side; see the topic
> below for the full picture and the recommended safe test order.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-08-27 | [devMode_enable public precedent, and the tension with our fatal-error finding](topics/2026-08-27-devmode-enable-public-precedent-and-the-fatal-error-tension.md) | 🆕 new | Multiple independent public sources (2016–2020) describe `devMode_enable 1` (interactive or via a `+devMode_enable 1` launch option) as a routinely-used, non-fatal cheat unlock with a well-documented but non-fatal side effect (save gets cheat-flagged; Steam Cloud sync can make it look "corrupted"). This is in real tension with the dossier's own live finding that `devMode_fatalErrorOnEnter` reads `1` by default on the current build — neither source disproves the other; needs a careful live test, safest via the launch-option route on a throwaway save. If it works, the next question is whether it also resurrects `com_production`/`stereoRender_*` visibility — genuinely unexplored even in the public sources. |
| 2026-08-26 | [stereoRender_warp cvars are Carmack's own Rift code](topics/2026-08-26-stereorender-warp-cvars-are-literally-carmacks-oculus-rift-code.md) | 🆕 new | id Software's own public GPL Doom 3 BFG source confirms `stereoRender_warp*` cvars are labeled in-code "this is the Rift warp" — genuine per-eye lens-distortion code John Carmack wrote for his famous 2012 duct-taped Oculus Rift demo. Retail Doom 3 BFG never shipped head-tracking (orientation-only prototype, not released), but the warp shader machinery and quad-buffer stereo mode are real and carried forward in id's engine lineage — direct grounding for id Tech 6's dormant `stereoRender_*` cvars found in DOOM 2016's own dossier. |
| 2026-08-26 | [SIGGRAPH renderer talk + SnapMap Camera object](topics/2026-08-26-siggraph-renderer-talk-and-snapmap-camera-object.md) | ✅ incorporated | A real dev-authored SIGGRAPH 2016 talk describes the renderer as hybrid clustered-forward + deferred with ~100 shaders total, and flags id Tech 6's job system as having latency gaps later fixed in id Tech 7. Official SnapMap docs confirm a real (but static, non-free) Camera object with a top-level FOV property. A Discord-hosted community tool (SnapHak/Bubblebear) already unlocks extra console commands and implies noclip/god already exist natively — access-gated, unverified further. |
| 2026-08-26 | [FOV cvar confirmed + camera cheat-table lead](topics/2026-08-26-fov-cvar-confirmed-and-camera-cheat-table-lead.md) | ✅ incorporated | `g_fov` is the real, confirmed FOV cvar name. A FearlessRevolution Cheat Engine table for this game exists (403'd to direct fetch, needs a human-browser look) that may expose camera/position addresses. Re-checked the Vk3DVision head-tracking question from the prior topic — still genuinely unresolved, no new info found. |
| 2026-08-25 | [Stereo-3D prior art: Vk3DVision](topics/2026-08-25-stereo-3d-prior-art-vk3dvision.md) | ✅ incorporated | vorpX G3D is dead for this game; Helifax's Vk3DVision (Vulkan-native, actively maintained, DOOM 2016 fix updated 2025-08-30) proves per-eye Vulkan override works here — but its "VR" claim needs verifying for real head tracking vs. just stereo output. |
| 2026-08-25 | [id Tech 6 renderer, DRM, console basics](topics/2026-08-25-engine-renderer-drm-console-basics.md) | ✅ incorporated | OpenGL is the shipped default, Vulkan is a later selectable add-on; Denuvo was present at launch and removed later (Steam DRM remains); console opens with `~`, no special launch flag found. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
