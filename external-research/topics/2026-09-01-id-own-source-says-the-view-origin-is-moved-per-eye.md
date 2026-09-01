# id's own GPL source says the view origin *is* moved per eye — which complicates the dossier's "two identical centered views" caveat

**Supersedes:** `ENGINE-DOSSIER.md` §6a (the "the two stereo world views are both centered between
the eyes ⇒ separation is applied downstream, not as two different view matrices" caveat) and the
same claim as republished in `flat-to-vr-cross-engine-research/docs/case-studies/id-tech-6-dormant-stereo.md`
§"The caveat that matters most".

**Status:** 🆕 new · **Priority:** high — this bears directly on `ENGINE-DOSSIER.md` §12's open risk
*"Two identical centered views (§6a) means separation happens downstream… good enough for comfort-3D,
not automatically good enough for 6DOF"*, and on where §6h's control point sits in the pipeline.

## The claim being corrected

The dossier reads a doc-comment compiled into DOOM 2016's binary — *"there will be two unique
\[world views] in split-screen multiplayer and two identical ones in stereo-3D (both centered
between the eyes)"* — and draws this conclusion:

> Separation is applied **downstream** of view setup (projection/screen-space skew), not as two
> different view matrices… our per-eye override probably belongs at the **projection** stage.

That reading was careful and reasonable. It is also, on the evidence of id's own published source
for the previous generation of the same code, **at best half of the picture**.

## What id's published source actually says

`neo/renderer/RenderWorld.h` in **id Software's own GPL release of Doom 3 BFG Edition** —
first-party primary source, not a decompilation — declares `renderView_t` with these fields and
these comments, quoted verbatim:

```c
float    fov_x, fov_y;              // in degrees
idVec3   vieworg;                   // has already been adjusted for stereo world seperation
idMat3   viewaxis;                  // transformation matrix, view looks down the positive X axis
int      viewEyeBuffer;             // -1 = left eye, 1 = right eye, 0 = monoscopic view or GUI
float    stereoScreenSeparation;    // projection matrix horizontal offset, positive or negative based on camera eye
```

Read the first and last comments together. id's stereo path applies **both** halves of a textbook
stereo setup, and they are different things:

| cvar (as named in DOOM 2016's binary) | engine's own help text | what the BFG source shows it doing |
|---|---|---|
| `stereoRender_separation` | "world units from center to eyes" | **moves `vieworg`** — a real per-eye translation of the camera in world space |
| `stereoRender_screenSeparation` | "screen units from center to eyes" | **shifts the projection matrix horizontally** — the convergence / screen-plane term |

So the world-space eye offset is **not** downstream, and it is **not** a skew. `vieworg` — the view
origin, the direct analogue of `globalViewOrigin` — *"has already been adjusted for stereo world
seperation"* by the time the renderer sees it. The projection offset is a **second, complementary**
step for convergence, which is exactly why two separately-named separation cvars exist rather than
one.

`viewEyeBuffer` is worth noting on its own: a single int, `-1` / `+1` / `0`, with **0 meaning
monoscopic view *or* GUI**. If id Tech 6 inherited that field, there is a one-integer eye selector
somewhere near the camera state, and the GUI is explicitly a first-class citizen of the same enum.

## The corroboration from the sibling engine

Independently: **Helifax** (Octavian Vasilov, author of Vk3DVision) built a **full 6DOF VR mod for
DOOM Eternal** — id Tech 7, the direct successor — and the technique, as described publicly by
Flat2VR, is *"synced eye, single pass, stereo instancing."*

Single-pass stereo instancing renders both eyes in one draw by indexing **per-eye view-projection
matrices** from the instance ID. It cannot be done with one shared centered view and a screen-space
shift; it requires two genuinely different per-eye view matrices. That someone achieved it on the
next generation of this same engine family is evidence that per-eye *view* transforms are the
natural seam here, not an exotic one.

## Why this matters for §6h specifically

§6h established that writing the twelve floats at `DOOMx64vk.exe + 0x360F6B0` — origin plus
orthonormal basis, the `globalViewOrigin` / `Fwd` / `Left` / `Up` quartet — moves the view and the
world renders correctly from it.

On this reading, **that is precisely the lever id's own stereo code uses.** `stereoRender_separation`
adjusts `vieworg`; §6h adjusts `globalViewOrigin`. A per-eye IPD offset along the basis's `left`
vector is the same operation the engine performs on itself when its stereo path runs. The control
point already found is not a workaround for the absence of a stereo path — it is the stereo path's
own input, reached from a different direction.

The pessimistic §12 risk — *"a pure screen-space/projection-skew trick gives correct stereo but not
correct per-eye positional geometry"* — looks materially less likely than it did. Correct per-eye
positional geometry appears to be what this lineage was built to produce.

## The tension, flagged rather than resolved

**Neither source disproves the other, and this is not being written up as settled.**

- Our binary's own doc-comment really does say *"two identical ones in stereo-3D (both centered
  between the eyes)"* `[inferred-static, 2026-08-26]`. That is DOOM 2016's text, about DOOM 2016.
- BFG's source really does say `vieworg` *"has already been adjusted for stereo world seperation"*
  `[verified from published first-party source, 2026-09-01]`. That is id Tech 4/5-era text, four
  years and one engine generation earlier.

Plausible reconciliations, none of them established: the DOOM 2016 comment may describe the
*world-view list as constructed*, before per-eye adjustment is applied to each; it may be stale
commentary carried forward with the code; or id Tech 6 may genuinely have simplified the path. It
may also simply describe views that are centered *and then* offset, with "identical" meaning "of
the same scene" rather than "of the same camera".

**Same shape as the `devMode_enable` tension already on record** (topic, 2026-08-27), and it gets
the same treatment: both readings kept, both tagged, resolved by measurement rather than argument.

## Prior-art status update — one thing changed since 2026-08-25

The [Vk3DVision topic](2026-08-25-stereo-3d-prior-art-vk3dvision.md) recorded that project as
"actively maintained". That is no longer true: **the `helifax/Vk3DVision-Public` repository was
archived by its owner on 2026-03-05 and is now read-only**, with **4.25.5** as the final release.
The maintained fix list still shows DOOM (2016) last updated **2025-08-30** and DOOM Eternal's
separate **"Virtual Reality ver. 0.90"** package last updated **2024-08-30**.

Two things follow. The feasibility proof still stands — per-eye override at the Vulkan level
demonstrably works on this exact title. But there will be **no future fixes**, so nothing about this
project's plan should assume the tool keeps pace with anything. And the split is now explicit and
worth recording: on **id Tech 6 / DOOM 2016 the public prior art is stereo-only**; the **6DOF VR
package exists only for DOOM Eternal on id Tech 7**. The long-open "does Vk3DVision's FullVR do real
head tracking" question resolves, for our game, to **no** — the VR variant was never made for it.

## Concrete next step

The cheapest test of this whole topic needs the console gate opened (see the DOOMLegacyMod topic
from the same day), and then costs one command: **`rp viewMatrixX` before and after a
`stereoRender_separation` change**, or simply reading `globalViewOrigin` with `stereoRender_enable`
set. If the world origin moves per eye, the BFG reading holds for id Tech 6 and the per-eye override
belongs at the **view** stage — where §6h already has a working control point. If only the
projection changes, the dossier's original caveat was right and the override belongs at the
projection stage after all.

Until that is measured, **write both readings into the dossier side by side and build the per-eye
offset at the view stage anyway** — because §6h has already proved that writing there works, and the
projection route has not been tried at all.

## Sources

- [id-Software/DOOM-3-BFG — official GPL source release](https://github.com/id-Software/DOOM-3-BFG)
  — `neo/renderer/RenderWorld.h` (`renderView_t`), `neo/renderer/RenderSystem_init.cpp`
  (`stereoRender_enable`, `stereoRender_swapEyes`, `stereoRender_deGhost`, and the six-mode
  `STEREO3D_*` enum)
- [Flat2VR — sneak peek at Helifax's DOOM Eternal 6DOF VR mod](https://x.com/Flat2VR/status/1704495949978984506)
- [Upcoming DOOM Eternal VR Mod by Helifax — YouTube](https://www.youtube.com/watch?v=6Z-LGvDUlv8)
- [Vk3DVision-Public — GitHub releases (archived 2026-03-05, final 4.25.5)](https://github.com/helifax/Vk3DVision-Public/releases)
- [VK3DVision Game Fixes list — 3dsurroundgaming.com](https://3dsurroundgaming.com/Vk3DVisionGames.html)
