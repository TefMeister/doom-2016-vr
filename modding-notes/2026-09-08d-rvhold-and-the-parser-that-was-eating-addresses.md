# `rvhold`, and the parser that was silently eating addresses

`/pd`, dev PC, 2026-09-08d. **The game was not launched. Nothing in this note has been run.**

Source: `staging/doom-2016-vr/proxy-vulkan/`. Deployed `vulkan-1.dll` md5 `74944db5…`, 195,584 B,
dated backup kept.

## Two `[PD]` rows, and they turned out to be the same session's work

The ⭐⭐ row asked for `rvhold`. The other asked why `rvcheck` and `rvmat` reject the address format
`rvscan` itself prints. They belong together, because **the second bug would have made the first
command unusable the moment anyone typed it.**

---

# 1. The parser was reading addresses as OCTAL

`rvcheck` and `rvmat` parsed their argument with `strtoull(s, NULL, 0)`. **Base 0 means "infer the
base from the prefix", and in C a leading zero infers OCTAL.** Every address this proxy prints comes
from `"%p"`, which on win64 is zero-padded to 16 digits:

```
rvscan prints    00007FF767CBF6B0
strtoull base 0  reads 0000 as an octal prefix, takes the 7, stops at the first F
returns                         7
```

`[verified-numerically 2026-09-08]` — reproduced as a host test, which asserts both the correct
value **and** that the result is no longer the old `7`.

That single defect produced both reported symptoms, which is why they looked like two different
problems:

| symptom | what was actually happening |
| --- | --- |
| `rvcheck` prints its **usage** line | the address parsed to 0, and `renderview_cmdCheck` prints usage on a NULL `A` |
| `rvmat` says **`window not readable`** | the address parsed to a small integer, and that window genuinely is not readable |

**Neither command was rejecting the address. The address never reached the command.** The `rvmat`
form is the worse of the two: it reports a fact about memory when the truth is a fact about parsing,
so it reads as evidence about the game.

**The fix** is `src/hexaddr.c` — a pure parser that is **always hex, never inferred**. It takes the
padded form, the `0x`-prefixed form and the bare form; skips leading blanks; ignores trailing text
(so `rvexplicit <addr> on` still works); and **refuses** rather than guessing on empty input, on
non-hex, on a bare `0x`, and on a value too large for 64 bits. Refusing overflow matters here
specifically: a wrapped value is a plausible-looking pointer to the wrong place, and these commands
**write**.

It is its own file precisely so `test/rvtest.c` exercises **the shipped parser**. 14 new checks.

### The test caught a real mismatch in my own code

`hexaddr.h` says *"`0x` on its own is not an address"*. My first implementation returned `0` with
`ok=1` for it — it parsed the `0` and treated the `x` as ignorable trailing text. **The header
documented the stricter behaviour and the code did not implement it**, and the check I had written
for that line failed. Fixed in the implementation, not by relaxing the test: a bare prefix is a
typo, and returning zero-and-ok would hand a command the address 0 and let it report "not readable"
— *the same silent misparse this file exists to remove, one layer down*.

---

# 2. `rvhold` — the only form of the §6c experiment that can produce a meaningful negative

## Why the old command could never have answered it

2026-09-08c ran `rvexplicit <addr> on` and the picture did not change. That was recorded as a
possible *"the engine ignores the flag"*. **It could not have meant that**, for two measured
reasons:

1. **The whole `renderView_t` is rebuilt under us.** Written values read back intact in the same
   command tick and were **all zero by the next round-trip** (~18 s, ~1100 frames), while `vieworg`
   tracked the player throughout — so the struct is live and being rewritten, not the wrong struct.
   `[measured 2026-09-08, n=2 writes]`
2. **`explicitProjectionMatrix` is all zeros at rest.** So setting the flag alone — all the old
   command did — could only ever have pointed the engine at a **degenerate** projection. An
   unchanged picture is the expected outcome of that *even on an engine that honours the field
   perfectly.*

So the experiment has to write **the matrix and the flag, every frame**. That is `rvhold`.

## What makes a negative readable — the part that matters

If the picture still does not change, that is *still* two different findings, and the old command
could not tell them apart. So before each write, `rvhold` reads back what is actually there and
classifies it:

| verdict | meaning |
| --- | --- |
| **`HELD`** | what we wrote last time is still there — our value survived a whole frame, so an unchanged picture means the engine **really does not read this field on this path**. That is the §6c answer. |
| **`ZEROED`** | the matrix is all zeros again — the engine clears the struct between our writes. We are writing at the wrong point in the frame and **nothing about §6c has been learned.** |
| **`REWRITTEN`** | neither — something else owns the field. Also not a §6c answer. |

Without this, "unchanged" is uninterpretable — which is exactly the state the project was left in.

**The counters are kept per hook site**, because writing at two points and reporting one number
would hide the case that localises the engine's rebuild: held at one site and zeroed at the other.

## Where it writes, and why two places

