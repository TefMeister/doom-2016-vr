# Engine Dossier — DOOM (2016) (id Tech 6 engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** Phase 0 not started — repos just seeded, install still finishing on the dev PC ·
**VR-readiness verdict:** TBD

## 1. Identity
- Game / build / version: DOOM (2016), id Software, published by Bethesda Softworks. Steam release.
- Platform & store; unofficial port? (extra fragility/legal notes): Steam (PC). No known unofficial-port concerns.
- Legitimacy: owned copy (installing at time of writing).

## 2. Engine lineage
- Family / base engine and how it was modified: **id Tech 6**, id Software's successor to id Tech 5
  (used in The Evil Within, our own `the-evil-within-vr-*` project — worth cross-referencing that
  dossier once recon starts here). Not yet confirmed directly against this binary.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.): TBD.
- Distinctive file formats / build tags / symbol naming: TBD.

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): TBD.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: TBD — id Tech 6's DOOM (2016) shipped
  with an **OpenGL 4.x** renderer at launch and added a **Vulkan** path in a later patch (selectable
  in-game); which this build defaults to, and whether both are present, needs confirming directly.
- Developer console / cvar system present? how opened?: id Tech engines are well known for a
  console (historically `~`); presence/binding not yet confirmed for this build.

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: TBD.
- Attach workflow that works: TBD.
- Injection vector that works (proxy DLL name / injector / framework): TBD.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)
- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**:
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention:
- Where projection `P` / FOV comes from:
- The per-eye override maths (`K_eye = …`):

## 7. Constant-buffer fill mechanism
- Map/DISCARD ring / UpdateSubresource / D3D11.1 offset / **persistent map +
  memcpy** (trap):
- Can source contents be read cheaply (captured CPU pointer) or need staging
  read-back?:
- The chosen override patch point and why:

## 8. Pass inventory (by render target)
- Main scene (res/formats):
- Shadow passes (depth-only sizes):
- Post / AA chain (SMAA/TAA/motion vectors; downscale sizes):
- UI / HUD (how it's kept separate):

## 9. cvar / console cheat sheet
| command / cvar | effect | use |
|---|---|---|
| | | |

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used):
- In-process input / camera drive method that worked:
- Frame-capture method; where images land:

## 11. Dead ends & false leads (save future time)
- <what looked true but wasn't, and why>

## 12. Open risks toward the North Star
- id Tech 6 has no known prior turnkey VR injector (unlike UE4/RE Engine) — expect Phase 3–4 to be
  a fully manual camera-matrix hunt, per the `PLAYBOOK.md` appendix note for bespoke/no-tool engines.
- Renderer choice (OpenGL vs Vulkan) is unconfirmed and will materially change the injection/hook
  strategy (a GL proxy is a very different shape from a Vulkan layer) — resolve this first in Phase 0.
