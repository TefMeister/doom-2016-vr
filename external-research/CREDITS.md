# Credits & Attribution

This project is a reverse-engineering and modding effort built on the public
research, tools, and documentation of many people who came before us. None of
this would be possible without their work. We list every source we've drawn
on below — including work that helped only as inspiration — by name or
handle, as accurately as we could verify it.

## The game itself

This mod modifies, at runtime, the original **DOOM** (2016) by
**id Software**, published by **Bethesda Softworks**, built on the
**id Tech 6** engine. The game, its engine, and all of its assets belong to
their respective owners, and the game is the entire reason this project
exists. **No game files, code, or assets are distributed in any of this
project's repositories** — only code, notes, and tools we wrote ourselves.

## Prior art, tools, and research this repo draws on

| Source / Work | Creator(s) | Link |
|---|---|---|
| Vulkan specification (Memory Allocation chapter; `VkMemoryPropertyFlagBits` reference) — the host-coherent flush semantics behind the 2026-09-04 topic | The Khronos Group | https://docs.vulkan.org/spec/latest/chapters/memory.html |
| Vk3DVision (Vulkan stereoscopic 3D driver) | Helifax (Octavian Vasilov) | [github.com/helifax/Vk3DVision-Public](https://github.com/helifax/Vk3DVision-Public) |
| Depth3D (ReShade stereoscopic/depth shader) | BlueSkyDefender | [github.com/BlueSkyDefender/Depth3D](https://github.com/BlueSkyDefender/Depth3D) |
| DOOM (2016) — Graphics Study | Adrian Courrèges | [adriancourreges.com](https://www.adriancourreges.com/blog/2016/09/09/doom-2016-graphics-study/) |
| vorpX community forum discussion (G3D status for DOOM 2016) | vorpX forum community | [vorpx.com/forums/topic/doom-2016](https://www.vorpx.com/forums/topic/doom-2016/) |
| DOOM (2016) Cheat Engine table | "DET" (FearlessRevolution community) | [fearlessrevolution.com/viewtopic.php?t=1199](https://fearlessrevolution.com/viewtopic.php?t=1199) |
| Viewmodel FOV Mod - 2016 Edition | Nexus Mods contributor | [nexusmods.com/doom/mods/35](https://www.nexusmods.com/doom/mods/35) |
| "The Devil is in the Details: idTech 666" (SIGGRAPH 2016 talk) | Tiago Sousa & Jean Geffroy (id Software) | [slideshare.net/TiagoAlexSousa](https://www.slideshare.net/TiagoAlexSousa/siggraph2016-the-devil-is-in-the-details-idtech-666) |
| Official DOOM SnapMap Editing Wiki | Bethesda / id Software | [wiki.bethesda.net/wiki/snapwiki/Doom](https://wiki.bethesda.net/wiki/snapwiki/Doom/) |
| SnapHak / Bubblebear (SnapMap unlock tool) | "Chrispy" | documented at [doomwiki.org/wiki/SnapHak](https://doomwiki.org/wiki/SnapHak) (Discord-distributed, not independently verified here) |
| DOOM-3-BFG official GPL source release (`stereoRender_*`/Rift-warp code) | id Software (original code by John Carmack) | [github.com/id-Software/DOOM-3-BFG](https://github.com/id-Software/DOOM-3-BFG) |
| "Exploring Virtual Reality in Doom 3 BFG" | Shacknews | [shacknews.com](https://www.shacknews.com/article/75138/exploring-virtual-reality-in-doom-3-bfg) |
| Doom 2016 Cheat Codes guide (`devMode_enable` sequence, UPDATED 2020) | Steam Community guide author + commenters | [steamcommunity.com/sharedfiles/filedetails/?id=686972243](https://steamcommunity.com/sharedfiles/filedetails/?id=686972243) |
| "Doom 2016: Cheat Codes and Console Commands" | Shacknews | [shacknews.com](https://www.shacknews.com/article/94650/doom-2016-cheat-codes-and-console-commands-godmode-all-unlocks) |
| Steam discussion threads documenting `devMode_enable`/`+devMode_enable 1` history and side effects | DOOM (2016) Steam community members | [steamcommunity.com/app/379720/discussions/0/351660338723079025](https://steamcommunity.com/app/379720/discussions/0/351660338723079025) · ["Launching in Dev Mode: FIXED"](https://steamcommunity.com/app/379720/discussions/0/357286663672706978/?ctp=61) · ["PC fix development tool / development mode" guide](https://steamcommunity.com/sharedfiles/filedetails/?id=683584994) |
| DOOMLegacyMod — re-adds DOOM 2016's hidden console commands & cvars, and the published `doom_cmds.txt` / `doom_cvars.txt` interface dumps | **emoose** (original author), updated and re-hosted by **brunoanc** | [github.com/brunoanc/DOOMLegacyMod](https://github.com/brunoanc/DOOMLegacyMod) · [emoose on GitHub](https://github.com/emoose) · [Nexus mirror](https://www.nexusmods.com/doom/mods/96) |
| DOOM Eternal 6DOF VR mod (single-pass stereo instancing) — technique prior art on the successor engine | Helifax (Octavian Vasilov); reported by **Flat2VR** | [Flat2VR announcement](https://x.com/Flat2VR/status/1704495949978984506) · [demo video](https://www.youtube.com/watch?v=6Z-LGvDUlv8) |
| VK3DVision game-fix list (per-title fix versions and dates) | Helifax / 3D Surround Gaming community | [3dsurroundgaming.com/Vk3DVisionGames.html](https://3dsurroundgaming.com/Vk3DVisionGames.html) |
| Steam Community threads documenting DOOM 2016's Photo Mode (how to enable, camera behaviour, limits) | DOOM (2016) Steam community members | ["How do I use Photo mode?"](https://steamcommunity.com/app/379720/discussions/0/351660338715209462/) · ["Where is my Photo mode"](https://steamcommunity.com/app/379720/discussions/0/351660338713879695/) · ["Cant find Photo mode?"](https://steamcommunity.com/app/379720/discussions/0/351660338713472121/) · ["Doom photomode is missing"](https://steamcommunity.com/app/379720/discussions/0/351660338716958160) |
| "DOOM has a gory new photo mode, here's how to use it" | Critical Hit | [criticalhit.net](https://www.criticalhit.net/gaming/doom-has-a-gory-new-photo-mode-heres-how-to-use-it/) |

Development on this project is AI-assisted: much of the research, code, and
documentation was produced with **Claude (Anthropic)** (https://claude.com)
working alongside the project owner.

## Missing from this list?

If you — or someone whose work you know — contributed to, influenced, or
even just inspired anything used in this project and you aren't credited
here, please **open a GitHub issue on this repo** and we'll correct it as
soon as possible. We would much rather over-credit than leave anyone out.

## Respecting creators

This project exists because other people generously shared their
reverse-engineering research, tools, and modding know-how in public — we've
tried to credit every one of them by name or handle above, as accurately as
we could verify. If you are the creator or rightful owner of anything
credited or used here and you'd rather your work not be referenced in this
repo, or you want specific content removed or no longer used by the mod,
please tell us: **open a GitHub issue on this repo**. We'll act on that
request promptly — no argument, no delay — and we'll find another way to get
the job done that doesn't rely on your material. This is your work; we're
just grateful to have learned from it.
