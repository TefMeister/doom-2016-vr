# `projconv` — turns `rvproj`'s raw numbers into a named convention, before the live run needs it

Filed by: `/pd` in the **tandem seat**, 2026-09-09, dev PC. **The game was not
launched and nothing here was run against it.** No file beside the game exe was
touched — the seat forbids deploying, and `build.sh` is deliberately unchanged.

---

## Why

The board's ⭐⭐ row ends: *"`** CONSISTENT **` ⇒ the convention stops being a
guess: **read it off the raw numbers** and build the per-eye matrix to match."*

That last step is a judgement made live, under time pressure, from sixteen
floats — and it decides how the per-eye matrix is built. This makes it a printed
answer instead.

It is the missing half of `projshape.c`. That file is a **search filter**: it
decides ROW vs COLUMN and recovers the two FOV angles, because its job is
rejecting millions of non-projections in a memory scan. `projconv` is a
**describer**, run on the one matrix already known to be real, and it answers
what `projshape` never needed to:

- **is depth reversed?** (near→1, far→0 — what idTech 6 is expected to use)
- **is the far plane infinite?**
- **what are near and far?**
- **is the frustum already off-axis?** ⚠️ this one matters directly: a per-eye
  matrix is built by putting an offset in exactly those slots, and a projection
  that already carries one must not simply be overwritten.

## Use it right now, without rebuilding the DLL

```
cd staging/doom-2016-vr/proxy-vulkan
clang -std=c99 -O1 -Wall -Wextra -o build/projconvtest.exe src/projconv.c test/projconvtest.c -lm
./build/projconvtest.exe                 # self-test
./build/projconvtest.exe <16 floats>     # describe a matrix pasted from the log
```

Worked example, a reversed-Z matrix in the shape `rvproj` prints:

```
$ ./build/projconvtest.exe 1.0 0 0 0  0 1.778 0 0  0 0 -0.00000763 1  0 0 0.0625 0
REVERSED [0,1], row-major | a=-0.00000763 b=0.062500 | near=0.06250 far=8191.35
                          | fov 90.00x58.71 deg, aspect 1.7780
```

**So the moment `rvproj` prints `** CONSISTENT **`, paste its sixteen numbers in
and the convention is named.** No rebuild, no relaunch.

## ⚠️ NOT wired into the DLL, on purpose

`build.sh` is untouched and `projconv.c` is **not** in the proxy's source list.
An `/lm` may be about to build and deploy, and changing the binary under a live
session is exactly what the tandem seat exists to prevent.

To wire it in later (a one-line change plus a call in `rvproj`'s printer): add
`src/projconv.c` to the `"$CC" -shared` list in `build.sh`, then call
`projconv_describe()` / `projconv_format()` on each matrix `rvproj` already
prints. **`[compile-verified 2026-09-09]` for the proxy target** —
`x86_64-w64-mingw32-clang -O2 -Wall -Wextra` compiles it clean, so wiring it in
will not produce a surprise build failure.

## Verification: 26 checks, 0 failures `[verified-numerically 2026-09-09]`

The tests never hand-write an expected matrix. Each convention is **built** from
a known near/far/fov by the formulae a renderer would use, then fed to the
describer, which must name it and recover the numbers it was built from — ground
truth constructed the other way round.

```
  standard [0,1], built from n=0.0625 f=8192.0 fovY=65.0:
  [PASS] named standard   [PASS] near recovered (0.06250)
  [PASS] far recovered (8192.06250)   [PASS] fovY recovered (65.00000)
  REVERSED [0,1] - what idTech 6 is expected to use:
  [PASS] named reversed   [PASS] far recovered (8192.00000)
  ... infinite far both directions, column-major storage, the [-1,1] trap,
      and five rejection cases ...
  ALL CHECKS PASSED (0 failures)
```

### ⚠️ Two things it will NOT tell you, and it says so in its own output

1. **[0,1] standard vs GL-style [-1,1] cannot be separated from one matrix.**
   The depth pairs have identical signs. Read as [0,1], a [-1,1] matrix gives
   the **correct far** and **exactly twice** the true near — the test pins that
   factor, so the warning is actionable rather than vague. The output carries
   the note whenever the ambiguity is live. DOOM renders through Vulkan, whose
   clip space is [0,1], so [-1,1] would be surprising — but surprising is not
   evidence and the code does not treat it as any.
2. **A premultiplied view-projection** (`m[15] != 0`) is reported as such rather
   than mis-read: near and far are not recoverable from one.

### Two real bugs the self-test caught before any launch

Both would have produced a confident wrong answer in the live session:

- **the "infinite far" epsilons were far too loose.** An infinite far plane puts
  `a` at exactly 1 or exactly 0; an ordinary finite one sits `n/(f-n)` away —
  **7.6e-6** for n=0.0625, f=8192. A tolerance of 1e-3, which looks generous
  rather than wrong, swallowed *every* finite projection and reported it as
  infinite, discarding the far plane. Now 1e-7, and the far recovery is done in
  **double**, because `a - 1` cancels six significant digits and in float the
  answer was noise.
- **the storage test refused readable matrices.** `b` is a general number, and
  for a near plane near 1 it lands close enough to 1 that *both* slots look like
  the ±1 marker — a matrix with n=0.5, f=1000 has b = −1.0005. Tightening the
  marker tolerance is not the fix, because `projshape.c` allows it slack on
  purpose (an infinite far plane with a depth epsilon sits slightly off 1).
  Instead both readings are now run through the classifier and the one that
  actually yields a convention wins; only if both do is it genuinely ambiguous.

## What is NOT established

- **Nothing here has seen a real DOOM matrix.** Every check is against
  synthetic matrices built in the test. It is `[verified-numerically]` that the
  describer inverts the standard formulae correctly — **not** that idTech 6 uses
  any of these conventions. That is exactly what the live `rvproj` run decides.
- The diagnostic that would show the *derivation* is wrong rather than a detail
  needing tuning: `rvproj` reports `** CONSISTENT **` (so the matrix is real and
  its inverse agrees) while `projconv` refuses it. That would mean idTech 6
  stores a projection in a form none of the five conventions covers, and the
  next question is its shape, not its epsilons.
