# 2026-08-31 (run 8) — Scans no longer freeze the game; and the GPU copy is the wrong target

## ✅ The blocking fix works

`[measured 2026-08-31]` Frame pacing with a full scan running in the background:

| Interval | Rate |
|---|---|
| baseline, no scan | ~60 fps |
| **during a background scan** | **51 fps**, then straight back to 60 |
| (before the fix, inline scan) | **3.6 fps** |

The scan itself still completes in ~3 s and returned its 64 hits normally. Moving it to its own
thread and chunking the copy at 1 MB — taking the lock per chunk rather than for the whole sweep —
removed the freeze entirely. The game stays playable throughout.

## ❌ The strategic finding: the GPU-side camera is downstream of rendering

Run 7 patched the camera-to-world matrix successfully — 72 copies rewritten every submit — and the
image barely moved (1.3 % at yaw 20, 2.1 % at yaw 90, i.e. dust). This run explains why.

Searching for the **rotation basis** rather than the position:

| Search | Result |
|---|---|
| `(0.867, -0.499, 0)` — R's row 0 | 64 packed hits, **all** the camera-to-world matrix (translation = eye position) |
| `(0.867, +0.499, 0)` — Rᵀ row 0 | 0 packed hits (all 64 were column-3 coincidences) |
| `(-0.499, 0.867, 0)` — Rᵀ row 1 | **0 packed hits** |

**The transposed rotation — the world-to-camera basis a view matrix is built from — does not exist
as consecutive floats anywhere in the mapped buffers.** `[measured 2026-08-31]`

Combined with run 7's failed search for either inverse translation, the reading is:

- What we can find and patch is the **camera-to-world** matrix plus **`globalViewOrigin`** — inputs
  the shaders use for lighting, reflections and effects. That is consistent with the small but
  non-zero image change when we rotate them.
- Vertices are transformed by a **combined MVP / view-projection** matrix, which is **not
  orthonormal** (projection scaling is baked in), so no orthonormal-basis search will ever find it,
  and it is largely **per-object**.
- Crucially, the engine has already **derived** those matrices by the time `vkQueueSubmit` runs.
  **We are patching downstream of the thing that matters.** Patching the GPU copy cannot rotate
  geometry, however many copies we rewrite or how reliably we rewrite them.

## ⇒ The pivot: target the engine's CPU-side camera, not the GPU-bound copy

The right target is the camera state in **ordinary process memory**, which the engine reads when it
builds the view and MVP matrices each frame — the same shape of target as Psychonauts' camera
transform at `+0x150`, which is writable and *upstream* of culling and rendering.

Everything built so far transfers directly:

1. **Ground truth is already solved** — `getviewpos` via the console, read by screenshot.
2. **Value search is already written** — it just needs to scan committed process regions
   (`VirtualQuery`/`VirtualAlloc` walk) rather than the tracked Vulkan mappings.
3. **Background chunked scanning** keeps that affordable without freezing the game.
4. **Verification is already solved** — move, re-read, re-search; and screenshots prove the visual
   result, which is what caught every wrong turn today.

Expect the CPU-side copy to be a small, **stable** address (unlike the per-frame ring buffers), which
also makes patching cheap and continuous rather than needing per-submit rewrites.

## What this session cost and bought

Four wrong targets in sequence — flush path (buffer is `HOST_COHERENT`), address-based differential
(ring buffers), camera-to-world matrix (downstream), and rotation-basis search (MVP is not
orthonormal). Each was eliminated by measurement rather than argument, and each produced a durable
fact in the dossier. The machinery built along the way — console driving, value search, background
scanning, submit-time patching, screenshot verification — is all reusable and all works.

**Next session:** extend the value search to process memory and find the engine's camera struct.
