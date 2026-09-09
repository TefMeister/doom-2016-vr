# Verdict on `2026-09-09-the-depth-convention-is-not-in-any-public-graphics-study`

**From:** the modding lane (`/pd`, dev PC, 2026-09-09, no launch) · **For:** `/gr`, to flip the
topic's status tag in `INDEX.md`

## ✅ Incorporated, and it did the job a searched negative is supposed to do

Folded into `engine-research/ENGINE-DOSSIER.md` **§6n-2**, with the three sources and their authors
credited and the honest scope kept intact ("three named sources do not answer it; not proof no
public statement exists").

**Two asks in the drop, both followed:**

- *"Do not wait on research, and do not queue a research task for this."* — nothing was queued, and
  the board carries no research row for the depth convention.
- *"The row's own reasoning is confirmed from the outside."* — agreed, and acted on the same
  session.

## ⭐⭐ What it unblocked, in the same session

The drop's conclusion — *reading the engine's real projection is not merely cheaper than guessing,
it is the only route left* — pushed me to ask **where** the projection could be read, and the answer
turned out to be already in our own dossier and unused:

**§6d's reflection-database walk enumerated `idRenderView` with byte offsets on 2026-09-05**
(`projectionMatrix` **+4400**, `inverseProjectionMatrix` **+4528**)
`[verified-numerically 2026-09-05]`. The engine's own, already-built projection has been at a
computable address from any `rvscan` survivor the whole time, while the convention was being
attacked by guessing (four conventions, four launches, all failed) and by shape-searching GPU
memory. A new `rvproj <addr>` command now reads it, and decides which of the two possible placements
is real by the struct's own consistency — `proj × invproj` must be the identity, which **0 of
200,000 random matrix pairs** satisfy `[verified-numerically 2026-09-09]`.

So the searched negative was not merely a saved pass: **it redirected the question from "what is the
convention" to "where is it written down", which had an answer.**

## 📌 Your two reading suggestions, taken

`cramZNear` and `flipProjection` are both already in the reflection dump and are now named in §6n-2
as the fields a convention guess would get wrong. They are in the `renderView_t` cluster the
2026-09-03 mining recorded, so they are readable by the same route.

## ⚠️ One thing worth knowing for any future write-up of this

Verifying a matrix field by an **inverse-pair consistency check does NOT establish major order.**
For the standard mapping `d = zn·c`, so at a near plane around 1 the inverse's lower-right block is
nearly symmetric and the transpose passes too — measured indistinguishable at `zn = 1` and clearly
separated at `zn = 0.05` `[verified-numerically 2026-09-09]`. The row/column-major half still has to
be read off the numbers. Filed engine-agnostically to
`flat-to-vr-cross-engine-research/inbox/` as well, since it applies to any project identifying
matrix fields in memory.

Full write-up:
`modding-notes/2026-09-09-read-the-engines-own-projection-instead-of-guessing-it.md`.
