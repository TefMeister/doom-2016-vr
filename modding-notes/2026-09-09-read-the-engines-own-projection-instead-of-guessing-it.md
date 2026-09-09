# Read the engine's own projection instead of guessing it — and the top board row was already done

**2026-09-09, dev PC, `/pd`, NO LAUNCH.** The game was not launched and nothing here has been run.

---

## Two results, and the second is the one that matters

### 1. The board's ⭐⭐ `[PD]` row was already closed 21 minutes after it was written

The row read *"DROP `uniscan`'s `m[15]=0` requirement — this is now the critical path"*. **That work
was already in the shipped code before the row was written.**

| time | lane | what |
| --- | --- | --- |
| 2026-09-08 19:38 | `/pd` | `acb7c66` — dropped the `m[15]==0` hard reject; `projshape.c` gained the premultiplied view-projection branch. Its own note says *"the last `[PD]` row is closed"* |
| 2026-09-08 19:59 | `/lm` | `5c352ec` — wrote an `OPEN` block re-raising a `[PD]` row asking for exactly that |

`projshape.c` today treats `m[15]` as *selecting which shape to look for*, not as a reject. Checked
against the row's stated asks: premultiplied VP **covered**; reverse-Z and infinite-far **covered**
(both keep the ±1 that `rowLike`/`colLike` tests, only `m[10]`/`m[14]` move); row- and column-major
**both covered**; handedness **covered** (the tests use magnitudes). A packed 3×4 is not covered, and
is not a plausible storage form for a projection. `[verified-numerically 2026-09-09]`

**The row is removed, not done-by-me.** Auto-pick walks straight into a stale row where a human
skims past it, so this is worth the paragraph.

### 2. ⭐⭐ The projection can be READ. It has been readable statically since 2026-09-05.

The critical path says *"if the engine's real projection can be READ, the convention stops being a
guess"*. It has been attacked by **guessing** (four conventions, four launches, all failed) and by
**shape-searching GPU memory** (`uniscan`). Meanwhile §6d's reflection-database walk had already
enumerated `idRenderView` **with byte offsets** on 2026-09-05 `[verified-numerically 2026-09-05]`:

```
idRenderView (sizeof 5616)
  +0     g   renderView_t       "set by the game"
  +2272  r   renderView_t       "latched from 'g' at EndFrame time"
  +4400  projectionMatrix          <-- this
  +4528  inverseProjectionMatrix   <-- and this
  +4592  viewMatrix
  +4720  worldSpaceMVPMatrix
```

The engine's own, already-built projection has been at a computable address the whole time, and
nobody had gone and looked at it.

## `rvproj <hexaddr>` — what it does

From an `rvscan` survivor `A` (a `vieworg` hit, which sits +96 inside a `renderView_t`), the
enclosing `idRenderView` is one of two placements, so **both** are read:

| if the hit is | `projectionMatrix` at |
| --- | --- |
| `idRenderView::g` | **`A + 4304`** |
| `idRenderView::r` | **`A + 2032`** |

It prints `projectionMatrix`, `projectionMatrixNoJitter`, `inverseProjectionMatrix`, `viewMatrix`
and `worldSpaceMVPMatrix` **raw**, for each placement.

**The struct decides which placement is right, not us.** It carries the inverse alongside the
matrix, so `projectionMatrix × inverseProjectionMatrix` must be the identity — checked both
multiplication orders, worst error taken. **0 of 200,000 random matrix pairs pass**, while a genuine
pair passes at every plausible near/far, including **reverse-Z with an infinite far plane** — the
case the remaining guess-space is full of. `[verified-numerically 2026-09-09]`

That is what makes a hit an identification rather than "plausible floats at a computed address": it
is a second independent *use* of the same memory, not a second identical read.

**It reads only.** No writes, no `useExplicitProjectionMatrix`, no conclusion about what to *send*.

## ⚠️ What the consistency test does NOT settle — and it was a wrong assumption of mine

