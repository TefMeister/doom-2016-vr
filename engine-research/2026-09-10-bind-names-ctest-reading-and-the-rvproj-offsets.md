# 2026-09-10 — bind key names, the `ctest` reading table corrected, `rvproj` offsets audited, and `+com_allowconsole` closed

*Author: `/lm` reader helper, doom-2016-vr, dev PC. **No launch. Nothing written under the game
install or `Saved Games`.** Sources: the game's own on-disk console dumps
(`~/Saved Games/id Software/DOOM/base/doomcmds.txt`, `doomcvars.txt`, `DOOMConfig.cfg`), the
reflection-database dump in `dev-archive/recon/2026-09-05-reflection-eye-field-hunt/`, the proxy
source in `staging/doom-2016-vr/proxy-vulkan/src/`, and a byte-level read of
`DOOMx64vk.exe` / `DOOMx64.exe`.*

---

## 0. ⚠️ METHOD NOTE THAT CHANGES FUTURE STATIC WORK ON THIS GAME

**Denuvo does NOT hide this binary's string data.** The complete key-name table, the cvar and
command names with their doc comments, the command-line token list and the file-path format strings
were all read directly out of `DOOMx64vk.exe` with a plain byte search — no unpacking, no debugger,
no launch. `[verified-numerically 2026-09-10]`

The dossier's standing caution *"the exe is packed at rest, so a naive string scan may find nothing"*
is **too strong for data strings**. It presumably still holds for code. Any future name question —
does token X exist in this build — is answerable statically and cheaply.

⚠️ Carry §11's other string caution though: use a **2- or 3-character minimum**, never `-n 4`.

---

## 1. ⭐ NUMPAD BIND NAMES — SETTLED

`DOOMx64vk.exe` carries the engine's full key-name table in the clear, at file offset
≈`0x283A000`–`0x283C000` (byte 42 174 000–42 180 000), laid out in **DirectInput DIK order** with a
parallel `#str_key_*` localisation key for each. `[verified-numerically 2026-09-10]`

**The numpad names this engine's `bind` accepts:**

| name | DIK scancode | extended? |
|---|---|---|
| `KP_STAR` | `0x37` | no |
| `NUMLOCK` | `0x45` | no |
| `KP_7` `KP_8` `KP_9` | `0x47` `0x48` `0x49` | no |
| `KP_MINUS` | `0x4A` | no |
| `KP_4` `KP_5` `KP_6` | `0x4B` `0x4C` `0x4D` | no |
| `KP_PLUS` | `0x4E` | no |
| `KP_1` `KP_2` `KP_3` | `0x4F` `0x50` `0x51` | no |
| `KP_0` | `0x52` | no |
| `KP_DOT` | `0x53` | no |
| `KP_ENTER` | `0xE01C` | **YES** |
| `KP_SLASH` | `0xE035` | **YES** |
| `KP_COMMA`, `KP_EQUALS` | (JP layouts) | — |

Scancodes are the DIK values implied by the table's own ordering, which is the standard DIK
sequence and matches at every anchor point tested. `[inferred-static]` for the numeric codes;
`[verified-numerically 2026-09-10]` for the *names*.

- ⚠️ **Avoid `KP_ENTER` and `KP_SLASH`.** They are extended scancodes, and the proxy's `rawKey()`
  in `autoinput.c` sends `KEYEVENTF_SCANCODE` **without** `KEYEVENTF_EXTENDEDKEY`. Sending `0x1C`
  would deliver plain Enter instead. Every other numpad key is a plain scancode and needs no change.
- ✅ **The numpad is completely free.** Zero `KP_*` binds across all eleven bindsets in
  `DOOMConfig.cfg` (407 `bind` lines total). `[verified-numerically 2026-09-10]`
- **Suggested pair:** `bind "KP_1" "getviewpos"` → `scan 0x4F`, and `bind "KP_2" "conDump viewpos.txt"`
  → `scan 0x50`.

### Corroboration for the console key, for free
The same table gives **`GRAVE` = DIK `0x29`** — independently confirming §10's `scan 0x29` as the
physical console key, from a second source that owes nothing to the layout measurements of
2026-09-01. `[verified-numerically 2026-09-10]`

---

## 2. `listBinds` output, and what F9/F10 actually collide with

- **No `listBinds` capture exists anywhere on disk.** `doomview.txt` names the command in its
  `listCmds` block but holds no output from it. `[verified-numerically 2026-09-10]`
- **`DOOMConfig.cfg` is the answer anyway** — it *is* the engine's own bind table, written by the
  game, one `bindset N` block per profile, `bindset 10` down to `bindset 0`, each opening with
  `unbindall`. The live cvar dump shows `bindset "0"`, so **bindset 0 is the active one.**
