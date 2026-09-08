# 2026-09-08 — the ring's LEARN window is 53 MB short, §6c cannot be asked yet, and the camera global is cross-validated

`/lm`, dev PC, fully autonomous (the user launched nothing; they moved the mouse once by
accident, which changed only the view angle — position was unchanged and is evidenced below).

Evidence: `dev-archive/recon/2026-09-08-ring-window-53mb-short-and-6c-unaskable/`
(full proxy log, the console screenshot, and the two scripts written this session).

---

## 1. The console: a re-confirmation, a genuine cross-validation, and a stale board row

⚠️ **This section was written wrong first, and the correction is the point.** The first draft
led with "the console is NOT gated on retail" as a headline discovery. It is not a discovery:
**`ENGINE-DOSSIER.md` §9 has recorded the console as `verified live 2026-08-26` all along**, lists
`getviewpos` as "the camera ground-truth instrument", and records `g_fov 110` as a *working write*.
The draft was caught by reading §9 before committing. What follows is what is actually true.

### What was re-confirmed (modest)

Launched with **no** `+com_allowconsole 1`; `scan 0x29` opened the console, and:

```
]getviewpos
1762.94 5461.52 6367.59 31.5 0.3
```

`[verified-live 2026-09-08]`, which takes the console+`getviewpos` claim to **n=2 across two
sessions and two launches** (2026-08-26 and today). That is worth having and no more than that.

### ⭐ What IS new: the camera global is cross-validated

Before trying the console, the live position was read a completely different way — the module
base of `DOOMx64vk.exe` plus the dossier's §6h camera-global offset `+0x360F6B0`, through the
proxy's own `pdump`:

```
]pdump 0x7FF792DEF6B0
  +0:  1762.941  5461.524  6367.585  0.853
```

`getviewpos` then printed `1762.94 5461.52 6367.59`. **The engine's own console command and a raw
read at a statically-derived offset agree to printed precision.** `§6h` was carried on static
derivation plus live behavioural evidence; this is an independent instrument agreeing with it.
`[verified-live 2026-09-08, n=1, two independent routes]`

**Practical consequence: route (2) needs no console and no typing.** Given how badly typing into
the console behaves (below), `pdump` at module-base + `0x360F6B0` is the position read to
*automate*, not `getviewpos`.

### ❌ The stale row — and how it got stale

DOOM's `OPEN` block carried: *"optional cheap probe `+com_allowconsole 1`, ranked last on
purpose: even a won gate yields the stereo path's parameters, not its on-switch"*, and
`ai-game-control-profiles/profiles/doom-2016.json` said the console *"Needs +com_allowconsole 1 at
launch to be ungated; retail gates it."*

**Both are wrong, and the dossier never said otherwise.** §11's actual claim is much narrower:
`+com_allowconsole 1` is an *untested gate candidate* for the **cvars that are present in the
binary but never registered** — the `stereoRender_*` family, `noclip`, `rp`, `renameRenderProg`.
Console *access* was never the thing in question.

The failure mode is worth naming because it will recur: **a narrow, correctly-hedged dossier claim
("this flag might ungate the unregistered cvars") was copied into a board row and a profile as a
broader one ("retail gates the console")**, and then read as settled for a week. The board row is
the artefact a session actually acts on. Both are corrected. `[verified-live 2026-09-08]`

### ⚠️ Typing into the console is not reliable automation

The proxy's `type` burst-sent "getviewpos" and **one character** arrived. A paced external typer
(`recon/…/type-paced.py`, 45 ms key-down, 50–70 ms gap) got 7/10, then 3/3, then 1/1 — four
attempts to enter one command. Two later attempts landed **nothing at all**, most likely because
external `SendInput` follows focus and `SetForegroundWindow` is refused to a background process.

**The in-process route is the one to build**: the proxy's own `type`, one character per command,
so each lands on its own frame. `[PD]`. Until then, prefer `pdump` over `getviewpos`.

---

## 2. The ring path: the region fix WORKS, and the window is 53 MB short of the camera

`[verified-numerically 2026-09-08]`

This is the **third distinct cause** of the ring test's zero, and it must not be collapsed into
the previous two:

| date | claimed cause | status |
| --- | --- | --- |
| 2026-09-04 | `LEARN_CAP` too small (512 KB) | **`[disproved 2026-09-04b]`** — a full-span scan still matched 0 |
| 2026-09-04b | `ringcam` scanned the *biggest* mapping, not the one holding the copies | **fixed, and confirmed working today** |
| **2026-09-08** | **right region, but the LEARN *window* excludes the copies** | **new, measured** |

Today's LEARN printed exactly the line the fix was written to produce:

```
[ringcam] scanning region 2 (65536 KB) - value-located, not the biggest mapping
[ringcam] LEARN scanned [0..2832128) = 2765 KB of a 2765 KB offset span (not 64 MB):
          0 camera hit(s), 0 distinct delta(s)
```

