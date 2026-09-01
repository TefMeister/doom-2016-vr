# The sibling engine's console gate has a *launch-option* name — `+com_allowconsole 1` is worth one test

**From:** `/sr` cross-project sweep, 2026-09-01 (dev PC)
**For:** the modding session — a cheap addition to §13's "still open" list and §11's gate entry.
**Confidence:** `[reported]` — established for **id Tech 5**, not for id Tech 6. Untested here.

## The finding

While generalising this project's console-gate work, the sweep checked whether the same gate shape
appears elsewhere in the estate. On **id Tech 5** — The Evil Within, one generation earlier in the
same lineage — the developer console is opened by a **launch option**:

```
+com_allowconsole 1
```

…after which the console opens (on `Insert` there), and `noclip`, `God`, `g_stoptime` and
`devmapjump` all work. Multiple independent mainstream sources agree, and it needs **no mod and no
developer mode**.

## Why it is worth one test on DOOM 2016

§4a established that retail boots with `idLib::SetProduction( PROD_PRODUCTION )` and Cheat Mode off,
that `com_production` is itself not registered, and that the console therefore cannot be widened from
inside itself. §13 keeps two launch-time probes open — the `.cfg` + `exec` route and
`+devMode_enable 1`.

**`com_allowconsole` is a third candidate, and it is better-shaped than either**, because it is a
name from **this engine's own family** rather than a community guess, and because it is applied at
**launch time** — before the process can guard itself, which is the pattern this library already
records as beating in-process attempts at gates.

It costs one line in the existing launch script and one `listCvars` afterwards. If it does nothing,
that is a two-minute negative; if it does something, it is a route that needs no third-party tool at
all.

## How to run it so the result actually means something

Per this project's own standing rules, which it earned the hard way:

1. **Read `listCvars` / `listCmds` counts before and after.** The retail baseline is **171 / 40**
   `[verified-live 2026-08-26]`. A changed count is the unambiguous positive; "the console feels
   different" is not.
2. **Change one thing.** Do not combine it with `+devMode_enable 1` in the same launch, or a positive
   cannot be attributed to either.
3. If the count moves, immediately check **`listCvars stereo`** and `com_production` visibility —
   that is the question the gate work actually exists to answer.

## Related, same day

A separate `/gr` drop this session covers the public tool that re-adds the whole hidden interface
without dev mode, and the published command list confirming `rp` and `setviewpos` are real. **These
are different routes to the same door and should be tried cheapest-first: this one needs nothing
installed.**

Sources: [PC Gamer](https://www.pcgamer.com/the-evil-within-debug-console-commands-detailed-god-mode-is-in/) ·
[DSOGaming](https://www.dsogaming.com/news/the-evil-within-console-commands-revealed-unlock-framerate-slow-down-time-enable-god-mode/) ·
[The Evil Within Wiki](https://theevilwithin.fandom.com/wiki/Console_commands)
