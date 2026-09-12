# The arrow keys are fixed — and Windows cannot tell you which keys are extended (2026-09-12 evening, home PC `RTX`, `/pd`)

**The game was not launched and nothing here has been run.** One build was made, tested on the
host, deployed and hash-stamped.

Closes the 🚨⭐⭐ row queued a few hours earlier by the `/lm` session that found the defect
(`2026-09-12-three-rows-fall-in-one-launch-and-the-arrow-keys-were-never-arrows.md`, dossier §6p).

---

## 1. The defect, in one sentence

`sendinputKey()` and `rawKey()` both built their `dwFlags` as
`KEYEVENTF_SCANCODE | (down ? 0 : KEYEVENTF_KEYUP)` and **never** set
`KEYEVENTF_EXTENDEDKEY`. DOWN and numpad-2 are both scancode `0x50`; UP and numpad-8 are both
`0x48`. Without the flag, every synthetic arrow arrived as a **numpad** key, and DOOM's menus were
right to ignore it.

`seqPush()` makes this unavoidable rather than accidental: it derives the scancode with
`MapVirtualKeyA(vk, MAPVK_VK_TO_VSC)`, which returns `0x50` for `VK_DOWN` **and** `0x50` for
`VK_NUMPAD2`. The scancode alone cannot carry the distinction. Only the flag can.

## 2. The fix

- **`vkIsExtended(vk)` and `scanIsExtended(scan)`** added to `autoinput.c`.
- The flag is now OR-ed in at **all three** delivery points, so no route can disagree with another
  about which key was pressed:
  - `sendinputKey()` — the movement/hold path,
  - `rawKey()` — the path `key`, `scan` and `type` all take,
  - `postKeyMsg()` — as **lParam bit 24** (`KF_EXTENDED`), the message-route spelling of the same
    fact.
- Numpad Enter is deliberately **not** reachable: it shares `VK_RETURN` with the main Enter and only
  the extended bit separates them, so a caller asking for `VK_RETURN` gets the main one. That is
  what everything wants, and the comment says so rather than leaving it to be rediscovered.

Build clean, imports still complete (96/96), existing host tests unchanged at **116 + 30**.
`[compile-verified 2026-09-12]`

## 3. ⭐ The test failed first, and its failure was the useful part

`test/extkeytest.c` was written to check the new tables against **Windows itself** rather than
against a copy of themselves — `MapVirtualKeyA(vk, MAPVK_VK_TO_VSC_EX)`, which returns `0xE000` in
the high word for extended keys. The first run **failed on 31 keys**, and they split into two
genuine findings:

**(a) ⚠️ Windows reports the arrow and navigation cluster as NOT extended.**

```
vk 0x26 (UP):     vsc_ex = 0x0048      <- bare, no 0xE0
vk 0x28 (DOWN):   vsc_ex = 0x0050      <- bare, no 0xE0
vk 0x21..0x2E (PgUp/PgDn/End/Home/arrows/Insert/Delete/PrintScreen): all bare
vk 0x90 (NUMLOCK): vsc_ex = 0x0045     <- bare
```

`[verified-numerically 2026-09-12]` **The OS resolves the ambiguity towards the keypad** — which is
precisely the ambiguity that caused the bug. So `MapVirtualKey` **cannot be used** to decide whether
an arrow key is extended, in either mode. The keys that matter most here are exactly the keys the OS
will not vouch for.

That makes the OS valid ground truth in **one direction only**: *everything Windows calls extended
must be in our table*. The other direction has to be pinned by hand, and the test now does that in a
separate block with a comment saying that "simplifying" it into an OS query brings the bug back.

**(b) Our first table was genuinely incomplete.** Windows vouches for 19 keys we had missed — the
browser, volume, media and launch clusters, plus `VK_SLEEP`. Added. Nothing in this project sends a
media key, but a table that is wrong where it can be checked has no standing where it cannot.

Final: **`extkeytest: 47 passed, 0 failed`** `[verified-numerically 2026-09-12]`, wired into
`build.sh` so it runs on every build alongside the other three suites.

## 4. Deployed, not run

`vulkan-1.dll` md5 `54d06abe…`, deployed to the DOOM folder with
`vulkan-1.dll.pre-extkey-backup-2026-09-12` kept beside it, and re-stamped with `deployed.sh`.
**It has not been executed.**

## 5. The one check that closes this, next time DOOM is up

```
backend sendinput          (arrows need focus; inproc-keystate is dead for this game)
key esc                    -> pause menu, RESUME highlighted
key 0x28                   -> the highlight should move DOWN one row
```

| what happens | what it means |
| --- | --- |
| highlight moves to SETTINGS | ⭐ **fixed.** General menu navigation works for the first time; the profile's launch→gameplay route stops depending on lucky defaults. |
| highlight does not move, but `key enter` still works | the flag is not the whole story on this game — next suspect is the message route, since `postKeyMsg` now sets bit 24 too and can be A/B'd with `typeroute postkey`. |
| nothing works any more, including Enter | the change broke a path that worked. `vulkan-1.dll.pre-extkey-backup-2026-09-12` is beside the exe; swap it back and say so. |

## 6. What is NOT established

- **That the fix works in the game.** It is compile-verified and host-tested; the game was not
  launched. The host test proves the *classification* is right, not that DOOM accepts the result.
- **Whether DOOM's menus read the extended bit at all.** They ignored the non-extended arrows, which
  is consistent with reading it — but also with ignoring numpad keys for an unrelated reason.
- **Whether any other project's proxy has the same bug.** This one was found by accident. The same
  `KEYEVENTF_SCANCODE`-without-`EXTENDEDKEY` shape is worth grepping for across the estate; not done
  here, and it is a one-line search per project.
