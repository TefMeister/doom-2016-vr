# The HUD cannot be vanishing for a rendering reason — the obvious explanation is ruled out

**From:** `/gr doom-2016-vr`, 2026-09-01 (dev PC)
**For:** the modding session — fold into `ENGINE-DOSSIER.md` §6h and §13.
**Full write-up:** `external-research/topics/2026-09-01-why-the-hud-and-weapon-vanish-under-view-displacement.md`

## The dossier text this targets

§6h, "What is NOT established": *"Why the HUD and weapon drop out under displacement at all. A VR
camera that costs the HUD is not finished."* §13, item 4, carries the same question.

## What the evidence rules out

Adrian Courrèges' frame-by-frame graphics study of a real DOOM 2016 capture is precise about where
these two elements live:

- **The UI is drawn to its own render target** — *"a different render-target, in premultiplied alpha
  mode stored in LDR format"*, deliberately decoupled so post-processing can be applied to all
  widgets at once — and it is **composited last**, *"blended on the top of the game frame"* during
  the final film-grain pass.
- **The first-person weapon is in the depth pre-pass**, drawn first — *"first the player's weapon,
  then static geometry and finally dynamic geometry"* — as dynamic geometry with per-pixel velocity
  written for TAA and motion blur, under the standard world projection.

**Therefore the HUD cannot be culled by moving the world camera.** A screen-space overlay composited
after the world is finished is not in the world frustum. Whatever displacing `globalViewOrigin`
does, it is not removing the HUD geometrically. The weapon is the ordinary case and needs no exotic
explanation — it is in the world pass, so a displaced camera plausibly puts it out of frame or
behind the near plane.

## The hypothesis that leaves `[hypothesis, /gr 2026-09-01]`

The HUD loss is a **game-state response**, not a rendering consequence. Two candidates:

1. **The engine has a first-class "the view is not the player's" state that suppresses first-person
   elements.** Not speculation about a hypothetical — DOOM 2016 ships **Photo Mode**, which detaches
   the camera, hides the HUD, and leaves the player invisible with **no character model at all**.
   The engine demonstrably knows how to render a detached camera and demonstrably drops the
   first-person layer when it does. See the companion Photo Mode drop.
2. **The address is read by game code, not only by the renderer.** §6h notes it sits in an **image
   region — static data, not heap**. If gameplay or UI logic also consumes it, writing it does more
   than redirect the camera, and the HUD stops being *populated* rather than being culled. That would
   make the address more powerful than §6h currently claims, and correspondingly more dangerous.

## Why this is worth acting on

It changes what "fixing the HUD" means. A culling explanation would point at a rendering fix —
restore the HUD's own view, keep it out of the displaced frustum — and the frame breakdown says that
fix would be aimed at nothing.

If it is state, the more promising route is to **displace the camera downstream of whatever reads the
value for game purposes** — which is exactly what §6f's per-draw GPU copies are. §6f and §6h would
then not be rivals but a **division of labour**: write §6h's global when the engine should know the
camera moved; write §6f's per-draw copies when only the picture should move. **"Only the picture
moves, and differently per eye" is precisely the stereo requirement.**

## Suggested next steps, cheapest first

1. **Enter Photo Mode and see whether the HUD and weapon disappear the same way.** No code. If they
   do, the engine is doing this on purpose and we are riding a designed path rather than breaking one.
2. **Displace by a small amount and watch how the HUD goes.** A clean disappearance at any non-zero
   delta says "state flag". A progressive loss says something geometric after all, and this whole
   reading needs revisiting.
3. **Test the division of labour:** hold §6f's per-draw copies displaced while leaving §6h's global
   untouched. If the world moves and the HUD survives, that is the stereo write path — and the HUD
   problem is solved by choosing correctly between two control points we already have, rather than
   by fixing anything.

## Caveats to carry with the claim

The study captures a **2016-era build**, not our `20240321`, and describes the **OpenGL** renderer
while we are on the **Vulkan** executable (separate build configurations, §11). Pass *structure* is
engine-level and should carry, but that is not confirmed against a Vulkan capture. The Photo Mode
mechanism is `[reported]`. Nothing here is measured by us — it **excludes** one explanation on good
evidence and proposes two others. When Phase 2 opens properly, the study is the reference to read
**alongside** a Vulkan RenderDoc capture, not instead of one.
