# The `bind` persistence question can be sidestepped with a launch argument

**Found:** 2026-09-10 (`/gr`, estate sweep) · **For:** the ⭐⭐ `[FLAT]` board row
*"GET THE VIEW POSITION WITHOUT THE CONSOLE"*

## Why this matters for this project specifically

Everything on DOOM waits behind one thing: `psearch` needs the player's view origin, the only known
source is the console's `getviewpos`, and the prepared route is
`bind "F9" "getviewpos"` written by hand into `DOOMConfig.local` with the game closed. The board
lists three ordered checks for it — *does the engine accept `bind` in that file at all* (it shipped
with **zero** bind lines), *does the bind survive the config rewrite on exit*, *does `condump`
capture the output with the console hidden*.

**Two of those three have public answers, and the second one has a route that makes it moot.**

## 1. The `bind` command itself is real and its syntax is ordinary id Tech `[reported 2026-09-10]`

Players rebind keys from the console with `bind <KEY> <command>` — the worked example on the Steam
forum is `bind TAB _inventory`, typed after opening the console with the backtick/tilde key. So
`bind "F9" "getviewpos"` is the right shape; nothing exotic is being attempted.

## 2. The engine DOES rewrite that file, and there is a second, independent revert path the board has not listed `[reported 2026-09-10]`

DOOM 2016's settings-not-saving threads are full of players whose hand edits to
`%USERPROFILE%\Saved Games\id Software\DOOM\base\DOOMConfig.local` came back changed. The
troubleshooting the community converges on is: file permissions, **Steam Cloud**, running as
administrator, and deleting the file to let the game regenerate it.

**Steam Cloud is the addition worth taking.** It is a revert path that has nothing to do with the
engine's own config write, and a bind lost to it would look *identical* to a bind the engine
rejected — the board's check #1 and check #2 would both read "failed" for a third reason that is
neither. **If the file route is tested at all, disable Steam Cloud sync for DOOM first**, or the
test cannot distinguish its own outcomes.

⚠️ **Do not take the read-only trick as confirmed.** One poster states the mechanism —
*"if it's set to read-only the game won't be able to override settings"* — but **nobody in that
thread reports it actually preserving a hand-added line**, and the original poster's problem was
never solved. Read it as a plausible mechanism, not a working recipe `[reported 2026-09-10]`.

## 3. ⭐ The route that skips the whole question: pass it on the command line `[hypothesis]`

Our own `ENGINE-DOSSIER.md` §11 already carries **`+com_allowconsole 1`** as a launch option from
this engine's own vocabulary. That is the id Tech `+<command> <args>` mechanism: the engine executes
each `+`-prefixed console command at startup. If it accepts `+com_allowconsole 1`, the same parser
should accept

```
+bind "F9" "getviewpos" +bind "F10" "condump viewpos.txt"
```

**Nothing then has to survive anything.** The bind is applied per launch, so:

- check #1 (*does the file accept `bind`*) becomes irrelevant — the file is never touched;
- check #2 (*does it survive the config rewrite*) **disappears entirely**, and with it the Steam
  Cloud confound above;
- only check #3 (*does `condump` capture `getviewpos` with the console hidden*) is left, and that
  is the one that genuinely needs the game.

It also leaves no edit behind to clean up, which the hand-edit route does.

**Confidence, stated plainly:** the `+` mechanism working in this build is `[hypothesis]`. The
dossier's own `+com_allowconsole 1` entry is itself marked **UNTESTED** there, so this rests on an
untested premise — but it costs one launch to settle, the same launch the file route would cost,
and it settles more.

## The concrete next step this unlocks

One flat run, launching with both `+bind` arguments **and** Steam Cloud disabled, then `ctest` to
read which of the four input routes the console obeys (the board already specifies how to read that:
`"2"` alone ⇒ `WM_CHAR` only; `"01"` ⇒ the OS stack works and `WM_CHAR` does not; nothing ⇒ the
console never had focus). If `+bind` took, F9 prints the view position without a keystroke of typing.

**If `+bind` is rejected, the fallback needs no code either** — the board already established that
`type getviewpos` is available now: `AT_POSTCHAR` posts `WM_CHAR`, is the default type route, and
`autoinput_queueText()` maps arbitrary characters `[verified-numerically 2026-09-09]`.

## Sources

- [Rebinding Keys — DOOM General Discussions (Steam)](https://steamcommunity.com/app/379720/discussions/0/357286119111688929/) — the `bind TAB _inventory` syntax and the backtick console key.
- [Settings not saving in game — DOOM General Discussions (Steam)](https://steamcommunity.com/app/379720/discussions/0/141136086910173041/) — the config-revert reports, the read-only claim (unconfirmed in-thread), and Steam Cloud as a suspected cause.
- [Console Command Cheats — Doom Nexus](https://www.nexusmods.com/doom/mods/96) — config file location, `Saved Games\id Software\DOOM\base`.
