# 2026-09-01 (afternoon) — the address survives a restart, and it produces stereo

Second autonomous session of the day, on a relaunched game (fresh process, fresh level load).

## 1. The address held, and the basis was predicted before it was read

`getviewpos` read `1731.42 5441.92 6371.72  yaw 30.0  pitch -0.0`. From that alone the basis was
computed, and only then was `DOOMx64vk.exe + 0x360F6B0` dumped:

```
+0   1731.418  5441.916  6371.721      origin    (matches getviewpos)
+3      0.866     0.500     0.000      forward   (predicted 0.866 0.500 0.000)
+6     -0.500     0.866     0.000      left      (predicted -0.500 0.866 0.000)
+9      0.000     0.000     1.000      up        (exactly Z-up at pitch 0)
```

`[verified-live 2026-09-01, n=2 process instances]`

**Caveat kept deliberately:** the module loaded at the **same base** both times, so this is
reproducibility across a *restart*, not a test of **ASLR rebasing** — that needs a reboot. Use
`GetModuleHandle(NULL) + 0x360F6B0` rather than the absolute address; correct either way.

## 2. ⭐ Stereo works from this address

`05-stereo-left-eye-minus32-along-left.jpg` and `06-stereo-right-eye-plus32-along-left.jpg` are the
same scene rendered from `origin ± 32·left`. The parallax is depth-correct: the crate at the right
edge swings hugely between the two frames while the distant towers barely move. Both frames render
cleanly.

This is the operation id's own source says `stereoRender_separation` performs on `vieworg` — so
**per-eye rendering does not require reviving the dormant stereo path.** Caveat: two *sequential*
frames, not two eyes within one frame. The geometric primitive is proven; per-frame delivery is not.

## 3. Rotation needs the whole basis

`02-forward-only-write-shears-the-view.jpg`: holding **only** `forward`, rotated 20° about Z, gives a
badly sheared washed-out image with the HUD displaced — not a clean turn. The vector is clearly
consumed by the renderer, but a coherent rotation must move `forward` and `left` together.
`03-restored-after-shear.jpg` confirms release put the engine's basis back exactly.

That is why `pholdyaw <addr> <deg>` was added to the proxy the same day: it rotates the engine's
**live** basis each frame about Z, leaves the origin alone, and guards against runaway (if the value
it finds is the one it wrote, the engine did not refresh, so it re-applies the same rotation instead
of compounding one).

## 4. `setviewpos` is not on retail

`04-setviewpos-not-registered-on-retail.jpg`: `Unknown command 'setviewpos'`. Research had suggested
it as a free cross-check of the address; it exists in the engine but sits behind the console gate, so
the cross-check is not free on retail.

## What research contributed to this session, and it was decisive

Three `/gr` drops were drained into the dossier at the start of this work:

- **id's GPL Doom 3 BFG source** shows `vieworg` "has already been adjusted for stereo world
  seperation" — reframing our control point from a workaround into *the same lever the engine
  pulls*. That is what motivated the stereo test above, which then worked first try.
- **Photo Mode** is a shipped, ungated, detached free camera with the player invisible — so the
  elevated-camera result from the morning was riding a **designed** engine path, not luck.
- **The HUD loss cannot be culling** — the UI has its own render target and is composited last. It
  is most likely game state, which reframes it from "bug to fix" to "state to control".