- **Bindset 0's F-keys:** `F1` → `_quick0`, `F2` → `_quick2`, `F12` → `screenshot`.
  **`F9` and `F10` are unbound in every bindset.** `[verified-numerically 2026-09-10]`
  So the 2026-09-09b prepared binds override nothing — but the account's numpad-only rule still
  applies, and the numpad is equally free.

### ⚠️ A REAL RISK to the `DOOMConfig.local` bind route that is not in the 2026-09-09b note

**Binds live in `DOOMConfig.cfg`, not in `.local`, and every bindset block starts with `unbindall`.**
`DOOMx64vk.exe` holds the strings `DOOMConfig.local` and `DOOMConfig.cfg` adjacently, `.local` first
`[inferred-static]`. If that is also the **execution** order, then `.cfg`'s `unbindall` runs *after*
the `.local` bind and erases it — and the failure would look identical to "the engine ignores `bind`
in `.local`", which is question 1 in the 2026-09-09b note. Two different causes, one symptom.

**Cheapest separator, and it needs no extra launch:** after the launch, run `listBinds` (or
`conDump`) and look for the bind. Present ⇒ the route works. Absent ⇒ *also* try issuing the same
`bind` from the console by hand in that same session; if the hand-issued bind sticks, the file is
the problem (ordering or `unbindall`), not the `bind` command.

**A third route worth knowing about:** `activateConsole` is a **registered retail command**
(`doomcmds.txt`) `[verified-numerically 2026-09-10]`. A bind to it would open the console without
touching the dead-key tilde path at all.

---

## 3. ⭐ `ctest` — the exact reading table, with three corrections

Read off `autoinput_routeProbe()` and `autoinput.c`'s `tapDown()`, not off the comment block.
`[verified-numerically 2026-09-10]` (source read; nothing run)

`ctest` queues one digit per route, in this order:

| digit | route | what is actually sent |
|---|---|---|
| `0` | `sendinput-scancode` | `SendInput` `KEYEVENTF_SCANCODE` down/up — the real OS input stack |
| `1` | `postmessage-key` | `PostMessageW(WM_KEYDOWN)` + `WM_KEYUP`, straight at the game window |
| `2` | `postmessage-char` | **the same two messages, PLUS `PostMessageW(WM_CHAR, ch)`** |
| `3` | `inproc-keystate` | fabricates the answers to the game's own `GetAsyncKeyState`/`GetKeyState`/`GetKeyboardState` |

The board's reading is **right in substance**. Three corrections:

**(a) Digit `1` is not "the OS input stack".** Route 0 is; route 1 is `PostMessage`. So `"01"` means
*the OS stack **and** posted key messages both land, and the extra `WM_CHAR` does not help.*

**(b) ⚠️ Route 2 sends a strict SUPERSET of route 1.** Any result where `1` appears and `2` does not
is **self-contradictory** and indicts the test, not the game — re-run it rather than recording it.

**(c) 🚨 THE DEAD KEY BIASES THE TEST AGAINST DIGIT `0`.** §10(b): opening the console leaves an
accent pending and the **first character typed composes with it**. `ctest` sends `0` first. If the
dead key is live, digit `0` is eaten or mangled and the sendinput route reads as dead when it is
not. `PostMessage(WM_CHAR)` bypasses `ToUnicode` composition, so routes 2 is immune and route 1
partly so — i.e. **the bias runs in exactly the direction that would make `"2"`-only look true.**
**Send space, then backspace, after opening the console and before `ctest`.** `[inferred-static]`

**(d) ⚠️ A doubled `2` is probably NOT auto-repeat.** DOOM runs a real `PeekMessage`/`Translate`/
`Dispatch` pump (§13a). `TranslateMessage` turns a *posted* `WM_KEYDOWN` into a `WM_CHAR` on its
own — so route 1 may deliver a character too, and route 2 may deliver it **twice** (its own plus the
translated one). The comment block's rule *"a repeated digit means auto-repeat, the frame rate is too
low"* holds for digit `0`; for digit `2` the likelier cause is `TranslateMessage`.
**Separator:** if `0` is single and `2` is doubled, it is `TranslateMessage`, not framerate.
`[hypothesis]`

**(e) A missing `3` is ambiguous, and `ctest` does not say so.** `autoinput_setTypeRoute()` logs a
loud warning when the key-state route is selected without the IAT hooks having landed — because
inert looks exactly like ignored. **`autoinput_routeProbe()` assigns `g_typeRoute` directly and
bypasses that warning.** So a missing `3` from `ctest` means either "the console ignores key state"
or "our hooks never installed". **Check `status` before reading digit `3`.**
`[verified-numerically 2026-09-10]` — this is a small defect in `ctest`, not in the routes.

**Unchanged and correct:** `""` ⇒ nothing landed at all — console not open, not focused, or the
window handle is wrong.

---

