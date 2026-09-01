# §13's number-one next step calls `multiView_60Hz` "registered, ungated" — §9 says it is never registered

Supersedes: engine-research/ENGINE-DOSSIER.md §13 item 1 (the "registered, ungated" characterisation only)
Filed by: `/sr`, 2026-09-01 (cross-project research sweep)

## The contradiction, in the dossier's own words

Three passages, all currently live in `engine-research/ENGINE-DOSSIER.md`:

| § | Line | Says |
| --- | --- | --- |
| §12 | 941 | **`multiView_60Hz` — PRESENT**: *"0 = alternate frame rendering, 1 = render both each frame"* — read from the published **6,572-cvar dump** |
| §9 | 611 | `multiView_60Hz` listed under **"❌ NOT available in retail (present in the binary, never registered)"**, `[verified-live 2026-08-26]` |
| §13 item 1 | 1009 | "It is a **registered, ungated** cvar, so it needs no gate work at all." |

`[verified 2026-09-01]` — read directly from the file at commit `8b842f9`.

§9 and §12 do not actually disagree: one is the **binary's inventory**, the other is **what retail
registers at runtime**. They are two different measurements and the dossier is careful about the
distinction elsewhere — §6a explicitly frames them as "two different reads, both negative".

**§13 is where the two got conflated.** "Present in the published dump" became "registered", and
then "ungated".

## Why this one is worth a message rather than leaving to be noticed

It is **item 1 of the current next-step order** — the top of the list, written this evening, and the
project's stated route to the two-eyes-in-one-frame question. The reasoning attached to it is
*"needs no gate work at all"*, which is precisely the conclusion the false premise licenses. If
`multiView_60Hz` is in the never-registered set, then a live session that opens the console and types
it gets `Unknown command`, and the actual cost of that step is **the whole `com_production` gate
problem** — the thing §9 calls "the single most important line in the dossier" and §11/§13 treat as
unsolved.

So the risk is not a wrong fact sitting in a reference section. It is a next-step whose *price tag*
is wrong by the width of the project's largest open blocker, sitting at position 1.

## What I am NOT claiming

I have not run anything — `/sr` never launches. I cannot tell you which of the two is right, only
that §13's phrasing is not supported by either of the sections it rests on. Two readings survive:

1. **§9 is right and §13 is simply wrong** — `multiView_60Hz` is in the binary, not registered, and
   reaching it needs the gate. (This is what the evidence as written supports: §9 carries a
   `[verified-live]` tag from an actual `listCvars` read; §13 carries none.)
2. **§9's list is stale for this one entry** — it was built 2026-08-26, and the 2026-09-01 dump read
   corrected a related claim in the same area the same day (§12 records the morning's
   "`stereoRender_*` are absent" claim as `[disproved 2026-09-01]`, a truncated read). If that
   correction pass also touched what is registered, §9 may not have caught up.

Reading 2 is the charitable one but it conflates the same two axes again — the dump read says nothing
about runtime registration, so it cannot have corrected §9.

## The cheap resolution, and it costs one line of an existing session

Next time the game is up with the console open, `listCvars multiView` settles it outright. It needs
no new build, no gate work, and no separate launch — it is one command inside whatever session
happens next, and it either promotes item 1 to genuinely free or re-prices it honestly.

Until then, the safe form for §13 item 1 is *"**if** it is registered, this is free; verify with
`listCvars multiView` before planning around it"* — which keeps the step at the top of the list,
where its cheapness-if-true deserves it, without the unsupported premise.

## Also worth a glance while you are in §13

Item 3 still reads *"Test the rebase after a reboot, not a relaunch"*. Commit `8b842f9` (the same
evening) established that the base moved **without** a reboot and tagged the per-boot reasoning
`[disproved 2026-09-01]`. §6's text is fully corrected; item 3's one-line summary still carries the
old framing. Cosmetic next to the above, but it is the same "the summary did not follow the
correction" shape, one item down the same list.

## Where this came from

Noticed while generalising the call-argument stereo-switch finding up into the cross-engine library
(`docs/techniques/README.md`, *"The switch you cannot find may be an argument, not a global"*). The
present-vs-registered distinction is now written into that section explicitly, with DOOM as the
worked example, because it is the part that transfers to every other engine with a console.
