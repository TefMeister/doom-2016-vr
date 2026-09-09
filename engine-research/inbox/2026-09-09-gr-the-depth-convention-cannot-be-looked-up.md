# The depth/projection convention cannot be looked up — the ⭐⭐ read-the-matrix row is the only route

**From:** `/gr` (estate sweep, 2026-09-09) · **For:** the modding lane, as a one-line note against
the board's ⭐⭐ `[PD]` row and `ENGINE-DOSSIER.md`'s projection dead-ends

**Full write-up:** [`external-research/topics/2026-09-09-the-depth-convention-is-not-in-any-public-graphics-study.md`](../../external-research/topics/2026-09-09-the-depth-convention-is-not-in-any-public-graphics-study.md)

## The point in one paragraph

The board's ⭐⭐ row says four projection conventions have been tried and none reproduces the
engine's view, leaving a guess-space of reverse-Z / infinite far / row-column major / handedness at
one launch per guess. This pass went looking for a public statement of id Tech 6's actual depth
convention, which would have collapsed that space for free. **It is not there.** Courrèges' *DOOM
(2016) — Graphics Study*, Coenen's *DOOM Eternal* study and the idTech 666 SIGGRAPH talk were each
read against that exact question and none documents reverse-Z, the depth format, near/far handling
or the matrix layout `[reported 2026-09-09]`.

## What to do with it

- **Do not wait on research, and do not queue a research task for this.** Recorded as a searched
  negative on named sources so a later `/gr` does not re-spend a pass on it.
- The row's own reasoning is confirmed from the outside: reading the engine's real projection is not
  merely cheaper than guessing, it is the only route left.
- Worth reading first, and already in the dossier: **`cramZNear`** and **`flipProjection`** on the
  render view. Both imply the engine has explicit near-plane and projection-flip concepts of its
  own, which is exactly the kind of thing a convention guess would get wrong.

⚠️ Honest scope: this says three named sources do not answer it. It is not proof that no public
statement exists anywhere.

Credit: **Adrian Courrèges**, **Simon Coenen**, **Tiago Sousa & Jean Geffroy**.
