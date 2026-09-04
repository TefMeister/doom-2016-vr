# Research index

**Last `/gr` pass: 2026-09-04 (estate sweep) — CHECK-IN** (board OPEN block, re-audited 2026-09-03 by `/pd`, + INDEX)**.** Inbox empty; my 2026-09-02 eye-field drop is still unread in `engine-research/inbox/` and was left alone. **Nothing new, and not searched** — the one `[PD]` row (eye field on the view object) is what that pending drop addresses; the rest need a launch, a reboot, or a user decision.
_Previous: **Last `/gr` pass: 2026-09-03 (estate sweep) — CHECK-IN** (board OPEN block + INDEX)**.** Inbox empty; my 2026-09-02 eye-field drop is still unread in `engine-research/inbox/` and was left alone. **Nothing new, and little left to search.** The one `[PD]` row — mine the reflection database for an eye field on the view object — is what that pending drop already answers; the remaining rows need a `multiView_60Hz` run, a reboot for the ASLR re-check, or a user decision on `DOOMLegacyMod`. The cvar space in particular is exhausted: the 2026-09-02 pass downloaded the whole 711 KB / 6,572-entry file rather than fetching a page, so "is there a stereo MODE cvar" is settled negative on a complete read, not a truncated one._
_Previous: **Last `/gr` pass: 2026-09-02 (scoped re-run) — CHECK-IN** (board OPEN block + INDEX + the eye-field item)**.** Inbox empty. This morning's pass recorded nothing new; this one went at the static `[PD]` item properly and found something. Reading `renderView_t` …_
_Previous: Last `/gr` pass: 2026-09-01 (second pass, estate sweep) — CHECK-IN. Inbox drained: `/gs`'s report of off-vocabulary confidence tags. Four tags across three topics normalised to the eight-name vocabulary, with the pre…_

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
>
> **Inbox drained, 2026-09-01.** The modding session confirmed (via `inbox/`) that it read the
> `devMode_enable` topic in full on 2026-08-31 and folded it into `ENGINE-DOSSIER.md` §11 and §13,
> with both readings kept side by side and each tagged. Nothing has been tested — testing needs the
> game launched, which only the user does — so that row moves to 👀 **reviewed**, not
> ✅ incorporated. The same drop asked whether public research could settle how id Tech 6 reads
> input, specifically `GetRawInputData` vs `GetRawInputBuffer`. **That question is already answered
> by our own measurement and needs no public source:** dossier §11 records `llvm-objdump -p` on both
> shipped executables showing **zero** raw-input imports of any kind `[measured 2026-08-31]`, so
> neither function is called and the risk it named does not exist. No research budget was spent on it.
>
> **Status update, 2026-09-01.** The `devMode_enable` tension is now largely **moot as a route**,
> though it remains interesting as a fact: a public tool re-adds the entire gated console **without
> dev mode**, and its published command list contains `rp` and `setviewpos`. Three further topics
> were added the same day — the game's retail Photo Mode is a native detached camera, id's own GPL
> source contradicts part of the dossier's stereo caveat, and a developer-authored frame breakdown
> rules out the obvious explanation for the vanishing HUD.
>
> **Status update, 2026-09-01 (afternoon) — four rows resolved in one day, and one of my
> recommendations was wrong.** The modding session acted on all four of the morning's topics, so
> every one moves to ✅ incorporated:
>
> - **The cvar list.** I reported that automated fetch could not read the 695 KB file, correctly
>   caught that its "no `stereoRender_*`" answer was a false negative — and then recommended the
>   wrong remedy, asking for two minutes of the user's time with a browser. **A single `curl`
>   downloads the whole file.** The obstacle was the *fetch tool*, never the file size, and the ask
>   was avoidable. Recorded here rather than quietly fixed, because the lesson is the useful part:
>   *when a fetch truncates, reach for a different retrieval method before reaching for a human.*
> - **The result of that read changes the stereo plan.** All four `stereoRender_*` cvars exist, as
>   do `multiView_60Hz` and `com_production` — but there is **no stereo MODE cvar**. Opening the
>   console gate would hand us the stereo path's *parameters* and not its *on-switch*. New topic
>   below on what that switch actually looks like in this engine lineage.
> - **Photo Mode: confirmed by the user.** It removes the weapon and the HUD outright. So the HUD
>   loss under displacement is **the engine's own designed behaviour** when the view stops being the
>   player's — nothing was broken, and the hypothesis in that topic is settled.
> - **The division of labour was adopted.** Exactly as the HUD topic proposed: the static global is
>   the right lever for a *detached camera* and the wrong one for *stereo*, where only the picture
>   should move — that uses §6f's per-draw copies. **Stereo is now proven from the view-stage
>   address, with depth-correct parallax**, which also vindicates the id-source topic's
>   "try the view stage first" recommendation.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-09-02 | [The eye field has a twin, and the view origin is pre-adjusted](topics/2026-09-02-the-eye-field-has-a-twin-and-the-view-origin-is-pre-adjusted.md) | 🆕 new | ⭐ From id's GPL Doom 3 BFG source: `viewEyeBuffer` (int, −1/+1/0) and **`stereoScreenSeparation`** (float, *"projection matrix horizontal offset"*) are **adjacent and are the last two members** of `renderView_t` — search for the pair, not a lone integer, and either locates the other. Full field order given as an anchor sequence (`fov_x`/`fov_y` and `time[2]` are the landmarks). **The bigger find:** id's comment on both `vieworg` and `vieworg_weapon` is *"has already been adjusted for stereo world seperation"* — the eye offset is applied **twice**, once in the view origin upstream of the renderer and once in the projection, so §6h's origin+basis global is a candidate injection point distinct from the camera buffer. BFG is id Tech 4's descendant: a prediction for id Tech 6, not a layout claim. |
| 2026-09-01 | [There is no stereo MODE cvar — so what turns it on?](topics/2026-09-01-there-is-no-stereo-mode-cvar-so-what-turns-it-on.md) | 🆕 new | Follows the full cvar read: all four `stereoRender_*` parameters exist, `multiView_60Hz` and `com_production` exist, but **there is no stereo mode selector** — so opening the console gate yields the stereo path's *parameters* and not its *on-switch*, and §6a's advice to find the mode cvar live is void. id's own GPL source suggests why: in Doom 3 BFG the backend takes the eye as a **call parameter** (`RB_DrawView(data, stereoEye)`, 0 mono / ∓1 per eye), with `viewEyeBuffer` as first-class state on the view struct and the per-eye GUI offset derived from `stereoScreenSeparation` — no mode is read at draw time. That reframes the on-switch from "flip a global" to "call the render path twice with a different argument", which matches the shape this project has already got working. `[hypothesis]` for id Tech 6; the dispatch loop is located in neither engine yet. Puts **`multiView_60Hz`** (AFR vs both-eyes-per-frame) on the critical path regardless of the gate. |
| 2026-09-01 | [A public tool already defeats the console gate — and it has `rp` and `setviewpos`](topics/2026-09-01-doomlegacymod-unlocks-the-gated-console-rp-and-setviewpos.md) | ✅ incorporated | `DOOMLegacyMod` (emoose, updated by brunoanc) re-adds the hidden console interface on retail DOOM 2016 — **39 commands / 170 cvars → 290 / 6592**, matching our own live measurement of 40/171 to within one each — via a `dinput8.dll` proxy that patches before engine init, and **without dev mode**. Its published `doom_cmds.txt` was read in full and contains **`rp` ("Displays or modifies a renderparm")**, **`setviewpos`**, `setplayerviewpos`, `renameRenderProg`, `envshot` and `testImage`. Strong evidence that the gated cvars are **hidden and constructible**, not absent — dossier §12's biggest open question. Closed-source, no licence stated, build compatibility unverified; proxies a different DLL from ours, so no filename collision. The 695 KB cvar list defeated automated fetch (a first attempt produced a provable false negative). ✅ **Resolved same day by the modding side, and the remedy I proposed was wrong:** the whole file downloads in one `curl` (711,227 bytes / 11,103 lines / 6,572 cvars) — **the obstacle was the fetch tool, not the file size**, so no human, browser or Ctrl-F was needed. With a `g_fov` control confirming the read was sound: **`stereoRender_*` all four PRESENT**, `multiView_60Hz` and `com_production` present, `explicit*` **absent as cvars** (they are renderparms — so `rp`, not a cvar set), and **no stereo MODE cvar at all**. Also `setviewpos` is **not registered on retail** `[verified-live 2026-09-01]`, so it needs the gate opened first. |
| 2026-09-01 | [Retail Photo Mode is a native detached camera](topics/2026-09-01-retail-photo-mode-is-a-native-detached-camera.md) | ✅ incorporated | The `pm_photoMode*` cvars the dossier spotted in retail belong to a real, shipped, **ungated** feature: Options → Game → "DOOM Photo Mode [BETA]", reached from Mission Select, then `\` in-game. The camera **detaches and flies with WASD**, the game keeps running (enemies track the camera; `E` steps frames), FOV is adjustable, the HUD can be hidden, and **DOOM Guy has no character model** so the player is invisible. Explains why §6h's elevated-camera test met no culling collapse — the culling path was *designed* to follow a detached camera. `pm_photoModeMaxDist "5000"` against our 64-unit clamp suggests a far larger safe envelope. A free, zero-code cross-check for the `+0x360F6B0` address; its activation key is layout-dependent in exactly the way the console key is. Restricted to completed, non-Nightmare mission replays. |
| 2026-09-01 | [id's own source says the view origin *is* moved per eye](topics/2026-09-01-id-own-source-says-the-view-origin-is-moved-per-eye.md) | ✅ incorporated | **Supersedes** the dossier §6a caveat (and the same claim republished in the cross-engine case study) that stereo separation is applied only downstream of view setup. id's GPL Doom 3 BFG source declares `renderView_t::vieworg` as *"has already been adjusted for stereo world seperation"* alongside a separate `stereoScreenSeparation` = *"projection matrix horizontal offset"* — so id's lineage applies **both** a real per-eye world-space origin offset **and** a projection shift, which is why two separation cvars exist. Corroborated on the sibling engine: Helifax's DOOM Eternal **6DOF** mod uses single-pass **stereo instancing**, which requires per-eye view matrices. Makes §6h's `globalViewOrigin` write look like the engine's own stereo lever rather than a workaround. The tension with our binary's own "two identical centered views" comment is flagged, not resolved. Also updates prior art: **Vk3DVision was archived 2026-03-05** (final 4.25.5); DOOM 2016's fix is stereo-only and the 6DOF VR package exists **only for DOOM Eternal**. |
| 2026-09-01 | [Why the HUD and weapon vanish under view displacement](topics/2026-09-01-why-the-hud-and-weapon-vanish-under-view-displacement.md) | ✅ incorporated | Targets §6h's closing open item. Courrèges' developer-grade frame breakdown shows DOOM 2016's **UI is drawn to its own LDR render target and composited last**, in the film-grain pass — so it is **not in the world frustum and cannot be culled by moving the world camera**. That rules out the obvious explanation. Two hypotheses remain: the engine has a first-class "the view is not the player's" state that suppresses first-person elements (Photo Mode does exactly this, on purpose), or the static-data address is read by game code as well as by the renderer. If the latter, §6f's per-draw GPU copies and §6h's global are a **division of labour** rather than rivals — writing only the per-draw copies may move the world while keeping the HUD, which is precisely what stereo needs. The weapon is separate and ordinary: it is drawn in the depth pre-pass under the world projection. |
| 2026-08-27 | [devMode_enable public precedent, and the tension with our fatal-error finding](topics/2026-08-27-devmode-enable-public-precedent-and-the-fatal-error-tension.md) | 👀 reviewed | Multiple independent public sources (2016–2020) describe `devMode_enable 1` (interactive or via a `+devMode_enable 1` launch option) as a routinely-used, non-fatal cheat unlock with a well-documented but non-fatal side effect (save gets cheat-flagged; Steam Cloud sync can make it look "corrupted"). This is in real tension with the dossier's own live finding that `devMode_fatalErrorOnEnter` reads `1` by default on the current build — neither source disproves the other; needs a careful live test, safest via the launch-option route on a throwaway save. If it works, the next question is whether it also resurrects `com_production`/`stereoRender_*` visibility — genuinely unexplored even in the public sources. |
| 2026-08-26 | [stereoRender_warp cvars are Carmack's own Rift code](topics/2026-08-26-stereorender-warp-cvars-are-literally-carmacks-oculus-rift-code.md) | 🆕 new | id Software's own public GPL Doom 3 BFG source confirms `stereoRender_warp*` cvars are labeled in-code "this is the Rift warp" — genuine per-eye lens-distortion code John Carmack wrote for his famous 2012 duct-taped Oculus Rift demo. Retail Doom 3 BFG never shipped head-tracking (orientation-only prototype, not released), but the warp shader machinery and quad-buffer stereo mode are real and carried forward in id's engine lineage — direct grounding for id Tech 6's dormant `stereoRender_*` cvars found in DOOM 2016's own dossier. |
| 2026-08-26 | [SIGGRAPH renderer talk + SnapMap Camera object](topics/2026-08-26-siggraph-renderer-talk-and-snapmap-camera-object.md) | ✅ incorporated | A real dev-authored SIGGRAPH 2016 talk describes the renderer as hybrid clustered-forward + deferred with ~100 shaders total, and flags id Tech 6's job system as having latency gaps later fixed in id Tech 7. Official SnapMap docs confirm a real (but static, non-free) Camera object with a top-level FOV property. A Discord-hosted community tool (SnapHak/Bubblebear) already unlocks extra console commands and implies noclip/god already exist natively — access-gated, unverified further. |
| 2026-08-26 | [FOV cvar confirmed + camera cheat-table lead](topics/2026-08-26-fov-cvar-confirmed-and-camera-cheat-table-lead.md) | ✅ incorporated | `g_fov` is the real, confirmed FOV cvar name. A FearlessRevolution Cheat Engine table for this game exists (403'd to direct fetch, needs a human-browser look) that may expose camera/position addresses. Re-checked the Vk3DVision head-tracking question from the prior topic — still genuinely unresolved, no new info found. |
| 2026-08-25 | [Stereo-3D prior art: Vk3DVision](topics/2026-08-25-stereo-3d-prior-art-vk3dvision.md) | ✅ incorporated | vorpX G3D is dead for this game; Helifax's Vk3DVision (Vulkan-native, actively maintained, DOOM 2016 fix updated 2025-08-30) proves per-eye Vulkan override works here — but its "VR" claim needs verifying for real head tracking vs. just stereo output. |
| 2026-08-25 | [id Tech 6 renderer, DRM, console basics](topics/2026-08-25-engine-renderer-drm-console-basics.md) | ✅ incorporated | OpenGL is the shipped default, Vulkan is a later selectable add-on; Denuvo was present at launch and removed later (Steam DRM remains); console opens with `~`, no special launch flag found. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
