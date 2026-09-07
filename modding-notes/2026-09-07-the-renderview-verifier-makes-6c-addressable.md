# 2026-09-07 — a hit can now be VERIFIED as a `renderView_t`, and §6c is one command away

`/pd`, dev PC. **The game was not launched, and nothing here has been run.**

Closes the `[PD]` row opened 2026-09-05. Evidence:
`dev-archive/recon/2026-09-07-renderview-verifier/`.

---

## 1. What was missing

Walking the reflection database on 2026-09-05 produced the layout — from a `findvec` hit `A` on
`vieworg`, `fov_x` is at `A-80`, `useExplicitProjectionMatrix` at `A-4`, and
`explicitProjectionMatrix` at `A-68`. What it did **not** produce was any way to tell whether a
given hit actually *is* a `renderView_t`. `findvec 1728 5440 6372` returns dozens of camera-shaped
hits; writing `explicitProjectionMatrix` into the wrong one writes 64 bytes into whatever that
memory really is.

So the gap was never the offsets. It was that identification was an **assumption**.

## 2. What was built

`src/renderview.{c,h}` — a pure shape test — and `src/renderview_cmd.c`, the memory-safe command
layer. Four commands:

| command | does |
| --- | --- |
| `rvcheck <hexaddr>` | is this hit shaped like a `renderView_t`? Prints every field it read and, on rejection, **which test failed** |
| `rvmat <hexaddr>` | read `explicitProjectionMatrix` as a 4×4 |
| `rvexplicit <hexaddr> on\|off` | **the §6c experiment**: flip `useExplicitProjectionMatrix` |
| `rvsetmat <hexaddr> f1..f16` | write the 4×4, row-major |

Both writers **refuse unless `renderview_check` passes**, so the "wrong hit" failure mode needs an
explicit override rather than a slip.

The shape test:

- `vieworg` finite (NaN and ±inf rejected)
- `fov_x`, `fov_y` each finite and in `(1°, 179°)` — a deliberately **wide** bound, because
  rejecting the real struct costs far more than admitting a decoy
- the two fovs consistent as one frustum (`hi ≤ 6 × lo`) — this catches pairs that pass
  individually but cannot describe a single view
- `useExplicitProjectionMatrix` and `forceIdentityViewMatrix` each exactly 0 or 1 — **the cheapest
  and strongest discriminator**, at roughly 1/128 per byte on random data
- a coarse 0–100 confidence, so several survivors can be ranked rather than treated as equal

## 3. How well it is known

`[compile-verified 2026-09-07]` for the DLL — 246 exports, all 96 imports `DOOMx64vk.exe` needs.

`[verified-numerically 2026-09-07]` for the shape test: **22 checks, 0 failures**, run against
**the shipped `renderview.c`** rather than a transcription, with no game and no process memory.

**The number that matters: 0 of 20,000 random-memory windows passed.**

⚠️ **And what that does not mean.** It bounds the false-positive rate; it does not make it zero.
The expected count was already well under one, so 0 is unsurprising rather than remarkable. More
importantly: **a shape match is not proof.** A buffer of plausible floats with two 0/1 bytes in the
right places passes too. `rvcheck` says "looks like", and the command output says so in those words.

The positive control is test 1 — a struct built from the real `getviewpos` reading in §6e is
accepted. Without it a filter that rejected *everything* would also have scored 0/20000, which is
the trap this suite is shaped to avoid.

## 4. What is NOT established

- **That any of this is the live view.** The offsets are `[inferred-static 2026-09-05]` from the
  reflection tables. Nothing has been read out of a running DOOM.
- **That the engine honours `explicitProjectionMatrix` at all.** That is §6c's open question and the
  entire point of the experiment; this work makes it *askable*, not answered.
- **The per-eye override maths.** Dossier §6 still records `K_eye = …` as TBD pending 6c, and this
  changes nothing about that.

## 5. The one command to run next time DOOM is up, and what each outcome means

Prerequisite unchanged: `camseed` + `camrescan` first — `ringcam` needs the seed, and the board row
above says so.

```
findvec 1728 5440 6372          (or the current getviewpos reading)
rvcheck <each promising hit>    -> keep the ones that say LOOKS LIKE, note the confidence
rvmat <the best hit>            -> read the matrix before touching it
rvexplicit <that hit> on
```

| what you see | what it means |
| --- | --- |
| **the projection visibly changes** (FOV jump, skew, or a broken frustum) | ⭐ **`explicitProjectionMatrix` is honoured on the world view** — §6c is answered YES and a per-eye projection is a supported engine input rather than something to patch in. This is the categorically easier project the dossier hoped for |
| **nothing changes at all** | three different findings, and they must not be collapsed: the hit is not the live view; or the flag is re-set every frame by the engine; or the engine ignores it on this view. `rvcheck` the hit again after a few seconds — if `useExplicit` has gone back to 0 by itself, it is the second |
| **`rvcheck` rejects every hit** | the offsets are wrong, or `findvec` is not finding `vieworg`. That is a static problem, back to `[PD]` |
| **a crash** | the write went somewhere that was not a `renderView_t`. The shape test is a filter, not a proof — say which address |

`rvexplicit ... off` reverts, and the flag write is one byte.
