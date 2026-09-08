# 2026-09-08c — `rvscan` is answered, the explicit matrix is not askable this way, and the ring route is dead as a strategy

*Session: `/lm doom-2016-vr`, dev PC (DESKTOP-V8GTSIR), one launch, fully autonomous.
The user granted "launch and close the game as you please" for this session only.*

**Both starred questions on the board are now answered. Neither answer is the one the row hoped
for, and both are verdicts on the STRATEGY rather than tuning — which is exactly the kind of
outcome the reading table was written to make legible.**

---

## 1. Pre-flight

`deployed.sh check` said `OK`, and a rebuild from `staging/doom-2016-vr/proxy-vulkan/` produced a
**byte-identical** `vulkan-1.dll` (`3eae8b6fc648`, 189 952 B), so the install is not merely what was
stamped but genuinely the newest source. 22 host tests passed.

⚠️ **A correction to my own first reading:** Steam's launch shows `DOOMx64.exe` in the task list for
a few seconds and I briefly took that to mean the OpenGL exe had started and the Vulkan proxy would
not load. It is a bootstrap — `DOOMx64vk.exe` is what ends up running, the proxy loaded normally,
and the `[autoinput]` hooks appear in the log. Nothing had to be changed.

## 2. ⭐⭐ `rvscan` — ANSWERED. 8 survivors at confidence 100/100

```
rvscan: tested 833 candidate(s) in 78 ms -> 8 passed the shape test, 0 had an unreadable window
  rejected by: fov_x=822  fov_y=3  fov_pair=0  useExplicit=0  forceIdentity=0  vieworg=0
```

Chain: `getviewpos` → `1728 5440 6372.16` → `camseed` → `camrescan` (**112 camera copies located**)
→ `psearch` → **4402 candidates** → walk forward → `getviewpos` → `2345.03 5795.69 6333.47` →
`pnarrow` → **833 survivors** → `rvscan` → **8**.

All eight read identically `[measured 2026-09-08]`:

```
vieworg=(2345.03 5795.69 6333.47)   fov=(90.00 58.72)   useExplicit=0 forceIdentity=0
```

Two independent corroborations that these are real `renderView_t`s and not float soup:

- **The fov pair is self-consistent for 16:9.** `2·atan(tan(45°)/(16/9)) = 58.72°`, which is exactly
  the reported `fov_y`. The shape test does not check that relationship, so it is free evidence.
- **⭐ Survivor 7 is the dossier's §6h global, and the RVA held across a rebase.** It sits at
  `0x00007FF767CBF6B0` with the module based at `0x00007FF7646B0000` → **RVA `0x360F6B0`**, the
  exact offset §6h records. The dossier listed *"still to confirm: that the RVA `0x360F6B0` itself
  holds across the rebase"* as open; this boot's base differs from the recorded
  `0x7FF74D320000`, and the offset still lands. `[verified-live 2026-09-08, n=1 boot this session;
  n≥2 bases with the 2026-08-25 record]`. Survivor 8 is a second static view at RVA `0x360FFF0`.

The other six survivors are transient: one on a thread stack (`0x000000E5…`), five on the heap
(`0x000002A1…`).

## 3. ⭐⭐ §6c — the question CANNOT BE ASKED by one-shot writes

The row said: `rvexplicit <strongest> on`, then watch. Done, on the strongest (stack) candidate and
on the static §6h one. **The picture did not change** — mean luma delta 4.96–5.65 against a
baseline whose own ambient noise is the same size, and a 90° → 40° FOV would have been
unmistakable.

The reading table lists three explanations for "unchanged" and asks which one was seen. **It is the
second, and it is measurable:**

```
16:05:12.359  wrote 16 floats to explicitProjectionMatrix at 00007FF767CBF66C
16:05:12.360  useExplicitProjectionMatrix at 00007FF767CBF6AC: 0 -> 1
16:05:59.857  useExplicitProjectionMatrix = 0        <-- flag gone
16:05:59.858  explicitProjectionMatrix ... all 0.00  <-- our 16 floats gone too
```

Tightened with a same-tick read-back `[measured 2026-09-08, n=2 writes]`: values written at
`16:06:32.598` read back **intact in the same command tick** (`7.0` ×16) and were **all zero by the
next round-trip**, 18.5 s and ~1 100 frames later. So the write lands and is then erased.

**Two things follow, and the second is why the experiment as written could never have worked:**

1. **The whole `renderView_t` is rewritten, not just the flag.** `vieworg` tracks the player
   exactly, so the struct is live — it is rebuilt each frame rather than being the wrong struct.
2. **⚠️ `explicitProjectionMatrix` is ALL ZEROS to begin with.** So `rvexplicit … on` *alone* — the
   step the board specified — would at best have pointed the engine at a degenerate projection.
   Setting the flag without writing a matrix first cannot produce a legible result either way.

**NOT established:** that the engine ignores `explicitProjectionMatrix`. That remains untested. What
is established is that **a one-shot poke cannot test it**, because the write is erased before any
frame that would consume it. The test needs the flag *and* the matrix re-asserted from inside the
frame loop — a `phold`-style hold, which does not exist for this struct yet. `[hypothesis]` that it
is rewritten *every* frame; the measurement bounds it at "within ~1 100 frames", not per-frame.

