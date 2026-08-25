# id Tech 6 renderer, DRM, and console — first-look confirmation

**Why it matters:** the project just kicked off (`2026-08-25-project-kickoff.md` in
`-modding-notes`) and `ENGINE-DOSSIER.md` has several open `TBD`s in §3/§4/§6 that gate Phase 0
(renderer API, DRM/injection foothold, console access). This is a first public-source pass on
those specific questions before any live binary inspection — it should save time on Phase 0, not
replace confirming each fact directly against the actual installed build.

## Renderer: OpenGL is the default, Vulkan is a later add-on, selectable

DOOM (2016) shipped at launch with an **OpenGL 4.x** renderer. id Software (lead renderer
programmer **Tiago Sousa**, ex-Crytek, having taken over the role from John Carmack) added a
**Vulkan** backend in a July 2016 patch. Community reporting (GamingOnLinux forum, a Steam guide
on switching APIs) indicates the renderer choice is stored in a config value where `0` = OpenGL and
`1` = Vulkan, and can be changed via config file or launch option — consistent with OpenGL still
being the shipped default rather than something the game auto-upgrades away from.

**Why this matters for this project:** the choice materially changes the injection strategy — a
GL proxy DLL (`opengl32.dll`) is a completely different shape from a Vulkan layer
(`VK_LAYER_*` / ICD interception). ENGINE-DOSSIER §12 already flags this as the thing to resolve
first in Phase 0; this research doesn't resolve it (needs a live check of the installed build's
actual config/launch behavior) but confirms **both paths are real and both need to be accounted
for** — don't assume Vulkan-only or GL-only going in.

Adrian Courrèges' well-known "DOOM (2016) — Graphics Study" (frame-by-frame breakdown of a real
capture) is a strong technical reference for pass structure and render-target inventory once
Phase 0 confirms which API this build is actually using at runtime — worth a full read when
Phase 2 (pass inventory) starts.

## DRM: Denuvo was present at launch, later removed; Steam DRM remains

Multiple Steam Community threads and a PC Perspective article ("DOOM Removes Denuvo DRM",
December 2016) confirm DOOM (2016) shipped with Denuvo anti-tamper at launch and had it **patched
out** in a later update. Standard Steam DRM (not Denuvo) remains on the current Steam build. The
game is also sold DRM-free on GOG, which independently confirms Denuvo is gone (GOG doesn't carry
Denuvo titles). **This has not been independently verified against our own installed copy yet** —
treat as a strong prior (consistent with this portfolio's general pattern of older Denuvo titles
losing it in later patches, e.g. compare Mad Max's confirmed-still-live Denuvo) but confirm
directly, the same way every other project in this portfolio has (a debugger-attach test is the
standard check here, per the Mad Max precedent in `ENGINE-DOSSIER.md`/`STATUS.md`).

## Console: opens with `~` (tilde), no special launch flag found

A Steam Community cheat-codes guide describes opening the developer command console in-game with
the `~` (tilde) key — the classic id-engine binding, consistent with the id Tech lineage (id Tech
4/5/6 all use `~`). No evidence was found of a `com_allowConsole`-style gate needing to be set
first (that cvar name was a specific guess in the original research query and didn't surface in
results) — the console appears to just be there. Caveat found: using **any** console command
flips the save into "Developer Mode" (`devmode_enable 1` is also a real, separate command),
which flags campaign saves and can affect them — worth remembering if a live session wants to
avoid touching the player's real save data, e.g. prefer a fresh/throwaway save or a level restart
for any console-driven testing.

Useful cvars surfaced in passing (unverified, from a community cheat-codes guide, not tested
here): `com_showfps 3` (on-screen FPS), `Listcvars` / `ListCmds` (full command dump — good first
move once console access is confirmed live, to find the actual FOV/camera-related cvars instead
of guessing names).

## Next step this unlocks

Live-confirm, directly against the installed build (not from public sources): (1) which renderer
API is actually active by default and how to force the other one, (2) whether Denuvo is really
gone (debugger-attach test, matching the standard check already used elsewhere in this
portfolio), (3) console opens with `~` with no extra flag, and pull the real cvar list via
`Listcvars`/`ListCmds` to look for FOV/camera names instead of guessing.

## Sources

- [Id Tech 6 — Wikipedia](https://en.wikipedia.org/wiki/Id_Tech_6)
- [DOOM (2016) Working with OpenGL but not Vulkan — ValveSoftware/Proton#219](https://github.com/ValveSoftware/Proton/issues/219)
- [Viewing topic DOOM 2016 — GamingOnLinux forum](https://www.gamingonlinux.com/forum/topic/5223/)
- [Steam Community Guide: How to run DOOM with Vulkan API (with fixes!)](https://steamcommunity.com/sharedfiles/filedetails/?id=722643144)
- [DOOM Removes Denuvo DRM — PC Perspective](https://pcper.com/2016/12/doom-removes-denuvo-drm/)
- [DOOM (2016) is now available DRM-free on GOG — NeoGAF](https://www.neogaf.com/threads/doom-2016-is-now-available-drm-free-on-gog.1683216/)
- [Steam Community Guide: Doom 2016 Cheat Codes (UPDATED 2020)](https://steamcommunity.com/sharedfiles/filedetails/?id=686972243)
- [DOOM (2016) — Graphics Study — Adrian Courrèges](https://www.adriancourreges.com/blog/2016/09/09/doom-2016-graphics-study/)
