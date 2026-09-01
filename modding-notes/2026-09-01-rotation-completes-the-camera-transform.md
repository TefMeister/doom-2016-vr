# 2026-09-01 (late) — rotation works, and the camera transform is complete

Third session of the day, on a relaunched game running the build made a couple of hours earlier.

## What happened

`pholdyaw` turned the camera cleanly at 20° and at 90° — correct geometry, lighting and
perspective, no shear, no culling collapse, no void — and released back to the engine's own basis
exactly.

The comparison that makes it meaningful is with this afternoon's failure. Writing `forward` **alone**
sheared the image badly. Same address, same kind of write; the only difference is whether the basis
stays orthonormal. That is now demonstrated in both directions, which is worth more than either
result on its own.

## The transform is complete

| component | status |
|---|---|
| position — translate the camera anywhere | ✅ this morning |
| per-eye offset along `left` — stereo | ✅ this afternoon |
| orientation — turn the camera | ✅ **now** |
| reversible, engine's values restored | ✅ every test |

One static address, `DOOMx64vk.exe + 0x360F6B0`, gives the whole camera side of a VR mod. No engine
cooperation, no console gate, and the dormant stereo path never touched.

Worth stating plainly because it was not obvious this morning: the thing that made this fast was
**not** the bisection that found the address. It was the `/gr` drop showing id's own source moves
`vieworg` per eye. That turned "we can move a camera" into "we are holding the lever the engine
pulls", and the stereo and rotation tests followed directly from it.

## The HUD result is different under rotation, and that is new information

- **Translating** the origin removes the HUD, crosshair and weapon outright.
- **Rotating** the basis keeps them drawn and *displaces* them — at 20° they slide across the frame,
  by 90° they are gone off the edge.

Two different engine responses to two different operations on the same twelve floats. Under rotation
the first-person layer is still being rendered, just anchored to a view that no longer agrees with
it. `[hypothesis]` its placement comes from this same basis — which points at a way to keep the HUD:
rotate what the *renderer* reads and leave what the *HUD* reads alone.

I want to be careful not to let this harden prematurely. It is one observation at two angles, and
"the HUD reads the basis" is a story that fits, not a thing measured.

## Housekeeping confirmed

- **n=3 for the address.** Basis predicted from `getviewpos` before the dump, matched again. **The
  load base was identical for the third time**, so ASLR rebasing is *still* untested — it needs a
  reboot, and I should stop describing a relaunch as if it might settle it.
- **`scan 0x29` works in-game.** The console opens and types with no virtual key in the path, so the
  layout problem that cost time this morning is now routed around rather than worked around.
- The runaway guard in `pholdyaw` was never triggered and never misfired across 240 frames of
  rotation.

## Next

1. **Two eyes in one frame** — the real remaining stereo question. `multiView_60Hz` is the engine's
   own switch for exactly this ("0 = alternate frame rendering, 1 = render both each frame") but it
   is behind the console gate, so the near-term route is §6f's per-draw GPU copies.
2. **Test the rebase after a reboot.** Cheap, and it is the last thing standing between us and
   treating the address as permanent.
3. **Chase the HUD-under-rotation lever** — if the HUD's placement really does come off this basis,
   keeping the HUD in VR may be a matter of which copy we write rather than a fight.