## 4. ⭐⭐ The ring route — DEAD AS A STRATEGY, and it is not a window-size problem

```
LEARN window from camhunt discovery -- where the copies actually are:
  [62945872..67061392) = 4019 KB of a 4019 KB span (discovery: 112 copies)
252 camera hit(s): 0 with a usable delta, 252 too far from any bound offset -> 0 distinct delta(s)
>> FOUND THE CAMERA (252 copies) BUT NOT VIA A DYNAMIC OFFSET: the nearest bound offset is
   60673 KB below the nearest copy. The copies are in this region but NOT in the per-draw block
   range the game binds, so offset+delta probing cannot reach them however the window is set.
```

This is the reading table's "hits, all deltas too far ⇒ the probing strategy needs a different
anchor, and no window will fix it".

**It also explains and supersedes the 2026-09-08 finding that "the ring-learn window is 53 MB
short".** That framed it as a sizing problem. It is not: the copies sit ~59 MB above the nearest
offset the game ever binds, so **no window over `vkCmdBindDescriptorSets` offsets reaches them.**

`ringyaw 20` was not run — with 0 usable deltas there is nothing for it to drive.

## 5. ⭐ `framespy` — and the constructive half

Since §4's verdict asks for "a different anchor", `framespy` was run to enumerate what the frame
actually offers. 43 passes, **298 draws**, and:

```
command buffers begun: 8  ONE_TIME_SUBMIT=0
  -> NO one-time-submit: the game's own command buffers may be RESUBMITTED.
     Both eyes from one recorded frame, no mirroring needed.
VERDICT INPUT: dynamic offsets ARE in use.
```

Every pass's `dynOffset range` lies between **3 783 680 and 3 794 176** — i.e. the bound per-draw
uniform region is around **3.78 MB**, while the camera copies are at **62.9–67.1 MB**. Two
independent measurements of the same gap, which is why §4's verdict is not an artefact of the ring
window.

So the replacement strategy the evidence points at is **resubmit the game's own command buffers and
redirect the recorded draws at a second copy of the per-draw uniform region** — single-frame stereo,
no mirroring. That is a design lead, not a result: nothing here has been built or run.

## 6. Automation — the four capabilities, and one real correction

| capability | status |
| --- | --- |
| 1. menu → gameplay | ✅ **PROVEN** this session, autonomously |
| 2. console / exec commands | ✅ **PROVEN** — file channel *and* console read+write |
| 3. character + camera | ✅ character movement proven; camera not exercised |
| 4. self-close | ✅ **PROVEN**, graceful through the game's own menu, no `taskkill` |

### ⚠️ `ctest` says the proxy's DEFAULT input backend does not work

The console showed **`]0122`**:

| digit | route | result |
| --- | --- | --- |
| `0` | sendinput-scancode | ✅ |
| `1` | postmessage-key | ✅ |
| `2` | postmessage-char | ✅ but **delivered twice** |
| `3` | **inproc-keystate** | ❌ **never landed** |

`inproc-keystate` is what `status` reports as `[default]`. That is why an early `key 0x48` through
the file channel did nothing while the same key sent externally moved the menu. **Set
`backend sendinput` / `typeroute sendinput` before driving anything**; with that set, `move fwd 90`
walked the player 700 units and `type getviewpos` typed cleanly.

The doubled `2` is *not* the low-frame-rate auto-repeat the help warns about — the game was at ~60
FPS throughout (`camoff` was set first and kept off). `postmessage-char` appears to deliver twice on
its own. `[measured 2026-09-08, n=1]`

### Two harness defects worth fixing

- **`rvmat` and `rvcheck` reject the address format the tool's own log prints.**
  `rvcheck 000000E5E2DEB7A0` → `usage:`; `rvmat 000000E5E2DEB7A0` → `0000000000000000: window not
  readable` (a silently wrong answer, not an error). Both work with `0x`-prefixed, unpadded
  addresses. `rvexplicit` accepts the padded form. So copy-pasting a survivor address out of
  `rvscan` output fails for two of the three commands, and one of them fails *quietly*.
- **The profile's window title was wrong** — it recorded `DOOM`; the real titles are `DOOMx64vk`
  and `DOOMx64`. An exact match on `DOOM` finds nothing and a bare substring match can select a
  terminal window instead.

## 7. What to run next time

Everything below is **static — no game needed**:

1. **`rvhold <addr>`**: re-assert `useExplicitProjectionMatrix` *and* `explicitProjectionMatrix`
   every frame, the way `phold` does for positions, at the same point `camwatch` uses. That is the
   only way §6c can be asked. Then one launch answers it.
2. Fix the `rvmat`/`rvcheck` address parsing to accept what `rvscan` prints.
3. Design the command-buffer-resubmission route from §5.

Evidence: `dev-archive/recon/2026-09-08c-rvscan-answered-and-the-ring-route-is-dead/`.