Note "2765 KB **of a 2765 KB** offset span" — **LEARN was not capped.** It scanned the entire
window it was handed. The window itself is wrong.

`findvec 1728 5440 6372` located 64 copies in the same region in the same session. Region 2's
base is `0x00000282637E0000` (from `mappings`). Converting every hit to a region offset:

```
findvec hits    : 64
inside region 2 : 64 of 64
inside LEARN win: 0 of 64
offset range    : 0x3813950 .. 0x3C19F40   (56.08 MB .. 60.10 MB)
LEARN window    : 0x0 .. 0x2B3700          (2.70 MB)
nearest hit is 53.38 MB PAST the end of the scanned window
```

(arithmetic: `recon/…/hitoffsets.py`, run against the session log)

**Why this also explains the 2026-09-04 red herring properly.** `LEARN_CAP` was widened
512 KB → 8 MB. The copies are at 56–60 MB. **No value of `LEARN_CAP` would ever have worked**,
because the window's end is `g_offMax` — the largest *dynamic descriptor offset seen this frame*
— not the cap. Widening a ceiling cannot extend a window that ends far below it.

**The fix is small and static.** `camrescan` already discovered where the copies are —
`camstat` reports `cached offsets=122` this session — and `ringcam` already asks camhunt which
*region* to scan. It should take the *offset span* from the same place instead of from
`ringcam_onDynOffsets`. `[PD]`.

### Confounds ruled out, not assumed

- **The player had moved between `camseed` and `ringlearn`.** Not a confound: `readGlobalCam`
  (`ringcam.c:69`) reads the executable's live global at `+0x360F6B0`, not the seeded value, and
  it validates the basis row is unit length — `learn()` is not even called if that fails. It ran,
  so the live read was good.
- **"column 3 is not where the copies keep the translation"**, the other branch the log offers,
  is **untested** and remains open. The window result makes it moot for now: a predicate cannot
  match in bytes it never reads. It must be re-checked *after* the window is fixed, or the next
  session will collapse two causes again.

---

## 3. §6c is still not askable — and the reason is a print cap, not the offsets

`[verified-live 2026-09-08]`, and this **corrects the reading table** in the 2026-09-07 note.

That table said "`rvcheck` rejects every hit ⇒ the offsets are wrong, or `findvec` is not finding
`vieworg`; back to `[PD]`". **92 shape tests were run this session and 0 were accepted**, but
neither of those is the reason.

**(a) `findvec` cannot find a `renderView_t` even in principle.** It searches *GPU host-visible
mappings*. `renderView_t` is a CPU-side engine struct; it is not in a Vulkan staging buffer. All
64 `findvec` hits were rejected, 63 of them on "fov_x not a plausible angle" — which is what
reading uniform data through a struct layout looks like. The 2026-09-07 row's instruction to
`rvcheck` the `findvec` hits was never going to work.

**(b) The right search is `psearch`, and it found the values — but the candidate set is not
reachable.**

```
psearch 1728 5440 6372              -> 4465 candidates (image=8, private/heap=4457)
pnarrow 1762.941 5461.524 6367.585  ->  654 survivors
```

Two positions, a 6.8× narrowing, working exactly as designed. But `psearch.c` **prints only the
first 12 hits (`reported < 12`, line 115) and the first 16 survivors (`reported < 16`, line 170)**.
The full set lives in `g_hits[]` inside the proxy and is never exposed. `rvcheck` takes one
address at a time, read out of the log by a human.

**So the shape test could only ever be applied to 16 of 654 candidates — 2.4% — and the 16 that
happen to print are not a sample, they are the lowest addresses.** All 16 were in `000000BF3F…`,
which is thread-stack territory; a heap-allocated `renderView_t` would not be there.

**The fix is small, static, and uses only code that is already in the DLL:** a command that runs
`renderview_check()` over every entry of `g_hits[]` and reports the survivors — call it `rvscan`.
`g_hits[]` is in `psearch.c`; `renderview_check()` is in `renderview.c`; they are compiled into
the same binary. The 2026-09-07 verifier was built correctly — **it just has no way to be pointed
at the candidates.** `[PD]`.

---

## 4. Two defects found in the estate's own safety tooling, both fixed

Neither is about DOOM, both were found because this session used the tools:

1. **`claude-memory/tools/deployed.sh check` reported `GONE` for a file that was present and
   whose hash matched.** `deployed/<HOST>/*.tsv` was not covered by `.gitattributes`, so
   `core.autocrlf=true` checked it out with CRLF and every recorded path carried a trailing `\r`.
   The record had been written by a `/pd` session in its own clone root and reached this root
   through a pull. Fixed twice over: `*.tsv text eol=lf`, plus a defensive `${p%$'\r'}` strip.
   Verified: unpatched+CRLF → `GONE`; patched+CRLF → `OK`; patched+CRLF+wrong hash → `CHANGED`
   (it can still fail); all three real records for this host → `OK`.
   **This matters because a checker that cries wolf gets ignored**, and this one exists to stop a
   test being run against the wrong build.

