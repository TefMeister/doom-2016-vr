# A launch-argument `bind` skips two of the three checks on the ⭐⭐ view-position row

**From:** `/gr` (estate sweep, 2026-09-10) · **For:** the modding lane, `ENGINE-DOSSIER.md` §11
(launch options) and the board's ⭐⭐ `[FLAT]` row.
**Topic:** `external-research/topics/2026-09-10-the-bind-persistence-question-can-be-sidestepped-with-a-launch-argument.md`

## The dead end this addresses

The board's ⭐⭐ row lists three ordered checks on the prepared `bind "F9" "getviewpos"` edit to
`DOOMConfig.local`: does the engine accept `bind` in that file at all (it shipped with **zero** bind
lines); does the bind survive the config rewrite on exit; does `condump` capture the output with the
console hidden.

## Two things public sources say

**1. ⚠️ There is a SECOND revert path the row does not list: Steam Cloud** `[reported 2026-09-10]`.
DOOM 2016's settings-not-saving threads name Cloud sync alongside file permissions as a cause of
hand edits coming back changed. A bind lost to Cloud looks **identical** to a bind the engine
rejected, so checks #1 and #2 would both read "failed" for a third reason that is neither. If the
file route is tested at all, **disable Steam Cloud for DOOM first** or the test cannot distinguish
its own outcomes. (The read-only trick is stated as a mechanism by one poster but nobody reports it
actually preserving a hand-added line — not a recipe.)

**2. ⭐ Suggested §11 addition — `+bind` on the command line makes the persistence question moot**
`[hypothesis]`. §11 already carries **`+com_allowconsole 1`** as a launch option. That is the id Tech
`+<command> <args>` mechanism, so the same parser should take:

```
+bind "F9" "getviewpos" +bind "F10" "condump viewpos.txt"
```

Applied per launch, nothing has to survive anything: **check #1 becomes irrelevant** (the file is
never touched) and **check #2 disappears** (with the Cloud confound). Only check #3 is left, and it
is the one that genuinely needs the game. It also leaves no edit behind to clean up.

Honest about the premise: §11's own `+com_allowconsole 1` entry is marked **UNTESTED** there, so
this rests on an untested assumption. But it costs the same single launch the file route costs and
settles strictly more. And if `+bind` is rejected, the row's own fallback is already available —
`type getviewpos`, since `AT_POSTCHAR` posts `WM_CHAR` and is the default route
`[verified-numerically 2026-09-09]`.

## Suggested board/dossier change, in one sentence

Reorder the ⭐⭐ row to try `+bind` first and keep the file edit as the fallback, and add Steam Cloud
to §11 as a known confound for any config-file experiment on this game.