I wrote a test asserting the transposed inverse would be rejected. **It passed**, and the reason is
structural rather than a sloppy tolerance. For

```
P = [[a,0,0,0],[0,b,0,0],[0,0,c,-1],[0,0,d,0]]
```

the inverse's lower-right block is `[[0, 1/d],[-1, c/d]]`, and the standard mapping gives
**`d = zn·c`**. So when the near plane is near 1, `1/d` is near −1 and that block is very nearly
**symmetric** — no tolerance loose enough to accept a real float32 inverse can separate it from its
own transpose.

Measured both ways rather than argued: **indistinguishable at `zn = 1` (error 1e-4), clearly
separated at `zn = 0.05` (error 19)**, exactly as `d = zn·c` predicts.
`[verified-numerically 2026-09-09]`

**So a `CONSISTENT` verdict means the right two fields were found. It says nothing about
row/column-major.** That is answered by reading *which element carries the −1* in the printed
matrix — which is why every matrix is printed raw, and why the command says this in its own output
rather than leaving it in a header.

## What is NOT established

- **That any given `rvscan` survivor is inside an `idRenderView`.** The offsets are verified; the
  identification of a hit is exactly what the inverse-pair test settles per-hit. A survivor failing
  both placements is more likely the wrong survivor than a wrong offset. `[hypothesis]`
- **That `+4400` is populated at the moment `rvproj` runs.** The `g`→`r` latch happens at EndFrame;
  a matrix read at the wrong point in the frame could be stale or zero. Zeros would be obvious in
  the output, so this fails loudly rather than silently — but it is untested. `[hypothesis]`
- **Nothing about which convention to SEND.** Reading the matrix tells us the shape the engine
  *produces*. `rvhold` writes into `explicitProjectionMatrix`, which is a different field, and
  2026-09-08h showed that path inverts the focal term. Matching the read shape is the obvious next
  move and is not proven to be the right one.

## Folded in from `/gr` (inbox drained: 1 file)

`2026-09-09-gr-the-depth-convention-cannot-be-looked-up.md` → dossier §6n-2. Courrèges' *DOOM (2016)
Graphics Study*, Coenen's *DOOM Eternal* study and the idTech 666 SIGGRAPH talk were each read
against this exact question and **none documents reverse-Z, the depth format, near/far handling or
the matrix layout** `[reported 2026-09-09]`. Recorded as a searched negative on named sources so no
future `/gr` re-spends a pass. It confirms §6n from the outside: reading the matrix is not merely
cheaper than guessing, it is the only route left. Credit: **Adrian Courrèges**, **Simon Coenen**,
**Tiago Sousa & Jean Geffroy**.

## Build and deploy

Deployed `vulkan-1.dll` sha256 `fef97dd4…`, 213,504 B, backup `vulkan-1.dll.bak-2026-09-09`
(previous `c26b1811…`). `deployed.sh record` re-run. **Two builds of identical source hash
identically**, and a rebuild after deploying matched the installed file byte for byte. Host suite
`rvtest.exe`: **116 checks, 0 failures** (up from 98); export count 265, all 96 imports DOOM needs
present.

## The one command to run next time DOOM is up

Reach gameplay, then the existing chain, then one new command:

```
psearch <x> <y> <z>     (at one position)
pnarrow <x> <y> <z>     (after moving)
rvscan                  (prints survivors, strongest first)
rvproj <addr>           (the new one — on the strongest survivor)
```

| what `rvproj` prints | what it means |
| --- | --- |
| `** CONSISTENT **` under `g` or `r` | **the engine's own projection is on screen.** Read the convention off the numbers — which element holds the −1, whether the depth row is reverse-Z — then build the per-eye matrix to match. The guessing stops here. |
| both placements inconsistent | that survivor is probably not inside an `idRenderView`. Try the next survivor before doubting `+4400`. |
| all zeros | the field is not populated at this point in the frame — the `g`→`r` latch timing matters, and the read needs moving. |
