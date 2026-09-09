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
