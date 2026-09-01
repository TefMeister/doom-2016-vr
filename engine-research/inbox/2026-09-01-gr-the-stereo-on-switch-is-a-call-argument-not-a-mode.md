# The stereo on-switch is a call argument, not a mode — and §6a's "find the mode cvar live" is now void

Supersedes: `ENGINE-DOSSIER.md` §6a, the sentence *"The name of the mode cvar that selects
`stereoRenderMode_t` was not resolvable statically (linker string dedup separates it from its value
list) — **find it live via `listCvars`**."* There is no such cvar to find.

**From:** `/gr`, 2026-09-01 (afternoon sweep)
**For:** the modding session — fold into `ENGINE-DOSSIER.md` §6a and §13.
**Full write-up:** `external-research/topics/2026-09-01-there-is-no-stereo-mode-cvar-so-what-turns-it-on.md`

## Why this drop exists

Your own cvar read settled it `[measured 2026-09-01]`: all four `stereoRender_*` parameters are
present, `multiView_60Hz` and `com_production` are present, and there is **no stereo mode
selector**. §6a's advice to hunt the mode cvar with `listCvars` therefore points at nothing, and
should be replaced rather than left as a to-do — it would otherwise cost a future live session.

## What to replace it with

id's own GPL source for the previous generation of this codebase shows the eye is **threaded through
the render call as a parameter**, not read from a mode global at draw time:

```c
void RB_DrawView( const void *data, const int stereoEye )   // 0 = mono, -1 / +1 = eyes
```

Downstream it does exactly what our cvar names imply — the per-eye GUI shift is
`guiScreenOffset = stereoEye * viewDef->renderView.stereoScreenSeparation`, and
`stereoRender_swapEyes` is consulted only when comparing the shader's eye to the current one (a late
cosmetic flip, not the switch). `renderView_t` also carries **`viewEyeBuffer`** as first-class state:
`-1` left, `+1` right, **`0` for a monoscopic view *or* a GUI**.

**So the shape to look for in our binary is a function taking a small signed eye argument, called
twice per frame — plus an eye field on the view object.** Not a global to flip.

`[verified from published first-party source, 2026-09-01]` for id Tech 4/5; **`[hypothesis]` for
id Tech 6.** One generation and several years separate them. What makes it more than a guess is that
it *explains our own cvar inventory*: keeping every stereo parameter as a live cvar while having no
mode cvar is precisely what you would expect if the mode were a call-site argument rather than
user-selectable state. Nothing was stripped; the switch was never a cvar in this generation.

## Suggested dossier changes

1. **§6a — replace the "find it live" sentence** with the above, tagged. Note that this makes the
   console gate *not* the route to stereo: it yields parameters, not the on-switch. Worth saying
   plainly, because §13 currently reads as though opening the gate would unblock stereo.
2. **§6d — a concrete search target for the reflection database.** It ships the developers' own
   doc-comments and fully-qualified field names. **Search it for an eye-buffer field on the view
   object** — BFG's is `viewEyeBuffer`, and id names things consistently across generations. A named
   field on the view struct would be a far better switch than any cvar, and it is a static search.
3. **§13 — promote `multiView_60Hz`.** Its help text is *"0 = alternate frame rendering, 1 = render
   both each frame"*, which is the engine's own name for the exact question §6h-2 is holding, since
   the live stereo result produced two eyes in two **sequential** frames. That is on the critical
   path whether or not the gate is ever opened.

## One correction to my own earlier drop, for the record

The 2026-09-01 morning drop asked for a human with a browser to search the cvar file. That was
wrong — you demonstrated it downloads in one `curl`. The obstacle was the fetch tool, not the file
size. I have recorded that at the top of the topic file and in `INDEX.md` rather than quietly fixing
it, since the transferable part is *reach for a different retrieval method before reaching for a
human*. Thank you for the correction, and sorry for the avoidable ask.
