# Stereo-3D prior art: Vk3DVision proves the Vulkan per-eye override is achievable — but watch the head-tracking gap

**Why it matters:** ENGINE-DOSSIER §12 flags id Tech 6 as having "no known prior turnkey VR
injector (unlike UE4/RE Engine)" and expects a fully manual camera-matrix hunt. That's still true
for a true 6DOF conversion, but there IS real, working, actively-maintained prior art for the
narrower problem of per-eye stereo rendering on this exact engine/game — which is direct evidence
the core technique (intercepting the Vulkan pipeline and duplicating the view with an eye offset)
works on this specific title, before this project writes a single line of its own hook code.

## vorpX: broken for this game, don't rely on it

vorpX's Geometry 3D (G3D) mode for DOOM (2016) is reported dead by users on vorpX's own forum
("Has G3D ever worked in DOOM 2016? Cause it certainly doesn't any more") — it apparently worked
at some point but no longer hooks correctly (game appears flat). Consistent with this portfolio's
general experience that vorpX's G3D hooking is hit-or-miss per-engine/per-patch (compare Burnout
Paradise: vorpX fails outright; Mad Max: vorpX is third-person-only). **Don't plan around vorpX
G3D for this game.** vorpX's own forum points users toward the two alternatives below instead.

## Vk3DVision — the real lead: a maintained, free, Vulkan-native stereo driver with an actual DOOM (2016) fix

**[Vk3DVision](https://github.com/helifax/Vk3DVision-Public)**, by developer **Helifax**
(Octavian Vasilov, `@OctavianVasilov`), is a dedicated Vulkan stereoscopic-3D driver — the spiritual
successor to his earlier **OGL3DVision** (an OpenGL wrapper for Nvidia 3D Vision). It targets
Vulkan games specifically (so it only applies once DOOM 2016 is running its **Vulkan** renderer,
not the default OpenGL one — ties directly into the renderer-choice question in the companion
research note on engine/renderer basics), and explicitly advertises support for "Virtual Reality,
Nvidia 3D Vision, and general Side-by-Side & Top/Under & Hor./Vert. Interleaved 3D-TV" output.

Confirmed via the maintained fix-list page (3dsurroundgaming.com/Vk3DVisionGames.html, run by the
same author/community): a **DOOM (2016)** fix exists and is **actively maintained** — a "Sequential
Frame Stereo" (SFS) build last updated 2021, and a newer fix last updated **2025-08-30** (i.e.
essentially current). DOOM Eternal (built on the successor id Tech 7, same lineage) has an even
more developed fix, including a dedicated **"DOOM Eternal Virtual Reality ver. 0.90"** package
(updated 2024-12-30) — user videos show it running with real headset output (Oculus Rift S, Quest
2 via Link). Both DOOM 2016 and DOOM Eternal are described by users as working in "full Alternate
Frame Geometry 3D."

**Important nuance — this is stereo 3D output, not confirmed full positional head-tracking.** A
Steam Community thread specifically about a "DOOM 2016 VR Mod" names both Vk3DVision's "FullVR"
build and a ReShade/Depth3D-based alternative (below) as the two known options, and its own
read is that **neither delivers true 6DOF/positional head tracking** — they present stereo (or
depth-reprojected) 3D imagery *in* a headset, which is a real and valuable step (binocular depth,
correct per-eye geometry) but is not the same as this project's North Star (head pose driving the
in-game camera). Don't take "VR" in Vk3DVision's own naming at face value — verify directly
whether any head-tracking input loop exists before assuming it's solved. If it *does* turn out to
include head tracking (worth a direct check — the "Virtual Reality ver 0.90" naming and Rift
S/Quest 2 headset demos are suggestive, just not confirmed from public sources alone), that would
be a much bigger deal and worth immediately re-flagging in `ENGINE-DOSSIER.md`.

**License/access note:** Vk3DVision is closed-source — the GitHub repo
(`helifax/Vk3DVision-Public`) hosts only compiled releases, no source, and the project is
Patreon-funded. So this is **tool prior art / feasibility proof, not something to study
line-by-line** — matches this project's own rule (study the public *idea*, never copy
implementation) naturally, since there's no implementation available to copy even if we wanted
to. The useful takeaway is purely "the Vulkan-level per-eye-view-duplication approach is proven to
work on this exact game," which de-risks committing to that approach once Phase 0 confirms the
Vulkan renderer path.

## Depth3D (ReShade) — a lower-effort, different-technique fallback, also seen in the same thread

The same Steam thread also names **BlueSkyDefender's Depth3D** (open-source ReShade shader,
`github.com/BlueSkyDefender/Depth3D`) combined with the "SuperDepth3D" technique and a VR
companion app, as an alternative path to pseudo-3D output. This works by reprojecting the 2D
image using its depth buffer rather than rendering a true second eye — fundamentally a different
(cheaper, less accurate, works on almost any game with a readable depth buffer) technique from
Vk3DVision's real per-eye geometry approach. Not a strong lead for this project's actual goal
(real per-eye camera control), but worth knowing about as a comparison point / absolute-fallback
option if the from-scratch shader-reflection approach hits a wall.

## Next step this unlocks

When Phase 0 confirms the Vulkan renderer path is viable to force on this build, this is strong
enough prior art to justify prioritizing a **Vulkan-first** injection strategy over OpenGL for the
camera work (§6/§7 of the dossier), rather than treating the two renderer paths as equally likely
starting points. Before committing to that, it would be worth a live check of whether Vk3DVision's
DOOM (2016) fix still works on the current Steam build (it's actively maintained, most recent
update 2025-08-30) — a working third-party fix on the exact same build is a good sanity check that
Vulkan-path hooking is still viable post-patches, independent of anything this project builds
itself.

## Sources

- [Doom 2016 – vorpX forums](https://www.vorpx.com/forums/topic/doom-2016/)
- [Has G3D ever worked in DOOM 2016? — vorpX forums](https://www.vorpx.com/forums/topic/has-g3d-ever-worked-in-doom-really-cause-it-certainty-doesnt-any-more/)
- [is DOOM 4 (2016) playable via vorpx? — vorpX forums](https://www.vorpx.com/forums/topic/is-doom-4-2016-playable-via-vorpx/)
- [Vk3DVision-Public — GitHub (helifax)](https://github.com/helifax/Vk3DVision-Public)
- [Vk3DVision creator Patreon (Helifax / Octavian Vasilov)](https://www.patreon.com/vk3dvision/about)
- [VK3DVision Game Fixes list — 3dsurroundgaming.com](https://3dsurroundgaming.com/Vk3DVisionGames.html)
- [Vk3DVision - A Vulkan 3D Vision Driver — Meant to be Seen (MTBS3D) forum thread](https://www.mtbs3d.com/forum/viewtopic.php?f=105&t=25068)
- [DOOM 2016 VR Mod — Steam Community discussion](https://steamcommunity.com/app/379720/discussions/0/3887226396787323119/)
- [WHAT A RUSH! - DOOM ETERNAL in PERFECT 3D and VR thanks to Vk3DVision // Oculus Rift S — YouTube](https://www.youtube.com/watch?v=906af2cRNII)
- [Depth3D — BlueSkyDefender, GitHub](https://github.com/BlueSkyDefender/Depth3D)
