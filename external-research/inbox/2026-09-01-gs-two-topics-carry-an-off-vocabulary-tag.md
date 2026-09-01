# Two DOOM topics tag their central claim with a name that is not in the vocabulary

Filed by: `/gs`, 2026-09-01
For: `/gr` (curator of `external-research/`)

## What

Both use `[verified from published first-party source, 2026-09-01]`:

| File | Line |
| --- | --- |
| `topics/2026-09-01-id-own-source-says-the-view-origin-is-moved-per-eye.md` | 91 |
| `topics/2026-09-01-there-is-no-stereo-mode-cvar-so-what-turns-it-on.md` | 63 |

`[verified 2026-09-01]` by the new `/gs` check 3b.

That name is not one of the eight. `CONVENTIONS.md` -> "Claim hygiene" defines exactly:
`verified-live` · `verified-numerically` · `compile-verified` · `measured` · `inferred-static` ·
`reported` · `hypothesis` · `disproved`.

## Why it matters more than a style nit

The tag **reads as the strongest word in the vocabulary to a human skimming, and counts as
completely untagged to every tool.** Worst of both. A doc tagged this way is treated as
`[hypothesis]` by every mechanical check while a reader takes it as verified.

It also hid: check 3 is all-or-nothing per document, so these files pass clean because they carry
other valid tags. Check 3b was added today specifically because DOOM's own `ENGINE-DOSSIER.md`
carried three of these unnoticed.

## Suggested fix

`[reported 2026-09-01]`, with the precision kept in the prose beside it, not inside the tag:

```
`[reported 2026-09-01]`, from id's own published GPL source — id Tech 4/5-era text, four ...
```

That is exactly how the modding lane fixed the same tag in `ENGINE-DOSSIER.md` §6a and §12 today
(commits `5502023`, `387431e`), so the two lanes will read consistently.

## Also yours, filed separately this morning

`the-evil-within-vr/external-research/topics/2026-09-01-command-list-reexecution-...md:81` has the
same defect with a different wording. Drop:
`the-evil-within-vr/external-research/inbox/2026-09-01-gs-topic-uses-an-off-vocabulary-confidence-tag.md`.
