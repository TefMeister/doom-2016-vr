# There is no stereo MODE cvar — so what actually switches the path on? id's own source says the eye is a *parameter*, not a mode

**Status:** 🆕 new · **Priority:** high — this is the question left standing after the cvar list was
read in full on 2026-09-01. Opening the console gate would give us the stereo path's **parameters**
and not its **on-switch**, and that is a materially different problem from "set a cvar".

## What we now know, and what it leaves open

The complete cvar dump was read on 2026-09-01 (11,103 lines / 6,572 cvars, with a `g_fov` control
proving the read was sound). Result: **all four `stereoRender_*` parameters exist**, so does
`multiView_60Hz` and so does `com_production` — but **there is no mode selector**. `ENGINE-DOSSIER.md`
§6a had recorded that the cvar selecting `stereoRenderMode_t` could not be resolved statically
because of linker string dedup, and advised finding it live. The list says it is **not a cvar at
all** `[measured 2026-09-01]`.

So: what does the on-switch look like?

## The answer id's own source suggests: the eye is threaded through the call, not read from a global

Reading id Software's GPL Doom 3 BFG release — the previous generation of this codebase — the
backend does **not** read a stereo mode at draw time. The eye is a **parameter carried into the
render call**:

```c
void RB_DrawView( const void *data, const int stereoEye )
```

`stereoEye` is **0 in mono, and −1 / +1 for the two eyes**. Downstream it does exactly the two
things the DOOM 2016 cvar names imply:

- the GUI offset is computed per eye from the same view struct —
  `guiScreenOffset = stereoEye * viewDef->renderView.stereoScreenSeparation` (which is what
  `stereoRender_guiOffset`'s help text, *"shift guis so they don't appear at infinity"*, is about);
- `stereoRender_swapEyes` is consulted only at the point of comparing the shader's eye against the
  current one — a late, cosmetic flip, not the switch.

`renderView_t` also carries `viewEyeBuffer` (**−1 left, +1 right, 0 for a monoscopic view *or* a
GUI**), so the eye is first-class state on the view object itself.

**The dispatch loop that calls the backend twice lives upstream of the draw path** — it was not in
the files read this pass, and finding it is the concrete next research step.

## Why this reframes the problem in a *helpful* direction

"Enable a mode" and "call a function twice with a different argument" are very different jobs, and
the second one is the better one to have:

1. **It matches what this project has already proved.** Stereo has now been produced from the
   view-stage address with depth-correct parallax (§6h). That is the same shape as BFG's model —
   per-eye view state, then render — rather than a global mode being flipped somewhere.
2. **It explains the cvar inventory instead of leaving it odd.** id Tech 6 keeping every stereo
   *parameter* as a live cvar while having no *mode* cvar is exactly what you would expect if the
   mode were a **call-site argument** rather than user-selectable state. Nothing has been stripped;
   the switch was simply never a cvar in this generation.
3. **It puts `multiView_60Hz` on the critical path regardless of the console gate.** Its help text —
   *"0 = alternate frame rendering, 1 = render both each frame"* — is the engine's own name for the
   distinction this project is holding right now, since the live stereo result produced two eyes in
   two **sequential** frames. That is a submission-strategy question the library already documents,
   and the engine has an opinion about it.

## What is NOT established

- **The BFG shape is `[reported 2026-09-01]` — from id's own published GPL source — for id Tech 4/5,
  and `[hypothesis]` for id Tech 6.** One engine generation and several years separate them. The cvar
  inventory is consistent with the shape carrying forward; consistency is not proof.
- **The dispatch loop has not been located in either engine.** For BFG it is upstream of
  `tr_backend_draw.cpp`; for DOOM 2016 nobody has looked.
- Whether `multiView_60Hz` is even honoured on a retail build is untested — it is in the gated set.

## Concrete next steps

1. **Research (cheap, next `/gr`):** find BFG's stereo dispatch loop in the published source —
   likely in `RenderSystem.cpp` around the command-buffer execution, or wherever `RB_DrawView` is
   invoked. Knowing what the caller looks like tells the modding side *what to look for* in id Tech
   6's binary: a function taking a small signed eye argument, called twice per frame.
2. **Static (modding side):** the binary ships a reflection database with the developers' own
   doc-comments (§6d). Search it for an eye-buffer field on the view object — BFG's is
   `viewEyeBuffer`, and id names things consistently across generations. A named field on the view
   struct would be a far better switch than any cvar.
3. **Do not treat the console gate as the route to stereo.** It gives parameters. Worth having, but
   the on-switch is elsewhere, and this should be settled before any effort is spent installing the
   unlocker *for stereo reasons specifically*.
4. **Cross-check `multiView_60Hz`'s value against our own AFR-vs-both-eyes decision** when the gate
   question is settled either way.

## Sources

- [id-Software/DOOM-3-BFG](https://github.com/id-Software/DOOM-3-BFG) — `neo/renderer/tr_backend_draw.cpp`
  (`RB_DrawView( const void *data, const int stereoEye )`, the per-eye `guiScreenOffset`, the
  `stereoRender_swapEyes` comparison) and `neo/renderer/RenderWorld.h` (`renderView_t::viewEyeBuffer`)
- Our own cvar-list read, 2026-09-01, recorded in `engine-research/ENGINE-DOSSIER.md` §12 and in the
  inbox hand-off `2026-09-01-mod-cvar-list-read-in-full-stereo-cvars-confirmed.md`
- Companion topic: [id's own source says the view origin *is* moved per eye](2026-09-01-id-own-source-says-the-view-origin-is-moved-per-eye.md)
