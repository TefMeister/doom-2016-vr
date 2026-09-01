# Inbox drained: §6a's "find the mode cvar live" was pointing at nothing

**Date:** 2026-09-01 (evening) · **Game was NOT launched. Nothing here was run.**

Two `engine-research/inbox/` drops folded in and deleted. One of them withdrew a live instruction
in the dossier that would have cost a future in-game session.

## What was wrong

§6a told the next live session:

> "The name of the mode cvar that selects `stereoRenderMode_t` was not resolvable statically
> (linker string dedup separates it from its value list) — **find it live via `listCvars`**."

**There is no such cvar.** `[disproved 2026-09-01]` Our own full cvar read settled it
`[measured 2026-09-01]`: all four `stereoRender_*` parameters are present, `multiView_60Hz` and
`com_production` are present, and nothing selects `stereoRenderMode_t`.

The sharp part: **the same dossier already recorded the disproof** in §9 and §12 (`listCvars stereo`
returns nothing selecting the enum, so it is "not a cvar at all"). §6a and §12 contradicted each
other, and §6a is the section a session reads when planning stereo work. A reader following the
document front-to-back would have taken the instruction before reaching the retraction.

## What replaces it

The switch is a **call argument, not a mode**. id's published GPL source for the previous
generation threads the eye through the render call — `RB_DrawView( ..., const int stereoEye )`,
`0` mono / `-1` / `+1` — and `renderView_t` carries `viewEyeBuffer` as first-class state.
`[reported 2026-09-01, from id's own published GPL source]` for id Tech 4/5, `[hypothesis]` for
id Tech 6.

It is more than a guess because **it explains our own cvar inventory**: every stereo parameter
live as a cvar while no mode cvar exists is exactly what a call-site argument looks like. Nothing
was stripped; the switch was never a cvar in this generation.

**Consequence, written into §6a, §11 and §13:** opening the console gate yields stereo
*parameters*, **not the on-switch**. The gate is no longer on the critical path to stereo.

## What is NOT established

- The id Tech 6 half is `[hypothesis]`. One generation and several years separate BFG from this
  build. The reflection-database search (§6d) is what would upgrade it, and it is static.
- `+com_allowconsole 1` (§11, via `/sr`) is `[reported]` for **id Tech 5 only** and untested here.
- Nothing was launched, measured or built in this session. This is a documentation correction.

## Also corrected while here

Three tags in this dossier used the invented name "verified from published first-party source",
which is **not in the vocabulary**, so every mechanical check read those claims as untagged.
Replaced with the `reported` tag plus a date, keeping the precision in the prose beside it rather
than inside the tag.

**Update, later the same day.** The remaining two were fixed as well — §6e's undated
`verified-live` and §12's "verified from published source" — and the new `/gs` check 3b
then found **two more** ("built-not-proven", here and in the 2026-08-31 notes) that a hand-grep
had missed. Those mean `compile-verified`, a name adopted into the vocabulary the same day. This
dossier now passes check 3b. The lesson is the plain one: a hand-check for two known-bad strings
found two; the mechanical check found four.
