# Research index

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-08-26 | [FOV cvar confirmed + camera cheat-table lead](topics/2026-08-26-fov-cvar-confirmed-and-camera-cheat-table-lead.md) | 🆕 new | `g_fov` is the real, confirmed FOV cvar name. A FearlessRevolution Cheat Engine table for this game exists (403'd to direct fetch, needs a human-browser look) that may expose camera/position addresses. Re-checked the Vk3DVision head-tracking question from the prior topic — still genuinely unresolved, no new info found. |
| 2026-08-25 | [Stereo-3D prior art: Vk3DVision](topics/2026-08-25-stereo-3d-prior-art-vk3dvision.md) | 🆕 new | vorpX G3D is dead for this game; Helifax's Vk3DVision (Vulkan-native, actively maintained, DOOM 2016 fix updated 2025-08-30) proves per-eye Vulkan override works here — but its "VR" claim needs verifying for real head tracking vs. just stereo output. |
| 2026-08-25 | [id Tech 6 renderer, DRM, console basics](topics/2026-08-25-engine-renderer-drm-console-basics.md) | 🆕 new | OpenGL is the shipped default, Vulkan is a later selectable add-on; Denuvo was present at launch and removed later (Steam DRM remains); console opens with `~`, no special launch flag found. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