2. **The staged `build/vulkan-1.dll` was two builds stale (169,472 B, the 2026-09-04c
   pre-region build), and `install-and-launch.bat` copies it unconditionally.** Running the
   launch script as-is would have **silently downgraded the deployed 2026-09-07 renderview
   build** and then tested against it. Caught by rebuilding first, as
   `feedback-verify-deployed-artifacts-by-hash` requires.

   Rebuilding then raised a second question: the fresh build's hash differed from the deployed
   one. A byte diff showed **6 differing bytes, all timestamp** — `0x80–0x82` (PE
   `TimeDateStamp`) and `0x17404–0x17406` (its copy in the export directory) — out of 178,176.
   So the deployed build *was* current. But it also means **`CONVENTIONS.md`'s "rebuild and
   compare the hash" check could not work on this project.** Fixed with
   `-Wl,--no-insert-timestamp`: two builds two seconds apart are now byte-identical, and the new
   build differs from the deployed 2026-09-07 one in exactly the 8 timestamp bytes and nowhere
   else. Deployed and re-stamped (`135c3f925ef5`).

3. (minor) `echo 1> "…\doom_automation_enable.txt"` is parsed by cmd as `echo` redirected to
   fd 1, so the marker file has always contained the literal text `ECHO is off.`. Harmless —
   `autocmd.c`'s `byFile` test is existence-only, and `DOOM_AUTOMATION=1` is what actually
   enabled automation today — but it reads as broken. Rewritten as `>"file" echo 1`.

---

## 5. Automation, scored by the four capabilities

| # | capability | verdict |
| --- | --- | --- |
| 1 | menu → gameplay | ✅ **proven again**, keyboard/scancode, 5 keypresses, every hazard screen captured and the highlight verified before committing (`SELECT CAMPAIGN` carries `[R] DELETE GAME SLOT`) |
| 2 | console / exec commands | ✅ **file command channel proven**; ⭐ **the in-game console is proven open and executing on retail** — but *typing into it* is not yet reliable (see §1) |
| 3 | character + camera | ✅ both routes moved the player — `hold w 2.0` and the ViGEm pad. ⚠️ **the waypoint counter is a bad odometer**: it moved 272.0 → 271.2 over ~41 world units, because the waypoint is not along the walk direction. Judge movement by `getviewpos`, not the HUD |
| 4 | self-close | ✅ **exercised, clean, no taskkill.** Quit through the game's own pause menu — `EXIT TO DESKTOP` → the confirm that defaults to No → `Yes` — with the highlight captured and verified at all three steps (`RESTART MISSION` sits three rows above the exit row). Process gone in under 8 s. **All four capabilities proven in one session.** The install stays a DEV BUILD: proxy deployed, `r_renderAPI 1`, nothing reverted |

---

## 6. What this session did NOT establish

- Whether the engine honours `explicitProjectionMatrix` (§6c). **Unchanged.** Not because
  anything failed, but because the candidate set cannot be reached by the verifier.
- Whether the ring copies keep the translation in column 3. Untested; blocked behind the window.
- Whether the console can **write** cvars.
- Whether a `renderView_t` exists among the 654 survivors at all.

---

## 7. ⚠️ `camwatch` costs ~60× the framerate — it is not a "leave it on" mode

`[measured 2026-09-08, n=1, boundaries aligned to the second]`

The user reported the game running at roughly one frame per two seconds. It was our
instrumentation, not the machine. From the proxy's own 1000-frame markers:

| frames | wall time per 1000 | FPS | state |
| --- | --- | --- | --- |
| 29000 → 34000 | 16.7 s | **~60** | normal |
| 34000 → 35000 | **889 s** | **~1.1** | `camwatch` on |
| 35000 → 36000 | 16.7 s | **~60** | after `camoff` |

`camwatch` was issued at 10:36:49 and `camoff` at 10:51:32; the slow interval is
10:36:48 → 10:51:37. The boundaries match the two commands to the second, and the recovery is
immediate and complete.

**Why this is worth writing down rather than shrugging at.** The dev PC's low power is
*expected and non-diagnostic* by standing rule, so a slowdown here is easy to dismiss as "this
machine". It was not: 60 → 1.1 → 60 is an instrumentation cost, and a 60× hit makes anything
requiring live play — driving, aiming, judging whether a projection change *looks* right — either
impossible or misleading. **Turn `camwatch` off the moment the reading is taken**, and never
leave it on across a `[FLAT]` test whose outcome is judged by eye.

⚠️ It also means the earlier `camstat` readings were taken from a game running at ~1 FPS. Nothing
in this session's conclusions depends on frame timing, so no result is withdrawn — but a future
timing-sensitive measurement taken with `camwatch` on would be worthless.
