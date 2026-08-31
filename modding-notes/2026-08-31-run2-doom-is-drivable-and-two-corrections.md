# 2026-08-31 (run 2) — DOOM is fully drivable, and two of my earlier claims were wrong

**Machine:** dev PC. **Mode:** user launched and handed off; all of the below driven unattended.
Clean graceful shutdown. Evidence: `session-2026-08-31-run2.log` + before/after screenshots.

## Headline: `sendinput` drives DOOM completely

`[verified-live 2026-08-31, movement n=2, look n=3 including a reversal]`

| Capability | Result | Evidence |
|---|---|---|
| **Movement** | ✅ **works** | waypoint **271.9 m → 232.7 m**, ~40 m, completely different location |
| **Look (yaw)** | ✅ **works** | large injection swung the view right round, waypoint marker off the compass entirely |
| **Look is controllable** | ✅ **reversible** | equal-and-opposite injection returned to **232.7 at the same compass position** |

**DOOM (2016) can be driven programmatically for movement and look.** That was the open question
for this milestone and it is answered.

Caveat: `sendinput` requires the game to be the **foreground window**. Fine unattended, but it is a
real constraint, and it is the one thing the in-process route would have avoided.

## ❌ Correction 1: `inproc-keystate` does NOT work. My previous note was wrong.

The 2026-08-31 first-run note claimed `inproc-keystate` walked the player 271.9 → 257.0 m. **That
was a misattribution.** The probe ran control → inproc → **sendinput** in sequence, and I only took
a screenshot *after the whole sequence had finished*, then credited the movement to the backend I
happened to be thinking about.

Two isolated tests this session — `move fwd 300` on `inproc` alone, twice — produced **zero
movement**. Under identical conditions `sendinput` moved the player 40 metres.

**Why it cannot work:** the early hook now catches what the late one missed —
`DirectInput8 CreateDevice(SysKeyboard)` is logged. **DOOM reads gameplay keyboard through
DirectInput 8**, not through `GetAsyncKeyState`/`GetKeyState`/`GetKeyboardState`. Our key-state
hooks install perfectly and patch functions the game never consults for movement.

`sendinput` works precisely because it feeds the real OS input stack, which DirectInput reads from
in non-exclusive mode. The same reason it reaches the mouse.

**The lesson, and it is the same one twice in one day:** an experiment that changes two things and
is measured once cannot attribute the result. The probe changed backend three times before I looked.
One isolated test per backend, screenshotted immediately, settled in minutes what the elaborate
instrument got backwards.

## ❌ Correction 2: camhunt's address-based differential is invalid for DOOM

Proven properly this time, with a **paired control**:

| Run | Changed | Still orthonormal |
|---|---|---|
| `snapa` → **walk** → `snapb` | 2780 / 4096 | **319** |
| `snapa` → **stand still** → `snapb` | 2820 / 4096 | **331** |

**Standing still produces the same result as walking.** The differential does not discriminate
camera motion at all.

**Why:** DOOM writes uniform data into **per-frame dynamic/ring buffers**. A given address holds a
different object's matrix every frame, so "the bytes at this address changed" measures buffer
recycling. The core assumption behind `camhunt` — that a matrix lives at a stable address — does not
hold here. This is the same root cause as the probe failure, now demonstrated directly rather than
inferred.

Orthonormality is also far less selective than hoped: the candidate list fills at **4096 even at
`tol 1e-5`**, because a 64 MB uniform buffer legitimately contains thousands of orthonormal
transforms (every object, every bone).

## ✅ The scan fix worked, spectacularly

**3 min 45 s → ~4 seconds.** `[measured 2026-08-31]` The write-combined-memory diagnosis was
correct: bulk `memcpy` into cached RAM before scanning, 16-byte stride, and a six-multiply early
reject gave roughly a **56× speedup**, and the game no longer freezes during a scan.

The scan is now cheap. It is the *approach* that needs replacing, not the performance.

## What the survivors did show

Survivor translations are plausible world positions in the thousands of units — e.g.
`(4103.93, 7455.13, 6914.66)`, `(2113.17, 5680.83, 6255.28)`, many repeating — consistent with the
Phase 0 `getviewpos` scale, and with these being per-object model matrices. Translation sits in
**column 3**, not row 3 (row 3 read `0,0,0` throughout).

## Next: find the camera by VALUE, not by address

The address-based hunt is dead, but we now have something better — **we can drive the game and read
the screen**. That enables the classic approach:

1. Add a `key <vk>` / `type <string>` command so the console can be driven (only WASD+Space exist
   today). The console is available in retail — Phase 0 used it.
2. `com_showCameraPosition 1` puts live position **and rotation on screen**.
3. Screenshot it → ground-truth `X Y Z pitch yaw`.
4. **Search the buffer for those float values**, not for orthonormality. A known value is an
   enormously stronger filter than a numeric property, and it needs no stable address.

That turns the whole problem from "which of 4096 matrices is it" into "find these three floats",
and the ground truth is already on screen.

## Also worth keeping

- **A too-small injection reads exactly like failure.** The first look test (~5,400 px) produced a
  few degrees and I nearly wrote off mouse look entirely; ~36,000 px swung the view right round.
  When testing whether an input path works, saturate it first, then tune down.
- **DI8 mouse uses buffered `GetDeviceData`**, so immediate-mode `lX`/`lY` injection would be
  ignored — but this no longer matters, because `sendinput` reaches the device anyway.
- Graceful `WM_CLOSE` shutdown works reliably; used twice today, no force-kill needed.

Code: `staging/doom-2016-vr/proxy-vulkan/`.
