# The projection/depth convention is NOT documented in any public id Tech 6 material — the guess-space cannot be narrowed from the web

**Status:** ❌ dead end (a searched negative, recorded so it is not re-searched) · **Priority:**
medium — it does not answer the board's ⭐⭐ `[PD]` row, but it tells that row not to wait for
research.

## The question this was aimed at

The board's current critical path says four projection conventions have been tried (fov 40, fov 140,
`inverse`, `tangent`) and none reproduces the engine's own view, leaving a guess-space of
"reverse-Z, infinite far, row/column major, handedness and their combinations", each guess costing a
launch. `ENGINE-DOSSIER.md` already names reverse-Z as one of the candidate explanations for the
focal term being wrong.

If a credible public source stated id Tech 6's depth convention outright — reversed depth, an
infinite far plane, the depth format — that guess-space would collapse and several launches would be
saved. This pass went looking specifically for that.

## What was checked, and what it says

- **Adrian Courrèges, *DOOM (2016) — Graphics Study*.** Already this project's most-cited public
  source. Read again against this question: it describes the depth pre-pass at the level of *what it
  is for* — opaque meshes output depth, and the subsequent pass sets the depth test to `EQUAL` to
  avoid overdraw — and **says nothing about the depth convention, the depth format, near/far
  handling, or the projection matrix layout** `[reported 2026-09-09]`.
- **Simon Coenen, *DOOM Eternal — Graphics Study*.** The closest sibling reference (id Tech 7, the
  direct successor). It refers to depth-only targets and the depth buffer in general terms and
  **also documents none of reverse-Z, the depth format, the projection convention, or the per-view
  constant-buffer layout** — it states outright that it stays high-level by design
  `[reported 2026-09-09]`.
- **"The Devil is in the Details: idTech 666"** (Tiago Sousa & Jean Geffroy, SIGGRAPH 2016), already
  credited by this project. Searched against this question; nothing surfaced that states the depth
  convention. It is a renderer-architecture talk, not a matrix-layout reference.
- General reverse-Z literature (the reversed-Z + infinite-far technique itself) is plentiful and
  well documented, but **none of it is about this engine** — it describes the technique, not id
  Tech 6's choice.

⚠️ Recorded honestly as a **searched negative on named sources**, not as proof of absence: it means
these three sources do not answer it, not that no public statement exists anywhere.

## Why this is worth keeping

Two things follow, and both save time:

1. **Do not queue a research task for the depth convention.** The obvious sources have been read
   against this exact question and do not carry it. A future `/gr` should not re-spend a pass here.
2. **It strengthens the board's own ⭐⭐ row rather than competing with it.** That row argues for
   *reading* the engine's real projection instead of guessing the convention. This pass is the
   evidence that the cheap alternative — look the convention up — is not available. The read route
   is not merely the better option; it is the only one.

The engine's own field names remain the strongest lever and they are in-house, not public:
`ENGINE-DOSSIER.md` already records `projectionMatrix`, `projectionMatrixNoJitter`,
`inverseProjectionMatrix`, `explicitProjectionMatrix`/`useExplicitProjectionMatrix`, and — most
suggestive for this question — `cramZNear` and `flipProjection`, both of which imply the engine
itself has explicit near-plane and projection-flip concepts worth reading before assuming a
convention.

## Sources

- [Adrian Courrèges, *DOOM (2016) — Graphics Study*](https://www.adriancourreges.com/blog/2016/09/09/doom-2016-graphics-study/)
- [Simon Coenen, *DOOM Eternal — Graphics Study*](https://simoncoenen.com/blog/programming/graphics/DoomEternalStudy)
- ["The Devil is in the Details: idTech 666" — SIGGRAPH 2016, Tiago Sousa & Jean Geffroy](https://www.slideshare.net/TiagoAlexSousa/siggraph2016-the-devil-is-in-the-details-idtech-666)

---

## Outcome — folded in the same day, and it did more than save a pass (added by `/gr` 2026-09-10)

The modding lane (`/pd`, dev PC, 2026-09-09, no launch) incorporated this into
`engine-research/ENGINE-DOSSIER.md` **§6n-2** with all three sources credited and the scope kept
honest, and queued no research row for the convention — both asks above were followed.

**What it unblocked, in the same session.** Being told the convention cannot be looked up moved the
question from *"what is the convention"* to *"where is it written down"* — and the answer was
already in our own dossier, unused. §6d's reflection-database walk had enumerated `idRenderView`
with byte offsets on 2026-09-05 (`projectionMatrix` **+4400**, `inverseProjectionMatrix` **+4528**)
`[verified-numerically 2026-09-05]`. The engine's own projection had been at a computable address
from any `rvscan` survivor the whole time, while four launches were spent guessing four conventions.
A new `rvproj <addr>` command now reads it and decides between the two possible placements by the
struct's own consistency: `proj × invproj` must be the identity, which **0 of 200,000 random matrix
pairs** satisfy `[verified-numerically 2026-09-09]`.

**Both reading suggestions above were taken:** `cramZNear` and `flipProjection` are named in §6n-2
as the fields a convention guess would get wrong, and both are readable by the same reflection route.

**⚠️ One limit on that verification, worth carrying forward.** An inverse-pair consistency check
identifies the matrix *fields* but **does not establish major order**. For the standard mapping
`d = zn·c`, at a near plane near 1 the inverse's lower-right block is nearly symmetric and the
transpose passes too — measured indistinguishable at `zn = 1`, clearly separated at `zn = 0.05`
`[verified-numerically 2026-09-09]`. Row- vs column-major still has to be read off the numbers.
The modding lane filed that engine-agnostically to `flat-to-vr-cross-engine-research/inbox/`, so it
is `/sr`'s to curate, not this project's.

Full write-up: `modding-notes/2026-09-09-read-the-engines-own-projection-instead-of-guessing-it.md`.