## 4. ⭐⭐ `rvproj`'s `+4304` / `+2032` — AUDITED, AND I AGREE WITH THE 2026-09-09b READING

### The arithmetic is sound and cannot go stale
`rvproj_delta()` computes the deltas from named constants rather than storing literals:
`RV_OFF_BASE (−96) + RVX_OFF_PROJ (4400) = +4304` for placement `g`, and
`−96 − RVX_OFF_R_IN_RENDERVIEW (2272) + 4400 = +2032` for placement `r`. Both match the header's
stated values exactly. `[verified-numerically 2026-09-10]`

### Every `renderView_t` offset re-checked against the reflection dump — all eight agree
`dev-archive/recon/2026-09-05-reflection-eye-field-hunt/view-family-fields.txt` gives the struct's
own field offsets. Subtracting 96 (`vieworg`) reproduces `renderview.h` at every field:

| reflection | field | `renderview.h` |
|---|---|---|
| `+16` | `fov_x` | `RV_OFF_FOV_X` = −80 ✓ |
| `+20` | `fov_y` | `RV_OFF_FOV_Y` = −76 ✓ |
| `+28` | `explicitProjectionMatrix` | `RV_OFF_EXPLICITMAT` = −68 ✓ |
| `+92` | `useExplicitProjectionMatrix` | `RV_OFF_USEEXPLICIT` = −4 ✓ |
| `+96` | `vieworg` | anchor A ✓ |
| `+108` | `viewaxis` | `RV_OFF_VIEWAXIS` = +12 ✓ |
| `+216` | `forceIdentityViewMatrix` | `RV_OFF_FORCEIDENT` = +120 ✓ |

`[verified-numerically 2026-09-10]`

### ✅ Agreed: the 14 rejections say nothing about `rvproj`
`renderview_check()` reads only `A−96 … A+124`. **The `+4304` / `+2032` offsets were never read on
that run.** The row is untouched, not disproved — exactly as the note says.

### ⚠️ BUT one step of the note's argument is a tautology, and should not be leaned on
The note offers *"every rejection is on `fov_x`, and **none on `vieworg`**"* as evidence.
`renderview_check()` **short-circuits**, and it tests `vieworg` finiteness **first**, then `fov_x`,
then `fov_y`, then the pair, then the two bools. So:

- `vieworg=0` is **guaranteed** — `psearch` located those addresses *by matching three finite floats
  at A+0*. It could not have been anything else.
- `fov_y=0`, `fov_pair=0`, `useExplicit=0`, `forceIdentity=0` are **vacuous** — nothing got past
  `fov_x` to reach them.

The histogram carries exactly **one bit**: *nothing had a plausible angle at A−80.*
`[verified-numerically 2026-09-10]`

### The conclusion still stands — on a better argument
The reason to blame the candidate set rather than the offset is **not** the histogram; it is that
`RV_OFF_FOV_X` is independently verified against the reflection database (table above), and the
observed values — `(0.00, 0.00)`, `(0.60, 0.13)`, `(1.00, 1.00)` — are unit/zero data, the signature
of an address inside something that is not a view struct at all. `[measured 2026-09-09]`

### 🎯 So: do NOT burn a launch pre-emptively re-deriving offsets
The decisive test is free and comes with the run the session is already planning: with a real
`getviewpos` origin, `psearch` → `rvscan` and read the histogram again.

- `fov_x` rejections **drop** ⇒ it was the candidate set. Proceed to `rvproj`.
- `fov_x` rejects **everything again** ⇒ *then* the offsets become the suspect, and the single point
  of failure to re-derive is **`vieworg` = +96**, since every other offset is expressed relative to it.

---

## 5. ⛔️ `+com_allowconsole` — CLOSED. It does not exist in this build.

§11 carries `+com_allowconsole 1` as an UNTESTED gate candidate borrowed from id Tech 5.

**`allowconsole` (case-insensitive) appears nowhere in `DOOMx64vk.exe`**, and appears in neither the
live `listCmds` (40 commands) nor the live `listCvars` dump. `[disproved 2026-09-10]`

Strength of that claim: it is a *string absence* argument, which is normally weak — but §0 above
establishes that this binary's cvar and command names **are** in the clear (the whole key table, the
cvar names and their doc comments were read out of it), so a registration literal would have been
found. It costs a line in the launch script if anyone wants belt-and-braces, but the expected result
is now "no change to the 171/40 counts".

---

## 6. ✅ `+<command>` LAUNCH ARGUMENTS DO EXIST — but the list is finite

`DOOMx64vk.exe` carries a `+`-prefixed launch-argument vocabulary as literal strings
`[verified-numerically 2026-09-10]`:

