# 2026-09-10 — The view position without a human, and the engine's own projection matrix

Dev PC `DESKTOP-V8GTSIR`, `/lm`, one launch, closed through the game's own menus with no
`taskkill`. One background reader alongside on static work.

Evidence: `dev-archive/recon/2026-09-10-the-view-position-without-a-human-and-the-engines-own-projection/`
(full proxy log, `viewpos.txt`, five screenshots). Distilled into the dossier.

---

## The headline

**Both ⭐⭐ rows fell in one launch.** The project has been blocked for weeks on a single thing —
getting the player's view origin without a human reading it off the screen — and behind that sat a
second row that had never once been reached.

1. **The view position, unattended.** `1728 5440 6372.16 30.0 -0.0`, typed for, run, and captured
   to a file, with nobody watching.
2. **The engine's own projection matrix, read live and proved self-consistent.**

## 1. Typing into the console works — and the probe that says so was lying

The board's plan was to measure which of four input routes DOOM's console obeys, with `ctest`.

⚠️ **Run cold, `ctest` would have produced a false finding.** The console key is a dead key: it
leaves a pending accent, and the first character typed afterwards composes with it. `ctest` sends
its route-0 digit **first**, and route 0 is the only one that goes through `ToUnicode` — so the
accent eats exactly the digit that would prove the plain OS input path works. The result would have
read **"WM_CHAR only"**, which is a statement about the engine, and it would have been wrong. The
session reader caught this from the source before the probe was run.

Flushed first, the probe gives `0122`:

| digit | route | verdict |
| --- | --- | --- |
| `0` | `sendinput-scancode` (real OS input stack) | ✅ lands |
| `1` | `postmessage-key` | ✅ lands |
| `2` | `postmessage-char` | ✅ lands, **doubled** |
| `3` | `inproc-keystate` | ⛔ does not |

`[verified-live 2026-09-10, n=1 launch]`.

- The doubled `2` is **`TranslateMessage`**, not auto-repeat: route 2 posts `WM_KEYDOWN`/`UP` *plus*
  `WM_CHAR`, and DOOM's own message pump turns the posted key-down into a second `WM_CHAR`. `0` came
  out single in the same run, so frame rate is ruled out.
- **The `3` is a real negative, not a missing hook** — `status` was run first and reported all three
  key-state hooks installed. Without that check a missing `3` is ambiguous, and `ctest` bypasses the
  warning that would have said so.

⚠️ **Honest correction on our own method:** the flush was accidental. `key 0x39` takes a
**virtual-key**, not a scancode, so it typed a literal `9` instead of a space — visible as the stray
leading `9` on the console line. It flushed the accent all the same. The correct pair is
`scan 0x39` then `scan 0x0E`, which is what was used from then on.

## 2. The whole capture loop, unattended

```
scan 0x29                 open the console
scan 0x39 / scan 0x0E     flush the dead key
typeroute sendinput       route 3 is the default and does NOT reach the console
type getviewpos           types the whole word, cleanly
key enter                 -> 1728 5440 6372.16 30.0 -0.0
type conDump viewpos.txt  -> written to Saved Games\id Software\DOOM\base\viewpos.txt
```

`[verified-live 2026-09-10, n=1]`. Nobody read the screen; the number came off disk.

⚠️ **`typeroute sendinput` is not optional.** The proxy's default type route is `inproc-keystate`,
which is precisely the one route the console ignores. A session that types without setting the
route gets silence and no error.

**Check #3 of the board's row was already answered on disk, and nobody had looked.** An earlier
human session left `doomview.txt` in the Saved Games folder containing four real `getviewpos`
captures made by `conDump`. Along with `doomcmds.txt` (a full `listCmds`) and `doomcvars.txt`, those
files answer "does this command exist" in seconds — no packed-binary archaeology needed. **Grep the
game's own dumps before planning a launch.**

## 3. Then the chain that had never been reached

```
psearch 1728 5440 6372.16      -> 2214 candidates, 4430 MB scanned
  (move the player)
pnarrow 3436.69 6489.1 6601.38 ->  790 survivors
rvscan 12                      ->    8 pass the shape test, all conf 100/100
```

All eight read `vieworg=(3436.69 6489.10 6601.38)` and **`fov=(90.00 58.72)`**.

⭐ **`fov_x` passed for the first time.** Every earlier attempt rejected every candidate on that
field, and the 2026-09-09b note read that as a wrong candidate set rather than wrong offsets. That
reading is now confirmed: given a *correct* starting position, the same offsets pass.

Two of the eight sit in the **executable's own image** (`00007FF787B1…`), so they are static
addresses rather than heap.

## 4. The engine's own projection matrix

`rvproj 000001A5BF09C120`, at `A+4304` — the `g` placement, "set by the game":

```
[ 1.000000   0.000000   0.000000   0.000000]
[ 0.000000   1.777778   0.000000   0.000000]
[ 0.000000   0.000000  -1.000021  -3.000064]
[ 0.000000   0.000000  -1.000000   0.000000]
```

