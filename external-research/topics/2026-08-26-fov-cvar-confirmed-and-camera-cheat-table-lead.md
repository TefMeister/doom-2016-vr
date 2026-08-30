# The real FOV cvar name is confirmed (`g_fov`), and a public Cheat Engine table exists for this game's camera/FOV — worth a live look before hooking from scratch

**Status:** 🆕 new · **Priority:** medium — a direct follow-up to the 2026-08-25 engine/renderer topic,
which found the console (`~`) and `listcvars`/`listcmds` but explicitly left "the actual FOV/camera-
related cvars" as something to find live rather than guess. This resolves the FOV half of that gap
from public sources instead, and surfaces a community memory-cheat resource for the camera side.

## What was found

- **The FOV cvar is `g_fov`** (usage: `g_fov <number>` in the developer console, opened with `~`) —
  confirmed consistently across multiple independent cheat-code guides (GameRevolution, GameSkinny,
  Steam Community). This is a real, usable cvar name, not a guess — worth trying directly via console
  once Phase 0 confirms console access live, instead of trawling a `listcvars` dump blind.
- **A public Cheat Engine table for this exact game exists**: FearlessRevolution (a legitimate
  single-player Cheat Engine / memory-analysis community, not a piracy site — same category of
  source already relied on elsewhere in this portfolio for RE leads) hosts a DOOM (2016) table by
  a contributor "DET" that a search-result snippet describes as including FOV control, with a note
  to rebind its hotkeys to avoid clashing with other camera tools — implying the table likely
  exposes more than just FOV (community Cheat Engine tables for this era of game commonly also
  expose player-position/camera-angle pointers). **This page returned HTTP 403 to direct automated
  fetch** (same pattern already seen on PCGamingWiki-style community sites elsewhere in this
  portfolio) — its actual contents are unverified beyond the search snippet; worth a human-browser
  visit rather than re-attempting automated fetch.
- **A related Nexus Mods page, "Viewmodel FOV Mod — 2016 Edition,"** also exists for this game,
  suggesting the FOV cvar/mechanism is well-trodden ground for the mod community — also 403'd to
  direct fetch, same caveat as above.
- **Re-checked the still-open head-tracking question from the 2026-08-25 Vk3DVision topic** (does
  Vk3DVision's "FullVR" actually do positional head tracking, or just stereo output?) by reading the
  two primary threads that topic already cited (the Steam Community "DOOM 2016 VR Mod" discussion,
  read directly this pass, and the MTBS3D forum thread, which 403'd to fetch). **No new information
  either way** — the Steam thread only lists the two tool options without discussing head-tracking
  at all. This question remains genuinely open, not resolved by this pass; don't treat it as settled
  in either direction.

## Why this matters for this project

Once Phase 0 confirms the console is reachable on the live build, `g_fov` gives a concrete, known-
real cvar to test immediately (no need to fish through a `listcvars` dump for it) — a quick way to
confirm console command effects are actually taking hold before trusting anything else console-driven.
The Cheat Engine table, if it does expose camera/view-angle memory addresses (unconfirmed — see
caveat above), could meaningfully shortcut the eventual camera-matrix hunt (§6/§7) the same way
community trainers have shortcut similar hunts elsewhere in this portfolio — worth a human-browser
look specifically for that, once camera work becomes the active phase.

## Concrete next step

When Phase 0 live-testing begins: try `g_fov <n>` directly via console as an early, low-effort
console-works confirmation. Separately, whenever camera/view work becomes the active phase, have a
human browser open FearlessRevolution's DOOM (2016) table thread directly (automated fetch is
blocked) to see whether "DET"'s table exposes camera-angle or player-position addresses, not just
FOV — that would be a meaningful head start over a from-scratch memory hunt.

## Sources

- [Doom (2016) Console Command Cheat Codes List — GameRevolution](https://www.gamerevolution.com/guides/70366-doom-2016-console-command-cheat-codes-list)
- [All DOOM 2016 Console Commands — GameSkinny](https://www.gameskinny.com/tips/all-doom-2016-console-commands/)
- [Steam Community Guide: Doom 2016 Cheat Codes (UPDATED 2020)](https://steamcommunity.com/sharedfiles/filedetails/?id=686972243)
- [Doom 2016 Cheat Table — FearLess Cheat Engine (fearlessrevolution.com)](https://fearlessrevolution.com/viewtopic.php?t=1199) (403 to direct fetch — cited from search snippet only, unverified content)
- [Viewmodel FOV Mod - 2016 Edition — Nexus Mods](https://www.nexusmods.com/doom/mods/35) (403 to direct fetch — unverified content)
- [DOOM 2016 VR Mod — Steam Community discussion](https://steamcommunity.com/app/379720/discussions/0/3887226396787323119/) (re-read directly this pass; no head-tracking detail found)
