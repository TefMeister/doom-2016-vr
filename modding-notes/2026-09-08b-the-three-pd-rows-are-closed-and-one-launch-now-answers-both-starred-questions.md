# 2026-09-08b — the three `[PD]` rows are closed, and one launch now answers both starred questions

`/pd`, dev PC, **the game was not launched and nothing here has been run.** Everything below is
compile-verified, and two host suites run against the shipped code with no game, no Vulkan and no
window. Every claim about what DOOM will *do* with this is a hypothesis until someone launches it.

Source: `staging/doom-2016-vr/proxy-vulkan/` (private). Deployed build
`3eae8b6fc648`, 189,952 B, stamped in `claude-memory/deployed/DESKTOP-V8GTSIR/`.

---

## 0. Pre-flight, and one thing it confirmed

`deployed.sh check` said `OK`, which only means the install still matches its stamp. The stronger
check — rebuild and compare — was run as well, and the incoming build was **byte-identical** to the
deployed one `[verified-numerically 2026-09-08]`. That is the first time that check has been able to
work on this project: `-Wl,--no-insert-timestamp` was only added yesterday, and before it two builds
of identical source differed in six timestamp bytes. So the 2026-09-07 renderview build really was
current, and nothing was tested against a stale binary.

Inbox: empty. `external-research/` re-checked: no new posts.

---

## 1. ⭐⭐ `rvscan` — the verifier now sees the whole candidate set

The 2026-09-08 finding was that §6c was blocked by a **print cap**, not by the offsets and not by
`findvec`. That is confirmed by reading the code, and the fix is what was predicted: both halves were
already compiled into the same DLL and had no way to be introduced to each other.

- `psearch.c` gains `psearch_hit(i)` — bounds-checked, `NULL` out of range.
- `renderview_cmd.c` gains `renderview_cmdScan()`, dispatched as **`rvscan [n]`**.

It tests **every** candidate, ranks the survivors by the confidence score `renderview_check()`
already computed, prints the best 24 strongest-first, and then prints the exact next commands to run
on the strongest one. What it prints is the thing the next live session was going to have to
assemble by hand from a log.

**The verdict histogram prints even when nothing passes**, and that is deliberate. "All 654 failed on
`fov_x`" and "654 failed across five different tests" are different findings — the first is what
reading unrelated data through this struct layout looks like, the second means the set is mixed and
the layout is the next thing to question. A mute zero says neither, and a mute zero is what the
2026-09-07 session had to interpret.

**What is NOT established.** That any survivor is the live `renderView_t`. The shape test is a
filter, by its own documentation. What can be said is how *leaky* a filter: `rvtest` fires 20,000
random windows at it and **0 pass** `[verified-numerically 2026-09-08, n=20000]`. So a survivor is
not noise — but "not noise" is a long way from "the live view", and only changing something and
watching the picture closes that gap.

Two guards worth naming:

- `rvscan` refuses to run while `camhunt_scanBusy()`, because `psearch_scan` runs on a background
  thread and `rvscan` runs on the render thread. Every dereference is guarded by `window_ok()`, so
  this is not a safety fix — it is so the printed count is reproducible.
- Candidates whose window straddles the end of a region are counted as **unreadable**, separately
  from shape rejections. Lumping them together would overstate how many real rejections the layout
  produced.

---

## 2. ⭐ The ring's LEARN window now comes from where the copies actually are

The measurement from earlier today: the window was `[0..2832128)` = 2.70 MB, taken from this frame's
dynamic descriptor offsets, and the 64 copies sat at 56.08–60.10 MB — the nearest **53.38 MB past the
end** `[verified-numerically 2026-09-08]`.

`camhunt.c` gains `camhunt_cameraOffsetSpan(region, …)`, which reports the min/max offset of the
copies **discovery already recorded** for that region. `ringcam`'s `learn()` takes its window from
there, padded a block either side — exactly as it already takes the *region* from the same
discovery. The old dynamic-offset window survives only as a fallback, and it now says out loud that
it is the window measured wrong today and that `camseed` + `camrescan` should be run first.

### ⚠️ The part that is more interesting than the fix

Fixing the window exposes a problem the old window hid. `PROBE` works by learning a **delta** from a
bound dynamic offset to a camera copy, then reading `offset + delta` every frame. If the copies are
at 56 MB and the highest bound offset is 2.7 MB, then every "delta" is ~53 MB — which is not a
block offset, it is the arithmetic you get when the nearest anchor is nowhere near the target.
Recording one would make `PROBE` read a fixed distance past every offset for the rest of the session.