**Proved, not assumed** — the proxy's inverse-pair test reports
`proj * invproj == I to 2.9803e-08` (tolerance 0.05), which identifies the placement
`[verified-numerically 2026-09-10]`. The `r` placement (`A+2032`) reads all zeros on this candidate,
which is what a `g` hit should look like.

It cross-checks against the FOV pair independently: `1/tan(45°) = 1.000`, `1/tan(29.36°) = 1.7778`.
Two different fields agreeing to four decimals is much stronger than either alone.

**⭐ And it gives the depth convention by measurement.** Solving the third row for a standard
perspective: **near ≈ 1.50 units, far ≈ 143,000 units**, right-handed, `-1` in the `w` row — a
conventional (not reverse-Z) projection. `[verified-numerically 2026-09-10]` for the matrix;
`[inferred-static]` for the near/far arithmetic, which assumes the standard form. That directly
addresses the `external-research` topic recording that this convention "is not in any public
graphics study" — we did not find it, we measured it.

Also read live and worth having: `viewMatrix` (A+4496), `inverseProjectionMatrix` (A+4432) and
`worldSpaceMVPMatrix` (A+4624) all populated and consistent.

## 5. A retraction: the proxy's `move` is fine — I was calling it wrong

I spent four probes and three hypotheses on "the proxy cannot move the player". It can. **`move`
takes `fwd` / `back` / `left` / `right` / `jump`, not `w` / `a` / `s` / `d`**, and every one of my
commands was rejected with the reason printed in the log at the moment I issued it:

```
[auto] BEGIN "move w 150"
[auto] no recognised keys in "w"
[auto] END   "move w 150"
```

I read the *game's* state after each attempt and never read the *proxy's reply to my own command*.
Three plausible theories got built on top of that — a focus problem, a hold-duration problem, and an
unhooked DirectInput keyboard — and the log had said "I did not understand you" four times.

**`move` is UNTESTED on this game, not broken.** `[disproved 2026-09-10]` for the defect claim.

⚠️ The rule this earns: **after issuing a command to your own tooling, read the tool's answer before
you read the game's.** A game that did not change is ambiguous; a tool that said "no recognised keys"
is not.

The external harness's held key (`game-harness.py hold w 2.5`) genuinely does move the player
`[verified-live 2026-09-10, n=1]`, and it is what produced the second position — so nothing built on
top of it is affected.

### What survives, because it was verified in source rather than inferred from behaviour

**`SysKeyboard` is never hooked.** `Hook_CreateDevice` computes `isMouse` and calls
`hookMouseDevice` only when true; there is no keyboard equivalent `[verified-numerically 2026-09-10]`.
That is real, and it means `inproc-keystate` cannot reach DOOM's gameplay keyboard, which goes
through DirectInput. But it is **not** what made `move` fail tonight, and it must not be written down
as if it were.

**🚨 And a latent corruption bug falls out of it.** DirectInput devices of the same class share a
vtable, so the mouse patch very likely lands on the keyboard too. `Hook_GetDeviceState` guards on
`cb >= 12` — and a keyboard `GetDeviceState` passes `cb = 256`. With `inproc` active and a look
delta pending, it would add mouse deltas into the first 8 bytes of the **key-state array** (DIK slots
ESCAPE and 1-7): phantom keypresses, not movement. `[inferred-static 2026-09-10]`. Fix is small:
compare `self` against the recorded device pointer, and test `cb == 12 || cb == 16` with equality.

## What is NOT established

- **Which of the eight candidates is the LIVE view.** A shape match is a filter, not proof — the
  proxy says so itself. Nothing has been written to any of them yet, and the `rvexplicit`
  experiment (§6c) has not been run against this candidate set.
- **Whether the near/far numbers are right**, as opposed to the matrix being right. The arithmetic
  assumes a standard perspective form; the matrix itself is measured.
- **Whether the proxy's `move` works on this game at all** — with the right key names it has still
  never been run. The unhooked `SysKeyboard` says `inproc-keystate` cannot work; `sendinput` and
  `postmessage` are untried with a valid argument.
- Whether `conDump` captures with the console **hidden**. It did not need to here — we open and
  close the console ourselves — but the row's original question is untouched.
- The save resumed into `game/sp/intro/intro` with the player initially unable to move; that was a
  scripted opening, not an input failure, and it cost several probes before the held-key route
  separated the two.

## Automation scorecard

| Capability | State |
| --- | --- |
| 1. Self-launch | ✅ `DOOMx64vk.exe` with `SteamAppId=379720` set for that process |
| 2. Menu → gameplay | ✅ title → CAMPAIGN → GAME SLOT 1 → CONTINUE GAME → level, every highlight verified by screenshot |
| 3. Commands | ✅ **new** — the console can be typed into and its output captured to a file |
| 4. Character + camera | ⚠️ movement proven via the external harness's held key only. The proxy's own `move` is **untested**, not broken — every attempt used the wrong key names |
| 5. Self-close | ✅ pause → EXIT TO DESKTOP → confirm (defaults to **No**, moved to Yes and verified). No `taskkill` |

⚠️ Hazard found: **Esc on the main menu opens a quit prompt**, not a back action. It defaults to No,
so it is recoverable, but it is not a safe "cancel".
