# 2026-08-31 (run 3) — 🎯 THE CAMERA IS FOUND

**Machine:** dev PC. **Mode:** user launched, handed off; everything below driven unattended.
Clean graceful shutdown. Evidence: `session-2026-08-31-run3-camera-found.log` + screenshots.

**M1's question — "how does the view matrix reach the GPU" — is answered.**

## The camera transform, located and confirmed

`[verified-live 2026-08-31, n=2 independent positions]`

```
 0.825  -0.563   0.049   2731.799
 0.562   0.826   0.034   6212.317
-0.060   0.000   0.998   6355.658
```

- **Column 3 is the world position**, matching `getviewpos` **exactly** (2731.8 6212.32 6355.66).
- The 3×3 is a genuine orthonormal basis — row 0: `0.825² + 0.563² + 0.049² = 1.0000`.
- Row 2 ≈ `(0, 0, 1)` — **Z-up confirmed**, independently of the earlier static reading.
- Lives in **region 2**, the high-flush per-frame uniform buffer (flush count rose 24806 → 29331
  across the session, exactly as a per-frame buffer should).
- **Replicated per draw** — the search capped out at 64 hits, all in region 2. Every draw's uniform
  block carries its own copy.

Also present, and found first: the position as a **packed `vec4` with `w = 1.0`**
(`2516.204 5977.121 6328.120 1.000`). That is `globalViewOrigin` — one of the renderparms the
binary names in its own string table.

## How it was found: search by VALUE, not by address

The address-based differential died in run 2 (per-frame ring buffers reuse an address for a
different object every frame). The replacement worked on the first attempt:

1. Drive the game's own console and run `getviewpos` → **ground truth on screen**.
2. Screenshot and read `2516.2 5977.12 6328.12 34.3 3.4`.
3. `findvec` those three floats in the mapped buffers.
4. **Move, re-read (`2731.8 6212.32 6355.66`), search again** — the memory tracked the camera.

Two independent positions, both matching exactly, is what makes this a finding rather than a
coincidence. A known value is an enormously stronger filter than orthonormality, which matched
thousands of transforms even at `tol 1e-5` — and it does not care that the buffers move data
around every frame.

## ⚠️ Dossier correction: `getviewpos` prints YAW then PITCH

`[verified-live 2026-08-31 — derived arithmetically from the matrix]` §6e recorded the format as
`X Y Z pitch yaw`. The two are the other way round:

- Reading was `... 34.3 3.4`. The matrix shows a rotation about **Z (the up axis) of 34.3°** —
  `cos 34.3 = 0.826`, `sin 34.3 = 0.563`, exactly the row-0/row-1 values.
- The tilt is `asin(0.060) = 3.44°`, matching the trailing **3.4**.

So **column 4 is yaw, column 5 is pitch**. Worth having right before anyone builds head-tracking on
it — a swapped pitch/yaw is the kind of error that produces a plausible-looking but wrong camera.

## Driving the console — two traps worth keeping

**The tilde key is layout-dependent, and DirectInput binds the physical scancode.** The first
attempt sent `VK_OEM_3`, which on this machine's layout maps to scancode **0x28** — a different
physical key. DOOM's console is on scancode **0x29**, which here is `VK_OEM_8`. Nothing opened and
the failure was silent.

**General rule: DirectInput reads physical scancodes, and the VK→scancode mapping is layout
dependent.** When a key "does nothing", check what scancode you are actually sending before
concluding the binding is wrong. `MapVirtualKey(vk, MAPVK_VK_TO_VSC)` will tell you in one call.

**Diagnosing it cleanly mattered too.** Rather than guessing at keys, the pump was first tested with
`type wwww...` — the player walked ~18 m, proving the queue, the hold timing and the scancode path
all worked, which isolated the fault to the tilde key alone.

Typing itself works: `com_showCameraPosition 1` appeared in the console **character-perfect**,
underscore and all, and was verified by screenshot before Enter was pressed.

`com_showCameraPosition 1` was set but produced **no visible on-screen overlay** — possibly a debug
layer `PrintWindow` does not capture. Not pursued: `getviewpos` prints into the console, which is
captured perfectly, and that was enough.

## Where this leaves M1

Finding it is done. **Controlling it is the next problem, and it is a different one:** the transform
is rewritten every frame and replicated across 64+ per-draw uniform blocks, so poking one address
achieves nothing — the next frame overwrites it.

Control has to happen at the **write path**, not the memory:
1. The buffer is `HOST_VISIBLE` and CPU-written (DOOM imports neither `vkCmdPushConstants` nor
   `vkCmdUpdateBuffer`), so every update passes through a mapping we already track.
2. Hook `vkFlushMappedMemoryRanges` — already hooked for the flush counter — and rewrite the camera
   transform *in the flushed range* before it reaches the GPU.
3. The per-draw replication is an advantage for stereo: each eye needs a different view, and the
   copies are already per-draw.

## Next session

1. Intercept at flush time and **write** a modified camera — start by nudging yaw a few degrees and
   confirming by screenshot that the rendered view turns.
2. Then per-eye: offset the position along the basis's right vector (row 0) for IPD.
3. `stereoRender_*` remains the other route, still unreachable from a retail console.

ViGEmBus install still outstanding, and would remove `sendinput`'s foreground requirement.
