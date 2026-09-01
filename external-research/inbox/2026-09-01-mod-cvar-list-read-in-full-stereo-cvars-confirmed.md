# Verdict: the full cvar list was read — `stereoRender_*` IS present, and the "absent" reading is disproved

**Supersedes:** the open item in `2026-09-01-gr-console-gate-has-a-public-defeat-with-rp-and-setviewpos.md`
asking for a human with a browser, and the earlier pass's report that `doom_cvars.txt` contains no
`stereoRender_*`.
**From:** modding session, 2026-09-01 (afternoon). **For `/gr`:** flip the relevant `INDEX.md` status
tags — this lead is now ✅ incorporated (folded into `ENGINE-DOSSIER.md` §12).

## How it was read, because this is the reusable part

`curl -L https://raw.githubusercontent.com/brunoanc/DOOMLegacyMod/master/doom_cvars.txt` returned
**711,227 bytes / 11,103 lines / 6,572 cvars** in one call — the complete file.

**The obstacle was never the file's size; it was the tool.** A page *fetch* truncates and returned
only the head of the alphabet. A *download* has no such limit. No human, no browser, no Ctrl-F was
needed — the request for two minutes of the user's time was avoidable, and the user rightly found it
confusing to be asked.

**Control run first**, since that is what invalidated the previous attempt: `g_fov` — verified live
on our own build — is present at line 3791 ("camera field of view"). The read is sound, so its
negatives are now evidence.

## Results

| term | result |
|---|---|
| `stereoRender_*` | **PRESENT — all four**, help text matching our static pass word for word |
| `multiView_60Hz` | **PRESENT** — "0 = alternate frame rendering, 1 = render [both each frame]" |
| `com_production` | **PRESENT**, plus `com_forceProductionCvars` ("force production cvars to specific values during build") |
| `explicitProjectionMatrix`, `explicitFov_*`, `forceIdentityViewMatrix` | **ABSENT** — not cvars at all |
| a stereo **mode** selector (`stereoRenderMode_t`, `hdmi3d`, `topBottom`, `leftAndRight`) | **ABSENT** |
| HMD / Oculus / VR cvars | **none** (the `rift` hits are AI demon-spawn cvars) |

Verbatim, as the file has them:

```
stereoRender_guiOffset           shift guis so they don't appear at infinity
stereoRender_screenSeparation    screen units from center to eyes
stereoRender_separation          world units from center to eyes
stereoRender_swapEyes            swap target buffers for left and right eyes
multiView_60Hz                   0 = alternate frame rendering, 1 = render
com_production                   Used to enable and/or inhibit specific
                                 behaviour during production building mode.
com_forceProductionCvars         Set to force production cvars to specific
                                 values during build
```

## The finding that changes the plan, and it is not the obvious one

**There is no stereo MODE cvar.** The dossier (§6a) had recorded that the cvar selecting
`stereoRenderMode_t` could not be resolved statically because of linker string dedup, and advised
finding it live via `listCvars`. This list says it is **not a cvar at all**.

So opening the console gate would hand us the stereo path's **parameters** — separation, screen
separation, GUI offset, eye swap, AFR-vs-both-per-frame — **but not its on-switch.** Enabling stereo
would still require calling engine code. That is a materially different problem from "set a cvar,"
and it should be settled before the gated console is treated as *the* route to stereo.

Two consequences worth carrying into the index:

1. **`multiView_60Hz` is directly on our critical path** regardless of the gate. Our live stereo
   result (dossier §6h-2) produced two eyes in two *sequential* frames; this cvar's help text names
   exactly that distinction. It is the engine's own answer to the question we are holding.
2. **`explicit*` are renderparms, not cvars**, so `rp` — not a cvar set — is their route, which
   raises `rp`'s value relative to the rest of the unlocked command set.

## Also settled live today, for the same INDEX row

**`setviewpos` is NOT registered on retail** `[verified-live 2026-09-01, n=1]` — the console answers
`Unknown command 'setviewpos'`. The suggestion to use it as a free cross-check of the §6h address is
sound in principle but **gated in practice**; it needs the console defeat installed first, which
remains the user's call.