```
+set  +fs_basepath  +fs_savepath  +r_fullscreen  +r_renderAPI  +com_gameType
+com_enableDeveloperMode  +devMode_  +net_  +net_versionchecksum  +telemetry_
+menu_enableInitialAgreements  +s_noSound  +sys_lang  +sys_langPlatform
+sys_mainThreadStackSizeKB  +rgraph_enable  +connect_lobby  +connect_userId
+liveTileArgs  +ForgeStartRecordingMetrics
```

**Three end in `_` (`+devMode_`, `+net_`, `+telemetry_`) — those are prefix matches, not names.**

**Two readings, and static evidence cannot separate them:**

- **(A) an allow-list of `+` args accepted from the command line.** Supported by the prefix stems —
  you need prefix matching to test arbitrary user input — and by `+com_enableDeveloperMode` naming
  something that is **not** a registered cvar in the live dump.
- **(B) the list of `+` args PRESERVED when the game relaunches itself into the other graphics API.**
  Supported by position: the block sits beside `idCommonLocal::Launch`,
  `Restarting executable in to different graphics API....`, `+r_renderAPI -2`, and
  `L:\zion\code\engine\framework\Common.cpp(2119)`.

Both readings require a `+` parser to exist, and `+set` is the classic id Tech
set-a-cvar-from-the-command-line token. `[inferred-static]`

**The experiment is self-verifying and needs no instrumentation:** the game echoes its own command
line to `qconsole.log` (`------ Command Line ------` / `Command Line: %s`), and §11 already gives the
unambiguous positive — a change in the `listCvars` / `listCmds` counts against the **171 / 40**
retail baseline. Change one thing at a time.

**Note for whoever runs it:** `+devMode_` being a *prefix* means
`+devMode_fatalErrorOnEnter 0 +devMode_enable 1` would clear §11's FatalError tripwire and enter dev
mode **in the same launch** — which is precisely the shape the public precedent in §11 describes.
Recording the option, not recommending it: it cheat-flags the save, and launching is the user's call.

### ⚠️ CONSEQUENCE FOR THE 2026-09-10 `/gr` DROP — `+bind` IS PROBABLY NOT ACCEPTED

*Concerns, but does not supersede,
`inbox/2026-09-10-gr-a-launch-arg-bind-skips-two-of-the-three-view-position-checks.md`, which
proposes `+bind "F9" "getviewpos"` on the command line to make the config-persistence question moot.*

**`+bind` does not appear in `DOOMx64vk.exe`. Neither do `+exec`, `+unbind`, `+getviewpos` or
`+conDump`.** `[verified-numerically 2026-09-10]` The `+` tokens that *do* appear are all **cvar**
names (or cvar-name prefixes) plus `+set` — not a single **command** name among them.

That is the shape of a `+`-argument facility that **sets cvars and does not run commands**, which
would reject `+bind` outright. It is not proof: under Reading (B) the list is a forward-list rather
than an accept-list, and a general id Tech `+<command>` splitter could still take `+bind` without
ever needing the literal string. But the drop's premise — *"§11 already carries `+com_allowconsole 1`,
so the same parser should take `+bind`"* — is now weaker in two independent ways:

1. **`com_allowconsole` does not exist in this build at all** (§5 above), so the precedent it rests
   on is not a precedent.
2. **No command name appears with a `+` prefix anywhere in the binary**, while twenty cvar names do.

**This does not kill the idea, and it is still cheap to try** — the command line is echoed to
`qconsole.log`, so a rejection is visible rather than silent, and it can ride along on a launch that
was happening anyway. But **do not order the ⭐⭐ row to try `+bind` FIRST on the strength of the
drop**: plan for it to fail, and have `type getviewpos` (or the numpad bind of §1) ready in the same
launch. The drop's *other* point — **Steam Cloud as a confound for any config-file experiment** —
is unaffected by any of this and stands.

### Bonus, correcting a §11 detail
§11 says the GL build "contains no reference to `DOOMx64vk.exe`". **Confirmed** — `DOOMx64vk` is
absent from `DOOMx64.exe`. But the **Vulkan** build contains `DOOMx64` (offset 45 396 513) together
with `Restarting executable in to different graphics API....` and `+r_renderAPI -2`, so the handoff
appears to exist **one way only: vk → gl.** `[inferred-static]` This does not change the launch
recipe; it is recorded so nobody re-derives it.

---

## 7. Also confirmed, cheaply, from the on-disk dumps

- `getviewpos`, `conDump` (**capital D**), `bind`, `unbind`, `unbindAll`, `listBinds`, `exec`,
  `resourceExec`, `verifiedExec`, `writeConfig`, `screenshot`, `God`, `activateConsole` are all
  **registered retail commands**. `[verified-numerically 2026-09-10]`
- `devMode_enable "0"` and `devMode_fatalErrorOnEnter "1"` are both visible cvars, re-confirming
  §11's tripwire reading from the live dump.
- `com_enableDeveloperMode` is **not** a visible cvar, despite `+com_enableDeveloperMode` existing in
  the binary.
