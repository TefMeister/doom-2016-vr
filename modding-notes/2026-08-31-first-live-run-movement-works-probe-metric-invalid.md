# 2026-08-31 — First live run: movement works, and two of my designs were wrong

**Machine:** dev PC. **Mode:** user launched, loaded a Mars gameplay level, handed off ("all
yours"); everything below was driven unattended. **Result: the proxy ran 43,028 frames in real
gameplay and detached clean.**

Evidence: `session-2026-08-31-first-live-run.log`, plus before/after screenshots.

## The headline: we can drive DOOM's movement

`[verified-live 2026-08-31, n=1 per backend]`

| Backend | Movement | Evidence |
|---|---|---|
| **`inproc-keystate`** | ✅ **works** | Waypoint distance **271.9 m → 257.0 m** — about 15 m walked, scene changed from open Mars vista to inside a cave |
| **`sendinput`** | ✅ **works** | **257.0 → 255.8**, view visibly shifted |
| `postmessage` | ❌ no effect | View and distance unchanged |
| `vigem` | ⏸ untestable | ViGEmBus still not installed |

`sendinput` working was predicted and the reason is worth keeping: DOOM reads keys through
`GetAsyncKeyState`/`GetKeyState`, and those reflect OS-level key state, which `SendInput` genuinely
updates. It is not going through DirectInput at all for the keyboard.

**Mouse look does NOT work yet.** Fabricating `GetCursorPos` produced **no yaw change whatsoever**
— identical view, compass marker in exactly the same place. The `Get`/`SetCursorPos` pair is not
DOOM's look path; DirectInput is. That is the one thing standing between us and full drivability,
and it is the half VR actually needs.

## ❌ Correction: the `probe` metric is invalid. Do not trust it.

This is the important one, because I documented `probe` as the most valuable part of the input work.

**It reported `no clear reaction` for `inproc-keystate` — the backend that had just walked the
player fifteen metres.** Its numbers:

```
control            -> 274 of 4096 matrices drifted with NO input
inproc-keystate    -> 235 of 4096 changed (control 274, margin -39)   "no clear reaction"
sendinput          -> 134 of 4096 changed (control 274, margin -140)  "no clear reaction"
```

Both scored **below** the control. A backend that does nothing should score *the same* as the
control, not less — that pattern alone says the measurement is noise.

**Why it is broken:** `camhunt`'s candidate addresses sit in per-frame dynamic/ring buffers. The
memory at a given address is reused for completely unrelated data every frame, so "did the bytes at
this address change" measures buffer recycling, not camera movement. Comparing counts across runs
compares two piles of noise. The 4096-candidate cap filling at the default tolerance made it worse.

**What actually worked: taking a screenshot and looking at it.** The waypoint distance readout in
DOOM's own HUD is unambiguous ground truth, costs two seconds, and settled every question the
four-minute scan could not.

This is precisely the failure the toolkit's own `capture-window.ps1` header warns about — *"the
cheapest way to get it wrong is to infer state from a derived number instead of looking"* — and I
walked into it while holding the tool that exists to prevent it. Worth noting I nearly did it twice:
a mean-pixel-difference metric then said inproc changed only 0.93 %, which was also misleading (the
player was jammed against a cave wall by then, so further forward input genuinely changed little).

## ❌ Correction: the camhunt scan was pathologically slow

**One scan took 3 minutes 45 seconds and froze the game solid** for its duration (no frames
presented). The probe does five of them.

**Cause:** `HOST_VISIBLE` Vulkan memory is typically **write-combined**. WC memory is designed for
streaming CPU *writes* and is brutally slow to *read* — and the scan was doing roughly 24 million
small strided reads straight out of it. Effective throughput was about **430 KB/s**.

**Fixed** (in this commit, not yet run live): bulk `memcpy` each region into ordinary cached RAM
first and scan the copy; 16-byte stride instead of 4, since uniform-buffer matrices are at least
16-byte aligned; and a six-multiply early reject before any of the expensive checks. Plus live
`budget <MB>` and `stride <n>` commands so tuning never needs a rebuild — a rebuild needs a
relaunch, and only the user can give one.

## ❌ The DirectInput instrumentation installed too late

`autoinput_init` ran at frame 120 and **logged no `CreateDevice` calls at all**. DOOM builds its
input devices during startup — `vkCreateInstance` at 13:24:51, first presented frame at 13:25:51, a
full minute later. Hooks now install from `vkCreateInstance` instead.

## Useful things measured along the way

- **7 live `vkMapMemory` regions**, of which **2 are `VK_WHOLE_SIZE`** and are skipped as
  unknown-extent. Sizes: two 64 MB, three 75 KB.
- **`map 2` (64 MB) has 27,907 flushes** against `map 6`'s 2,983 and zero for the rest. That is the
  per-frame uniform buffer and it is where the camera almost certainly lives. The rebuilt scan now
  orders regions by flush count so the budget is spent there first.
- Steady **~60 fps** with the proxy attached, 1280×720 windowed.
- Graceful shutdown via `WM_CLOSE` works cleanly — no force-kill needed.

## Next session (needs a relaunch to load the new DLL)

1. **Confirm the DI8 mouse wrap lands.** The log will now say whether `SysMouse` was hooked, and —
   critically — whether the game uses **buffered `GetDeviceData`**, in which case immediate-mode
   `lX`/`lY` injection is ignored and events must be fabricated instead.
2. **Test look** the same way movement was tested: screenshot, `look`, screenshot, read the compass.
3. **Re-run the camera hunt** with the fixed scan, which should take seconds rather than minutes.
4. **ViGEmBus** remains the strongest untested path — DOOM imports XInput directly.

Code: `staging/doom-2016-vr/proxy-vulkan/`, commit `ea0e1c6`.
