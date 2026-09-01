# 2026-09-01 (late) — rotation works, and that completes the camera transform

Third session of the day, on a relaunched game running the new proxy build.

## The result

**`pholdyaw <addr> <deg>` turns the camera cleanly.** Writing the basis coherently — `forward` and
`left` rotated together about Z, origin untouched — produces a **proper camera turn**: correct
geometry, correct lighting, correct perspective, no shear, no culling collapse, no void.

Compare with `02-forward-only-write-shears-the-view.jpg` in the previous recon folder, where writing
`forward` **alone** produced a badly sheared, washed-out image. Same address, same kind of write; the
difference is entirely whether the basis stays orthonormal.

- **20°** (`03-basis-rotated-20-degrees.jpg`): a modest, clean turn. The crosshair displaced roughly
  **232 px**, which is what 20° works out to at ~110° horizontal FOV across 1280 px
  `[measured 2026-09-01]` — though note the FOV was not re-read this session, so treat the numeric
  agreement as corroborating rather than as an independent measurement.
- **90°** (`04-basis-rotated-90-degrees.jpg`): a large turn, still completely clean.
- **Release** (`05-restored-identical-to-before.jpg`): visually identical to
  `02-before-rotation.jpg`, and `pdump` reads the engine's original basis back exactly —
  `-0.799 -0.600 -0.039 / 0.601 -0.800 0.000 / -0.031 -0.023 0.999`.

## What this completes

With rotation confirmed, **every component of the view transform at `DOOMx64vk.exe + 0x360F6B0` is
now known writable, and the world renders correctly from the result**:

| component | status |
|---|---|
| position (translate the camera anywhere) | ✅ 2026-09-01 morning |
| per-eye offset along `left` (= stereo) | ✅ 2026-09-01 afternoon |
| orientation (turn the camera) | ✅ **this session** |
| all of it reversible, engine's own values restored | ✅ every time |

That is the whole camera side of a VR mod, from a single static address, with no engine cooperation
required and the dormant stereo path untouched.

## The HUD behaves differently under rotation than under translation

Worth recording precisely, because it is a **different** result from the morning's:

- **Translating** the origin removes the HUD, crosshair and weapon **entirely** — which Photo Mode
  confirmed is the engine's designed behaviour when the view stops being the player's.
- **Rotating** the basis **keeps them rendered but displaces them** — at 20° the crosshair and health
  bar slide across the frame with the weapon pushed to the edge; by 90° they have travelled out of
  frame altogether.

So the two operations trip different engine responses. Under rotation the first-person layer is
still being drawn and is simply anchored to a view that no longer matches. This is a useful lever:
it suggests the HUD's placement derives from the same basis, so a VR build may be able to keep the
HUD by rotating the basis the renderer sees while leaving whatever the HUD reads alone.

## Also confirmed this session

- **The address held for a third time** `[verified-live 2026-09-01, n=3 process instances]`. Basis
  predicted from `getviewpos` (`1728 5440 6372.16 216.9 2.2`) before dumping, matched to three
  decimals. Load base was **the same again**, so ASLR rebasing is *still* untested — that needs a
  reboot.
- **`scan 0x29` works** (`01-scan-0x29-opens-the-console.jpg`). The console opened and `getviewpos`
  typed cleanly with no virtual key involved anywhere and no dead-key mangling — so the
  layout-dependence documented in §10 is now routed around rather than worked around.
- **The runaway guard was not needed but did not misfire**: 240 frames of rotation, released on
  request, originals restored.
