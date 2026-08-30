# Public precedent for `devMode_enable` — in tension with the dossier's fatal-error caution

**From:** `/gr doom-2016-vr` research session, 2026-08-27
**Targets:** `ENGINE-DOSSIER.md` §4a ("`devMode_enable` IS A TRAP") and §13 next-step #1 (the
`.cfg`+`exec` gate-bypass probe).

## The dossier dead end this answers

§4a reads `devMode_enable` = `0` and its neighbor `devMode_fatalErrorOnEnter` = `1` by default
(*"FatalError rather than enter Dev Mode"*), and correctly stopped short of testing further.
§13's next steps list a `.cfg`+`exec` probe as the cheap way to test whether the production-mode
gate can be bypassed at all.

## What research found

Multiple independent public sources (2016–2020: a Steam Community guide "UPDATED 2020" with dated
user comments, Shacknews' launch-week guide, and several Steam discussion threads) describe
`devMode_enable 1` as a **routinely used, non-fatal** unlock for other players — including a
documented **`+devMode_enable 1` command-line launch option** (distinct from typing it into the
live console), and a real but non-fatal side effect: the save gets cheat-flagged and Steam Cloud
sync can make it look "corrupted" on reload (fixable by disabling Cloud sync + clearing the save
folder — which deletes all saves, so back up first). No source found reports a crash, hang, or
process termination from setting it.

**This is genuinely in tension with the dossier's own live reading**, not a simple confirmation —
the public sources predate the current build (`20240321-...`) by years, so either a tripwire was
added later, or `devMode_fatalErrorOnEnter` gates something narrower than it looks. Full writeup,
sourcing, and a safety-ordered test plan (launch-option route first, on a throwaway save, before
any interactive console flip) in
[`doom-2016-vr-external-research/topics/2026-08-27-devmode-enable-public-precedent-and-the-fatal-error-tension.md`](https://github.com/TefMeister/doom-2016-vr-external-research/blob/main/topics/2026-08-27-devmode-enable-public-precedent-and-the-fatal-error-tension.md).

## Suggested dossier change

If a live test confirms or denies this, update §4a/§11 with the result either way (it's currently
the biggest open question standing between the project and knowing whether `stereoRender_*`/
`com_production` are merely hidden or never constructed). If it works, the very next check should
be `listCvars stereo` and `com_production`'s visibility — no public source addresses that part.