So `learn()` now **rejects** a delta above `DELTA_SANE` (256 KB) rather than recording it, and
separates the outcomes:

| what LEARN reports | what it means |
| --- | --- |
| hits, usable deltas | as designed; `ringyaw` / `ringeye` can drive |
| **hits, but all deltas too far** | the copies are in the region but **not in the per-draw block range the game binds** — `offset+delta` probing cannot reach them *however the window is set*. A verdict on the strategy, not a tuning problem |
| no hits, in a window that *does* cover the copies | the remaining untested branch: **column 3 is not where these copies keep the translation** |

That middle row is a live possibility, not a prediction — it is what the 53 MB gap would imply if
the dynamic offsets stay where they were today. It is written into the log so the next run
distinguishes it instead of producing a fourth ambiguous zero. `[hypothesis]`

⚠️ **This is the third distinct cause of that test's zero and must not be collapsed with the first
two** (cap, wrong region). Both of those are fixed and confirmed. The second hid behind the first for
four days, precisely because a fix that removes a symptom reads as an explanation.

---

## 3. Console typing: two defects, and four routes to measure

The board row said `type` "burst-sends". **It does not**, and the correction matters because it
points at a different fix. `autoinput_pumpKeys()` has always played one tap per frame with a hold and
a gap. Two other things were wrong.

### (a) The pacing was in frames, and frames are not a unit of time

`HOLD_FRAMES` was the constant **3**. At 60 fps that is a 50 ms hold — long enough for a 60 Hz poll,
short enough to stay under the ~250 ms Windows auto-repeat delay. But today's other measurement was
that **`camwatch` costs ~60× the framerate** (60 → 1.1 → 60 fps), and `type getviewpos` was issued at
10:44:32, inside the slow window. At 1.1 fps those same three frames are a **2.7-second hold**, and
ten characters take ~45 s to play out.

That is a much better fit for "one character arrived" than burst-sending: the string was very likely
still playing. It is `[hypothesis]` — nobody re-read the console 45 s later — but it is a hypothesis
that predicts the observation, and the old code cannot produce a correct hold at that frame rate
under any constant.

Pacing is now derived from the **measured** frame period, in `autoinput_paceFrames()`, which is pure
and host-tested. At 60 fps it yields 3–4 frames (GetTickCount quantises the period to 15/16/17 ms),
i.e. 50–67 ms — what the old constant gave. At 1.1 fps it yields 1 frame: 0.9 s instead of 2.7 s.

**A limit that no pacing can fix, and it is worth stating plainly:** the pump runs once per present,
so a tap can never be held for less than one frame. Below ~4 fps even a single-frame hold exceeds the
auto-repeat delay. The proxy now says so, once, when it matters. **Turn `camwatch` off before
typing** — the same conclusion §7 of the earlier note reached for a different reason.

### (b) There was only ever one route, and it follows focus

Every tap went out as a `SendInput` scancode. `SendInput` is delivered to the **foreground** window —
being inside the game's process does not change that. An external typer landing 7/10, then 3/3, then
1/1, then nothing at all is what losing focus looks like, and the in-process route inherited exactly
the same dependency.

Four routes now exist, carried **per tap** so one queue can mix them:

| route | what it assumes | why it might win |
| --- | --- | --- |
| `sendinput` | the OS input stack, foreground window | what has always been used; DirectInput sees scancodes |
| `postkey` | `WM_KEYDOWN`/`WM_KEYUP` posted at the window | focus-independent; DOOM runs a real message pump (dossier §13a) |
| `postchar` | the same **plus `WM_CHAR`** | console text entry is normally driven by `WM_CHAR`, not key state |
| `keystate` | fabricate the answer to the game's own `GetAsyncKeyState`/`GetKeyState`/`GetKeyboardState` | immune to focus *and* to auto-repeat; useless if the console reads characters |

`postchar` is the default, because it is the most likely to work. **That is a hypothesis and it has
not been tested.** The standing rule is to build several routes and measure which one the game obeys
against a control, not to reason about which ought to work.

**`ctest` is the measurement.** It queues the digit `0` down `sendinput`, `1` down `postkey`, `2` down
`postchar` and `3` down `keystate`, in that order. Open the console, run `ctest`, read the line:

```
0123   all four routes work; use postchar for text
2      only WM_CHAR lands -- the console reads characters, not key state
01     the OS stack works and WM_CHAR does not
(none) nothing landed: console not open, not focused, or the HWND is wrong -- check `status`
00123  a REPEATED digit is auto-repeat, i.e. the frame rate is too low. camoff, then repeat
```

One console line, four answers. Selecting `keystate` while the key-state IAT hooks did not land now
warns, because an inert route and an ignored route look identical in a log and are opposite findings.

---

## 4. A cross-machine defect found on the way, and fixed

`gen/generate.sh` **overwrote** the checked-in export table with whatever the local system
`vulkan-1.dll` exports. The home PC's newer loader added 19 Vulkan 1.4 entry points on 2026-09-08;
regenerating on the dev PC, whose loader is older, deleted all 19 again. Every build on either
machine dirtied four generated files, and any commit that swept them up would have silently reverted
the other machine's refresh.

It unions now, and never shrinks. A union is safe because a name the local loader lacks resolves to
`NULL`, which `proxy.c` already counts (`g_missingResolves`) and reports; every hooked function is
fail-safe against a null real pointer; and DOOM imports 96 names, all present on both machines.

Verified rather than argued `[verified-numerically 2026-09-08]`:

- regenerating on the dev PC leaves all four generated files **byte-identical to `origin/main`** —
  the only file that changes is `generate.sh` itself;
- the proxy loads and reports `resolved 246/265 exports (19 missing)`;
- the off-game Vulkan smoke test still passes end to end through the proxy.

---

## 5. Host suites now run on every build

They used to be reachable only through `build.sh --test`, and `rvtest` was not wired in at all. A
suite that has to be remembered is a suite that stops being run, and both of these guard claims that
are already written down.

| suite | checks | what it protects |
| --- | --- | --- |
| `test/rvtest.c` | 22, plus 20,000 random windows, **0 pass** | the shape test rejects; a survivor is not noise |
| `test/pacetest.c` | 16 | the hold is a *duration*; never fewer than 1 frame; never unbounded; non-increasing as the period grows, over every period 1–2000 ms |

Both include the **shipped** `.c` file rather than a transcription, so what is tested is what ships.

---

## 6. What this session did NOT establish

- Whether the engine honours `explicitProjectionMatrix`. **Unchanged** — but for the first time it is
  askable in one command.
- Whether any of the 654 survivors is a `renderView_t` at all.
- Whether the ring copies keep the translation in column 3.
- Which console route DOOM obeys, or whether the frame-rate explanation for the dropped characters
  is right. `ctest` decides the first; only re-running `type` at 60 fps decides the second.
- Nothing here has been run. The game was not launched.

---

## 7. The one launch that answers both starred questions

Everything below is a single sitting. **`camoff` first and keep it off** — at ~1 FPS the projection
test cannot be judged by eye and the typer cannot be trusted.

```
scan 0x29                          open the console
ctest                              -> which typing routes work (read the digits)
pdump 0x<module+0x360F6B0>          the position, without needing the console at all
camseed <x> <y> <z>
camrescan                          discovery records WHERE the copies are

psearch <x> <y> <z>                pass 1
  (move the player, re-read the position)
pnarrow <x> <y> <z>                pass 2
rvscan                             ⭐⭐ THE ONE THAT WAS BLOCKED
rvexplicit <strongest addr> on      §6c
ringlearn                          ⭐ now scanning where the copies are
ringyaw 20
```

| step | outcome | what it means |
| --- | --- | --- |
| `rvscan` | survivors listed | the shape test finally saw the whole set; go to `rvexplicit` |
| | 0 pass, nearly all on `fov_x`/`fov_y` | these addresses are not `renderView_t`s at all — question the *candidate set*, e.g. `pnarrow` at a third position |
| | 0 pass, failures spread across tests | the set is mixed; question the **layout** next |
| `rvexplicit … on` | projection visibly changes | ⭐⭐ the engine honours `explicitProjectionMatrix`; per-eye projection is a supported input, and this becomes the categorically easier project |
| | unchanged | one of three things — not the live view, flag re-set each frame, or ignored here. Try the next-strongest before concluding |
| `ringlearn` | usable deltas | the ring route is open; `ringyaw 20` should visibly rotate |
| | hits, all deltas too far | the copies are not in the bound per-draw range — **the probing strategy needs a different anchor**, and no window will fix it |
| | 0 hits in a covering window | column 3 is not where these copies keep the translation |

`ringyaw 20` rotating the view is what opens the two-submit stereo route.
