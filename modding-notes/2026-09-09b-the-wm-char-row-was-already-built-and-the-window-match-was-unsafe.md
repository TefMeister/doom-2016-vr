# 2026-09-09b — the `WM_CHAR` row was already built, and the window match was genuinely unsafe

`/pd` session, dev PC. **The game was not launched. Nothing here has been run
against it.** Two `[PD]` rows: one was already done and is removed, the other was
a real safety defect and is fixed and tested.

---

## 1. ⛔️ The `WM_CHAR` row was stale — the capability already ships

The row read: *"TEACH THE HARNESS TO POST `WM_CHAR`. Static, no game needed …
**no game harness can currently type a word into a console.**"*

**All of it already exists** `[verified-numerically 2026-09-09]`:

| piece | where |
|---|---|
| `AT_POSTCHAR` posts `WM_CHAR` | `autoinput.c` — `PostMessageW(w, WM_CHAR, …)` |
| and it is the **default** type route | `static int g_typeRoute = AT_POSTCHAR;` |
| arbitrary text, not a fixed key table | `autoinput_queueText()` maps each character with `VkKeyScanA` |
| a console command to drive it | `type <text>` |
| a way to compare all four routes | `ctest` |

⚠️ **The row's premise was a misreading, and it is worth naming because it is
convincing.** The `[FLAT]` row above it says *"its key table has no `g`/`t`/`p`/`o`"*
— which is **true of `g_keys[]`** and **irrelevant**. That table is the *held
movement* keys (W/S/A/D/Space). Typing goes through `autoinput_queueText()`,
which never consults it. A true observation about the wrong table.

**What is genuinely open is a MEASUREMENT, not code:** which of the four routes
DOOM's console actually obeys has never been observed. That is `ctest`, and it
needs a launch — so it belongs to the `[FLAT]` row, not to a `[PD]` one.

⚠️ **This is the third stale row auto-pick has walked into in two days** (manhunt's
contingent DRM row, alice's re-added key-layout row, this). The pattern is not
carelessness: rows get written from the *intent* at the time and the code moves
underneath them. Auto-pick makes that expensive, because it walks straight in
where a human skims past.

---

## 2. ✅ The window match was unsafe, and the fix is verified with a decoy

The other `[PD]` row, and this one was real.

`doomdrive.py` found DOOM's window **by title alone**. On 2026-09-09
`alice_harness.py` matched **the user's Chrome tab**, because the tab's title
contained "ALICE" — the next call would have typed menu keys into their browser.

**A title is user data.** A browser tab, an editor, a chat window, a terminal can
each contain a game's name. A title match can narrow a search; it can never
establish that a window belongs to the game.

**The owning process can.** `doomdrive.py` now checks both:

```
GetWindowThreadProcessId → OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)
                         → QueryFullProcessImageNameW    → require doomx64*.exe
```

The title prefix is kept as well — DOOM makes more than one window and the title
is what separates the render window from its splash. **Title narrows; process
verifies. Neither alone is enough.**

Two details worth not re-deriving:

- ⚠️ **`QueryFullProcessImageNameW`, not `GetModuleFileNameEx`** — it needs only
  `PROCESS_QUERY_LIMITED_INFORMATION`, which a normal user holds for a normal
  process; the module-based calls need `PROCESS_VM_READ` and simply fail.
- ⚠️ **The refusal is LOUD.** A window matching the title but failing the process
  check is named in the error along with its owning process. A silent "not found"
  would read identically to "the game is not running", and the entire point is
  that an impostor is visible rather than invisible.

### The decoy, because the row asked for one and it was right to

`dev-archive/tools/test_find_window_decoy.py` creates a **real, visible top-level
window titled exactly `DOOMx64vk`, owned by `python.exe`**, and requires three
things `[verified-numerically 2026-09-09]`:

```
  [PASS] the owning process is read correctly (python.exe)
  [PASS] title-only matching FINDS the impostor (the 2026-09-09 bug, reproduced)
  [PASS] process-checked matching REFUSES it
  [PASS] and the refusal names the impostor and its process
```

⚠️ **Check 1 is what makes the other two mean anything.** If the decoy were not
actually matching on title, "the fix refuses it" would pass for the wrong reason
and prove nothing. Reproducing the bug is part of the test, not a preamble.

The decoy needs no game — it is a plain Win32 window the test makes and destroys.

**Drops filed** to `alice-madness-returns-vr` and `enslaved-vr`, whose harnesses
have the same shape (Alice's is the one the incident was about; Enslaved matches
the substring `"enslav"` and has not been observed failing). This session holds
the claim on DOOM only, so those are create-only drops rather than edits.

---

## 3. Inbox drained

`2026-09-09-pd-tandem-projconv-names-the-depth-convention.md`, filed from this
session's own earlier tandem seat, folded into dossier §6n and deleted by
explicit name. It describes `projconv`, which turns `rvproj`'s raw sixteen floats
into a named depth convention.

---

## What is NOT established

- **Nothing here ran against the game.** The window fix is
  `[verified-numerically]` against a decoy, which proves it refuses an impostor —
  **not** that it still finds the real DOOM window. That has never been exercised,
  because it needs the game running. The specific failure that would show the fix
  is wrong rather than merely untested: `doomdrive.py state` reporting "no DOOM
  window … refused" **while DOOM is visibly running**, which would mean the exe
  name assumption (`doomx64*.exe`) is wrong.
- **The `WM_CHAR` route is built but unmeasured.** Whether DOOM's console obeys
  it is still unknown, and `ctest` is the launch that decides.
- `projconv` has still never seen a real DOOM matrix.
