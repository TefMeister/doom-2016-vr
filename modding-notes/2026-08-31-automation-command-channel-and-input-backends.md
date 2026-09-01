# 2026-08-31 — DOOM gets an external command channel and four input backends

**Machine:** dev PC. **Game never launched this session** (standing rule: only the user launches).
**Status of everything below:** `[compile-verified 2026-08-31]` — clean build, off-game smoke test
passes, **never run against DOOM**.

## Why this, today

M1 — the camera hunt in `camhunt.c` — has been built since 2026-08-26 and never run once. The
reason was not the code. Its only trigger was **NUMPAD 1/2/3**, so it needed a human standing at
the keyboard, and the differential design needs *two different camera poses*, so that human also
had to move between presses. A stalled project, blocked on attendance rather than on engineering.

So: replace the trigger with a file-based command channel, and give the proxy its own way to move
the camera.

## What was built

### The command channel (`src/autocmd.c`)

Commands are appended to `doom_automation_cmds.txt` beside the exe; answers come back in the proxy
log. Helper: `scripts/doom-auto.ps1`. This is the **third** use of a shape already verified in-game
twice — XIII's `xiii_automation_cmds.txt` and Psychonauts' `psyvr_automation_cmds.txt`.

Two details carried deliberately from those projects:

- **Truncate the file before executing, not after.** A line still sitting in the file proves it
  never ran. That is precisely how XIII's GPF was eventually pinned to a specific call.
- **Log BEGIN before and END after every command, flushed.** XIII 0.2.8 logged only on completion,
  so its crash left no record of which call died and it had to be inferred.

`tol <float>` retunes the orthonormality tolerance live. That is not a convenience: the dossier
expects the first real scan to return either far too many candidates or none, and retuning a
`#define` means a rebuild → a relaunch → waiting for the user.

**Opt-in, off by default** (`DOOM_AUTOMATION=1` or a marker file). A proxy that could drive the
game the moment it loaded is exactly the unattended-build hazard that corrupted a live RE Village
install on 2026-08-24.

### Four input backends (`src/autoinput.c`)

The user's framing, and it is the right one: use a *combination* of methods so the game can be
moved and looked around as much as possible — for every game, not just this one.

| backend | mechanism |
|---|---|
| `inproc` | post `WM_INPUT` with a sentinel handle, then answer the game's own `GetRawInputData` with fabricated data |
| `sendinput` | the OS input stack (Raw Input consumes it; needs focus) |
| `postmessage` | legacy `WM_KEYDOWN` / `WM_MOUSEMOVE`, focus-independent |
| `vigem` | virtual XInput pad at driver level |

`inproc` is the interesting one and it is the general lesson: **we are inside the process, so we do
not have to push events at the game from outside.** We post it a message and then answer its own
input read ourselves. The game never asks the OS — it asks us. That sidesteps both walls this
portfolio has hit: exclusive-mode capture (XIII, Psychonauts) and focus.

`vigem` **reports unavailable rather than pretending**. The driver needs an elevated install that
is still an open user action, and writing its report path blind would be unverifiable code — plus
the no-copy rule means writing our own client rather than vendoring ViGEmClient.

### `probe` measures instead of assuming

This is the part worth keeping. "The input API returned success" and "the game reacted" are
different facts, and we have paid for the difference twice: XIII swallowed 600 px of `SendInput`
motion as **0.0°** of yaw, and RE Village ignores `SendInput` entirely while honouring
`PostMessage`. Neither failure was visible from the call site.

So `probe` scores each backend against `camhunt_changedSinceA()` — what the game actually renders —
and **runs a no-input control first**. The control matters: a camera drifts on its own from idle
sway and TAA jitter, so "something changed" is not evidence. A backend counts only if it beats the
control by a clear margin.

### Hooking method

**IAT patching, not an inline trampoline.** It writes to a data page rather than to code, so it
needs no disassembler and does not argue with **Control Flow Guard**, which the dossier records as
enabled on both DOOM executables.

## A real trap found on the way

`build.sh`'s import-coverage check failed on **every one of the 96 names** after a fresh clone.
Nothing to do with the new code: this repo checks out with `core.autocrlf=true` on Windows, so
`gen/doom-imports.txt` arrives with CRLF, and `comm` was comparing `vkAcquireNextImageKHR\r`
against `vkAcquireNextImageKHR`. It reads exactly like a catastrophically broken build.

Fixed in the script (`tr -d '\r'`) rather than in the file, because git would just re-convert the
file on the next clone. Generalised to `flat-to-vr-cross-engine-research` — any repo whose build
verifies itself by comparing a checked-in list against tool output has this bug latent.

## Verification actually run

- `bash build.sh` → **0 warnings**, 246/246 exports, **all 96 imports covered**.
- `bash build.sh --test` → smoke test **passes**: proxy loads, real `VkInstance` created through
  the hook, GPU enumerated through thunks ("NVIDIA GeForce GTX 1660 SUPER"), clean teardown.

**What the smoke test cannot tell us:** anything about the input path. It has no game window and
never reaches frame 120, so `autocmd`/`autoinput` are not exercised at all. Whether `inproc`
actually lands is genuinely open — if DOOM reads input via `GetRawInputBuffer` instead of
`GetRawInputData`, the hook will install and still produce nothing. `autoinput_init` logs whether
that import is present, so the first live log says which case we are in.

## Next session

1. Reinstall the current build — the game folder still has the **old 2026-08-26 proxy** (94 KB).
2. User launches, gets into a level, hands off.
3. `probe`, then `snapa` / `look` / `snapb`, then confirm a survivor arithmetically against
   `getviewpos`.

Code: `staging/doom-2016-vr/proxy-vulkan/`, commit `0d314b1`.
