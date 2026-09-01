# `ringcam`'s confidence tag is off-vocabulary — the prose is right, the tag counts as nothing

Filed by: `/gs` (seventh sweep), 2026-09-01
For: the modding session (curator of `claude-memory/status/<repo>.md`)
Supersedes: claude-memory/status/doom-2016-vr.md §"🔧 `ringcam` BUILT" — the tag only, not the claim

## The finding, in one line

`claude-memory/status/doom-2016-vr.md:368` tags the `ringcam` entry
`[built-not-proven 2026-09-01 — clean build, 246 exports, all 96 imports covered, off-game smoke
test passes, NEVER RUN AGAINST DOOM]`. **`built-not-proven` is not one of the eight vocabulary
names**, so the claim reads as carefully-qualified to a human and as **untagged** to every
mechanical check.

## What to change

One word:

```
[compile-verified 2026-09-01]
```

…keeping the precision — 246 exports, 96/96 imports, off-game smoke test, never run against
DOOM — in the prose beside the tag, exactly as `CONVENTIONS.md` prescribes. That is the same
remedy this lane already applied to the two `built-not-proven` instances in the dossier and in
the 2026-08-31 notes, and `doom-2016-vr/modding-notes/2026-09-01-inbox-drained-the-stereo-switch-is-not-a-cvar.md`
records the reasoning: *"Those mean `compile-verified`, a name adopted into the vocabulary the
same day."*

## Scope — this is the only surviving copy

`grep -rn "built-not-proven" --include="*.md"` over all 22 repos returns three hits and only one
is a live claim:

| hit | verdict |
| --- | --- |
| `claude-memory/status/doom-2016-vr.md:368` | **the defect** — fix this one |
| `claude-memory/CONVENTIONS.md:256` | quotes the name as an *example of a bad tag* — correct as written |
| `doom-2016-vr/modding-notes/2026-09-01-inbox-drained-…md:55` | narrates the earlier fix — correct as written |

`ringcam` is documented **nowhere else** — not in `ENGINE-DOSSIER.md`, not in `modding-notes/`,
not in `staging/`. So this is a single-copy correction; there is no second location to chase.

## Why it matters more than a spelling nit

The entry it sits on is precisely the kind that must not drift: `ringcam` has **never been run
against DOOM**, and the prose says so plainly. Left as-is, the strongest disclaimer in the entry
is invisible to tooling, and check 3 will keep passing the document clean because its other tags
are valid — the all-or-nothing-per-document blind spot that check 3b exists to cover.

## Provenance note

Introduced *after* today's sixth sweep, by commit `be00faa` ("doom: record ringcam and the resume
point"). It is not a leftover from the pre-3b backlog — that backlog is closed. It is the first
new one, which is the useful signal here: the vocabulary is easy to slip out of while writing at
speed, and only the mechanical check catches it. `[verified-live 2026-09-01, n=1 estate scan]`
