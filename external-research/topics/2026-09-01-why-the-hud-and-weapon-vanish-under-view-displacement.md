# The HUD cannot be vanishing for a rendering reason — a developer-authored frame breakdown rules out the obvious explanation

**Status:** 🆕 new · **Priority:** high — this targets `ENGINE-DOSSIER.md` §6h's closing open item
verbatim: *"Why the HUD and weapon drop out under displacement at all. A VR camera that costs the
HUD is not finished."*

## The observation this is about

`[verified-live 2026-09-01]` Holding `DOOMx64vk.exe + 0x360F6B0` at a **displaced** value moves the
view and **drops the HUD, the crosshair and the weapon**. Holding it at **the value it already
holds** changes nothing — everything stays. So the loss is caused by *displacing the view*, not by
the act of writing into engine memory. That control is what makes the symptom attributable; what it
does not do is explain it.

## What the frame breakdown establishes

Adrian Courrèges' *"DOOM (2016) — Graphics Study"* is a frame-by-frame analysis of a real capture of
this exact game, and it is precise about where these two elements live.

**The UI is not in the world pass at all.** Quoting the study's findings: the UI *"is rendered to a
different render-target, in premultiplied alpha mode stored in LDR format"* — deliberately decoupled
so the game *"could apply some filter / post-processing like color aberration or visual distortion on
all of the UI widgets at once"* — and it is composited **last**, *"blended on the top of the game
frame"* during the final film-grain pass, immediately before display.

**This rules out the natural first explanation.** A HUD drawn to its own LDR target and blended at
the very end of the frame is **not in the world frustum** and cannot be culled by moving the world
camera. Whatever moving `globalViewOrigin` does, it cannot geometrically remove a screen-space
overlay composited after the world is already finished.

**The weapon is a different story, and a more ordinary one.** The study places the first-person
weapon in the **depth pre-pass**, drawn *first* — *"first the player's weapon, then static geometry
and finally dynamic geometry"* — as dynamic geometry with per-pixel velocity written for TAA and
motion blur. It uses the standard world projection. So the weapon *is* subject to the world view,
and a displaced camera plausibly moves it out of frame or behind the near plane.

## The hypothesis this produces

`[hypothesis, /gr 2026-09-01 — not tested, and it names the evidence that would settle it]`

**The HUD loss is a game-state response, not a rendering consequence.** Two candidate mechanisms,
both consistent with everything measured so far:

1. **The engine has a first-class "the view is not the player's" state, and it suppresses
   first-person elements when it is entered.** This is not speculation about a hypothetical: DOOM
   2016 ships **Photo Mode**, which detaches the camera, hides the HUD, and leaves the player
   invisible — reporting from its release states plainly that **DOOM Guy has no character model** to
   draw. The engine demonstrably knows how to render a detached camera and demonstrably chooses to
   drop the first-person layer when it does. If displacing the view origin trips the same or a
   neighbouring path, the HUD loss is the engine working as designed. See the companion Photo Mode
   topic.
2. **The address is read by game code, not only by the renderer.** §6h notes the value sits in an
   **image region — static data, not heap**. If gameplay or UI logic also consumes it (weapon
   placement, "what is the player looking at", HUD population), then writing it does more than
   redirect the camera, and the HUD stops being *populated* rather than being culled. This would
   make the address more powerful than §6h currently claims, and correspondingly more dangerous.

The two are distinguishable by a single observation, and it is one the project is already going to
be in a position to make.

## Why this is worth the dossier's attention now

It changes what "fixing the HUD" means. If the cause were culling, the fix would be a rendering fix
— restore the HUD's own view, give it an identity transform, keep it out of the displaced frustum.
The frame breakdown says that fix would be aimed at nothing, because the HUD was never in the
frustum to begin with.

If the cause is state, the fix is elsewhere entirely: either find the flag the engine sets and hold
it, or — much more promising — **displace the camera at a point downstream of whatever reads the
value for game purposes**, which is exactly what the per-draw GPU copies in §6f are. §6f and §6h
would then not be rivals but a **division of labour**: write §6h's global when you want the engine
to know the camera moved, write §6f's per-draw copies when you want only the picture to move. For
stereo, "only the picture moves, and differently per eye" is precisely the requirement.

## Honest caveats

- The frame breakdown is a capture of a **2016-era build**, not our `20240321`. Pass structure is
  unlikely to have been rewritten, but it is not our build.
- The study describes the **OpenGL** renderer; we are on the **Vulkan** executable. These are
  separate build configurations (§11). The pass *structure* is engine-level and should carry over,
  but that has not been confirmed against a Vulkan capture.
- The Photo Mode mechanism is `[reported]` from community sources and games-press coverage; nobody
  has confirmed what Photo Mode does to the HUD on our build.
- Nothing here is measured by us. It is a reading that **excludes** one explanation on good evidence
  and proposes two others.

## Concrete next steps, cheapest first

1. **One observation settles most of it, and it needs no code:** enter Photo Mode, and see whether
   the HUD and weapon disappear the same way they do under our displacement. If they do, the engine
   is doing this on purpose and we are riding a designed path rather than breaking one.
2. **Displace by a small amount and check whether the HUD *degrades* or *vanishes cleanly*.** A
   clean, instantaneous disappearance at any non-zero delta says "state flag". A progressive loss
   says something geometric after all, and this whole topic needs revisiting.
3. **Then test the division of labour:** hold §6f's per-draw copies displaced while leaving
   §6h's global untouched, and see whether the world moves while the HUD survives. If it does,
   that is the stereo write path — and the HUD problem is solved by choosing the right one of two
   control points we already have, rather than by fixing anything.
4. When Phase 2 opens properly, the study is the reference to read alongside a **Vulkan** RenderDoc
   capture, not instead of one.

## Sources

- [Adrian Courrèges, *DOOM (2016) — Graphics Study*](https://www.adriancourreges.com/blog/2016/09/09/doom-2016-graphics-study/)
  — pass order, the first-person weapon in the depth pre-pass, the separate LDR UI render target and
  its late composite, the velocity buffer and TAA sub-pixel jitter
- Companion topic: [DOOM 2016 ships a real, retail, ungated Photo Mode whose camera detaches from the player](2026-09-01-retail-photo-mode-is-a-native-detached-camera.md)
- [DOOM has a gory new photo mode, here's how to use it — Critical Hit](https://www.criticalhit.net/gaming/doom-has-a-gory-new-photo-mode-heres-how-to-use-it/)
  (DOOM Guy has no third-person character model)
