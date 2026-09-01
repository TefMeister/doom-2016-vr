# Correction: id's own source says stereo separation *does* move the view origin per eye

**Supersedes:** `ENGINE-DOSSIER.md` §6a — the caveat reading *"the eye separation is applied
downstream of the view setup (a projection skew / screen-separation step), not by building two
different view matrices… our per-eye override probably belongs at the projection stage, not the view
stage"* — and the §12 open risk built on it.

**From:** `/gr doom-2016-vr`, 2026-09-01 (dev PC)
**For:** the modding session — fold into `ENGINE-DOSSIER.md` §6a, §6h and §12.
**Full write-up:** `external-research/topics/2026-09-01-id-own-source-says-the-view-origin-is-moved-per-eye.md`

## The evidence

`neo/renderer/RenderWorld.h` in **id Software's own GPL release of Doom 3 BFG** — first-party
primary source — declares `renderView_t` with these comments, verbatim:

```c
idVec3   vieworg;                   // has already been adjusted for stereo world seperation
int      viewEyeBuffer;             // -1 = left eye, 1 = right eye, 0 = monoscopic view or GUI
float    stereoScreenSeparation;    // projection matrix horizontal offset, positive or negative based on camera eye
```

So id's stereo path applies **both** halves of a textbook stereo setup, and they are different
things — which is exactly why DOOM 2016's binary carries **two** separately-named separation cvars:

| cvar (as named in our binary) | engine's own help text | what BFG's source shows it doing |
|---|---|---|
| `stereoRender_separation` | "world units from center to eyes" | **moves `vieworg`** — a real per-eye world-space translation of the camera |
| `stereoRender_screenSeparation` | "screen units from center to eyes" | **shifts the projection matrix horizontally** — the convergence term |

Corroboration from the sibling engine: **Helifax's DOOM Eternal 6DOF VR mod** (id Tech 7) is
publicly described as using *"synced eye, single pass, stereo instancing"* — a technique that indexes
**per-eye view-projection matrices** from the instance ID and cannot be done with one shared centered
view plus a screen-space shift.

## Why this matters for §6h

§6h writes origin + basis at `DOOMx64vk.exe + 0x360F6B0` — the `globalViewOrigin`/`Fwd`/`Left`/`Up`
quartet — and the world renders correctly from the displaced position.

On this reading **that is the same lever id's own stereo code pulls.** `stereoRender_separation`
adjusts `vieworg`; §6h adjusts `globalViewOrigin`. A per-eye IPD offset along the basis's `left`
vector is the operation the engine performs on itself when its stereo path runs. The control point
already found is not a workaround for a missing stereo path — it looks like that path's own input,
reached from another direction.

§12's pessimistic risk — *"a pure screen-space/projection-skew trick gives correct stereo but not
correct per-eye positional geometry"* — is materially less likely than it looked.

## Suggested dossier change, and how to tag it

**Keep both readings, tag both, do not resolve by argument.** This is the same shape as the
`devMode_enable` tension already handled well in §11:

- our binary's own doc-comment, *"two identical ones in stereo-3D (both centered between the
  eyes)"* — `[inferred-static, 2026-08-26]`, DOOM 2016's text about DOOM 2016;
- BFG's `vieworg` comment — `[verified from published first-party source, 2026-09-01]`, id Tech 4/5
  text, one engine generation earlier.

Plausible reconciliations, none established: the DOOM 2016 comment may describe the world-view list
*as constructed*, before per-eye adjustment; it may be stale commentary carried forward; id Tech 6
may genuinely have simplified; or "identical" may mean "of the same scene" rather than "of the same
camera".

**Practical recommendation for §13:** build the per-eye offset at the **view** stage anyway, because
§6h has already proved writing there works and the projection route has not been tried at all. The
measurement that settles it costs one command once the console gate is open (see the companion
inbox drop): `rp viewMatrixX` before and after a `stereoRender_separation` change.

## One prior-art status change worth recording

`helifax/Vk3DVision-Public` was **archived by its owner on 2026-03-05** and is read-only, final
release **4.25.5**. The fix list still shows DOOM (2016) last updated 2025-08-30 and DOOM Eternal's
separate *"Virtual Reality ver. 0.90"* last updated 2024-08-30. The feasibility proof stands, but
there will be no future fixes. And the split is now explicit: **on id Tech 6 / DOOM 2016 the public
prior art is stereo-only; the 6DOF VR package exists only for DOOM Eternal on id Tech 7.** The
long-open "does Vk3DVision's FullVR do real head tracking" question resolves, *for our game*, to
**no** — that variant was never built for it. §12's "head tracking is still entirely ours to build"
stands, now on evidence rather than absence of evidence.

*A separate correction has been filed to `flat-to-vr-cross-engine-research/inbox/`, because the same
superseded claim is republished in its id Tech 6 case study. That is a different document with a
different owner, not a duplicate of this drop.*
