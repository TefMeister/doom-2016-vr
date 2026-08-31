# 2026-08-31 — AUDIT: every claim from this session re-checked against the logs

**Why:** after the differential test turned out to have had no movement in it, the user asked
whether *other* early results were wrong for similar reasons. This is that sweep — every claim made
today, checked against the archived session logs rather than memory.

Result: **one further claim withdrawn, one nuance recorded, and eleven confirmed sound.**

---

## ❌ WITHDRAWN — `postmessage` does not work

`[disproved 2026-08-31 — untested, not disproved]`

The evidence was a screenshot test in run 1 showing no movement. The log shows why that proves
nothing:

```
13:51:02  move ... via sendinput      -> 257.0 -> 255.8   (only 1.2 m)
13:51:06  move ... via postmessage    -> tested 4 s later
```

The **sendinput** move immediately before it managed only **1.2 metres**, because the player was
**jammed against a cave wall** — a fact I noted at the time and then failed to apply to the very
next test. `postmessage` was then tested from that same obstructed position, four seconds later.

A working backend and a dead one look identical when the player cannot move. **`postmessage` is
untested on DOOM.** Re-test it from open ground.

## ⚠️ NUANCE — the bisection has not actually narrowed anything yet

Round 1 *was* a valid bisection step:

- set A (765 candidates) held → **effect**
- set A's first half (382) held → **no effect**
- ⇒ the culprit is in set A's second half (383 addresses). **This inference is sound.**

Round 2, however, was **not a continuation**. It rebuilt from scratch (a fresh `psearch` gave 2579
→ 605) and tested *that* set's second half (303). So it corroborates that the effect is real and
reproducible across two independent searches — genuinely useful — but it did not halve anything.

**Net position: the effect is confirmed twice; the search is still at ~383 candidates, not 303.**

**Practical consequence worth recording: candidate sets do not survive a game restart.** Addresses
are heap pointers from one process. A bisection has to be completed inside a single session, which
is exactly what `pother` now makes feasible (~8 rounds, no rebuilds).

---

## ✅ CONFIRMED SOUND — re-checked, evidence holds

| Claim | Why it survives |
|---|---|
| **The probe metric is unreliable** | It scored `sendinput` "no clear reaction" (134 vs control 274) during the very phase in which sendinput walked the player ~15 m (271.9 → 257.0). A genuine false negative. Note the *reason* is corrected: the 15 m was sendinput's, not inproc's. Its "no reaction" verdict for `inproc` was, ironically, **correct**. |
| **`inproc-keystate` does not work** | Two isolated tests, zero movement, plus the mechanism: `DirectInput8 CreateDevice(SysKeyboard)` is logged, so gameplay keyboard bypasses the Win32 key-state calls we hook. |
| **`sendinput` drives movement and look** | Movement 271.9 → 232.7 (~40 m) in isolation; look swung the view fully round and an equal-and-opposite injection returned it to the same compass position. |
| **Scans were pathologically slow (write-combined memory)** | Measured 3 m 45 s; the staging-buffer fix produced ~56× (→ ~4 s), which *confirms* the diagnosis rather than merely being consistent with it. |
| **Scans no longer freeze the game** | 51 fps during a background scan vs 3.6 fps inline, back to 60 after. |
| **The camera transform is in the per-frame uniform buffer, position in column 3** | Matched `getviewpos` exactly at two independent positions. Independent of any input mechanism. |
| **`getviewpos` prints yaw then pitch** | Derived arithmetically from the measured matrix (34.3° about Z = cos 0.826 / sin 0.563; asin 0.060 = 3.4°). |
| **DirectInput binds physical scancodes; VK_OEM_3 → 0x28 here, console is on 0x29** | Measured directly with `MapVirtualKey`, then confirmed by the console actually opening. |
| **The camera buffer is `HOST_COHERENT`** | 7 flushes in ~10 s of gameplay against 24,155 accumulated mostly at load. The flush-rate datum stands on its own, independent of the lock. |
| **The GPU-side copy is downstream of rendering** | Three independent legs: zero hits for *both* predicted inverse-view translations; the transposed rotation basis exists nowhere as consecutive floats; patching camera-to-world across 72 per-draw blocks moved the image 1–2%. **Does not depend on the withdrawn differential claim.** |
| **`psearch` was matching NaN** | Fixed comparison changed the count from 1,048,576 to 2,218 — the fix's effect is the proof. |

---

## The pattern across all three withdrawals

Every one was a **setup** failure, not an analysis failure:

1. **Differential** — the independent variable (walking) was applied through an inert mechanism.
2. **Attribution** — three backends changed before a single observation.
3. **`postmessage`** — the test ran under a condition (player obstructed) that guarantees a null
   result regardless of the mechanism.

In all three the measurement was fine and the reasoning from it was fine. What was wrong was the
state of the world when the measurement was taken. That is the thing to check first, and it is
cheap to check: a screenshot before the test, not only after.

**Standing rule going forward, added to the dossier:** before a negative result is recorded as a
fact, confirm the test *could* have produced a positive one — that the mechanism works, that only
one thing changed, and that the game was in a state where the expected effect was possible.