- **`vkQueuePresentKHR`** — the frame boundary, alongside `psearch_onFrame`.
- **`vkQueueSubmit`** — which `proxy.c` already documents as landing *"after the game has written
  the frame's camera and before the GPU reads it"*.

We do not know where in the frame the engine builds its projection, so guessing one point and
reporting silence would repeat the 09-08c mistake. Writing at both and **counting each separately**
turns that uncertainty into data.

## The matrix it holds

Derived from the struct's **own live `fov_x`/`fov_y`**, defaulting to **half the live `fov_x`** — a
2× zoom, chosen to be unmistakable. Taking both angles means the aspect ratio is *recovered*
(`tan(fovX/2)/tan(fovY/2)`) rather than assumed, so the held projection matches the real viewport
instead of a guessed 16:9. Assuming an aspect is how a test produces a stretched image and gets read
as "the engine honoured it".

⚠️ **The matrix convention is a guess, and deliberately does not need to be right.** It writes the
common right-handed, 0..1-depth form; idTech 6 may use reverse-Z, an infinite far plane, or the
transpose. The question being asked is *"does the engine read this field at all"*, and **any visible
change — including a wrong-looking one — answers it yes.** Only the follow-up work of building a
correct per-eye projection needs the convention, and this test decides whether that work is worth
doing at all.

## Safety

- Refuses any address that fails `renderview_check`, or whose window is not readable.
- Makes the 65-byte matrix+flag span writable **once, at arm time** — the per-frame write is on the
  present/submit path, where a `VirtualQuery`+`VirtualProtect` pair would cost more than the copy it
  guards. `psearch`'s `phold` takes the same approach for the same reason.
- **Snapshots the original matrix and flag before the first write and restores them on release**, so
  a session does not end with a degenerate projection latched into a live struct.
- Bounded: default 3,600 frames (~60 s), hard cap 36,000. It is an experiment, not a mode.
- **A race the second hook site created, found in self-review.** With writes at *two* hook points
  plus `rvholdoff`, the target pointer is read by callers that are not guaranteed to be the same
  thread — so a write could use a pointer `rvHoldRestore` had just cleared, or land *after* a
  restore and latch the degenerate matrix back in, silently breaking the promise that release puts
  the engine's own values back. The pointer is now read once into a local and `g_rvHoldOn` is
  re-checked immediately before the write. ⚠️ **That narrows the window rather than closing it** —
  a lock on this path would cost more than the 65-byte copy it guards, and the residual worst case
  is one extra write to a struct the engine rebuilds every frame anyway. Recorded rather than
  papered over.

---

## Verification

- Builds clean under `-Wall -Wextra`; 265 exports; **covers all 96 imports `DOOMx64vk.exe` needs**
  `[compile-verified 2026-09-08]`.
- Host suite: **52 checks, 0 failures** (was 38) — 14 for the parser, including an explicit
  assertion that the old octal result of `7` is gone, and 12 for the projection maths, checked
  against independently computed `1/tan(θ/2)` values plus a trig-free anchor (fov 90 ⇒ exactly 1.0)
  and a check that every entry outside the five set is exactly zero, so a half-filled matrix of
  stack junk can never be written into a live engine struct. `[verified-numerically 2026-09-08]`
- **The deployed binary was verified before being overwritten**: a fresh build of the pre-session
  source is md5-identical to what was installed (`e3c896f9c8fe…`), so the stamp was honest.
  `[verified-numerically 2026-09-08]`

**Nothing here has been run in the game.**

## The next launch, and what each outcome means

```
rvscan                          (or reuse an address it printed earlier)
rvhold <addr>                   arm it — LOOK AT THE PICTURE
rvholdoff                       release, and read the counters
```

⚠️ **Set the input backend first**, from 09-08c: `backend sendinput` + `typeroute sendinput`. The
default `inproc-keystate` never lands, and a command that silently does nothing reads exactly like
the game ignoring it.

| what you see | what it means |
| --- | --- |
| **the picture changes at all** — even to something wrong or broken | **§6c ANSWERED YES.** The engine honours `explicitProjectionMatrix`, per-eye projection is a supported input, and this becomes the categorically easier project. |
| unchanged, counters **`HELD`** dominant | **§6c ANSWERED NO.** Our matrix survived whole frames and the engine did not read it. Fall through to the command-buffer resubmission route. |
| unchanged, counters **`ZEROED`** dominant | **§6c still unanswered.** We are writing at the wrong point; the engine clears the struct between our writes. Next build moves the write earlier — the view-setup path, not present/submit. |
| unchanged, **`REWRITTEN`** dominant | Something else owns the field. Identify the writer before anything else. |
| **`rvhold` refuses** | the address failed the shape test, or is not writable. Re-run `rvscan`. |

## What is NOT established

- That the engine honours the flag, or that it does not. **That is what this is for**, and it is
  untested.
- That present and submit are the right write points. The `ZEROED` verdict exists precisely because
  they may not be.
- That the projection convention is correct. See above — it deliberately is not load-bearing.
