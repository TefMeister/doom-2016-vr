# 2026-09-04 (`/lm`, dev PC, FULLY AUTONOMOUS) — the ring-camera LEARN found nothing; a virtual XInput pad drives DOOM's movement AND look, reversibly

> **⚠️ READ §10 FIRST — this note's own diagnosis was corrected the same day.** Sections 1, 2 and 4
> conclude the 512 KB scan cap was the cause and widening it would fix the ring test. A second launch
> on the widened 8 MB build **still found 0**, and `findvec` localised the camera copies to a region
> `ringcam` never scans. The cap was real but not the cure; the true root cause and the redesign are
> in §10. The virtual-pad result (§3) is unaffected and stands.

**One launch. The critical-path ring test returned a clean diagnostic negative with a concrete
cause and a static fix; and a second live item — does DOOM obey a ViGEm virtual pad — came back a
firm yes on both axes.** The user launched via `install-and-launch.bat` and went back to work;
Claude drove the promo hub → CAMPAIGN → GAME SLOT 1 → CONTINUE GAME → into gameplay, ran the ring
test, drove the virtual pad, and quit through the game's own menu. Windowed 1280x720, Vulkan.

Build under test at launch: `staging` ring build as of this morning (`Mad`—no: DOOM `vulkan-1.dll`
164,352 B rebuilt from HEAD `1c31e28`, smoke test passed before install). Evidence:
`dev-archive/recon/2026-09-04-ringcam-cap-and-vigem/`.

---

## 1. In plain words

The plan was: learn where the camera lives in the per-draw uniform ring, then yaw it and see the
view turn. The learn step found **zero** camera copies — but not because the camera is unreachable.
The global camera read fine the whole time (I moved and it tracked), and the reason the learn
missed is measured, not guessed: **the learn scans only the first 512 KB of the frame's dynamic-
offset window, and this scene's window is 3.4 MB.** It searched the first 15% and stopped. The
512 KB ceiling was chosen on 2026-09-01 when a frame spanned ~137 KB; this scene is 25x that. The
fix is a one-line ceiling change, done and deployed this session (§4).

The bonus item paid off big. DOOM imports XInput directly, so a virtual Xbox 360 pad made with
ViGEmBus should look like a real controller — and it does. Pushing the left stick walked the
player (~820 units, pure translation), the right stick turned the view (~98 degrees, pure
rotation), and pushing each the other way undid it. DOOM even popped a "Controller Disconnected —
Xbox 360 controller" toast when the pad went away, which is the game telling us it had bound it as
a genuine controller. This is the input route the board called "the highest-value unblock on this
project," now proven end to end against the game itself, not just at the OS level.

## 2. The ring LEARN — why it found nothing `[verified-live 2026-09-04, n=1 launch]`

```
[ringcam] LEARN over [0..3587328) = 512 KB (not 64 MB): 0 camera hit(s), 0 distinct delta(s)
[ringcam]   nothing matched -- the camera may not be in this window, or column 3 is not where the ring copies keep the translation.
[ringcam] mode=0 learned=0 deltas=0  offsets this frame=1702 window=[0..3583232]
[ringcam]   global cam OK (1728.00 5440.00 6372.16) left=(-0.500 0.866 0.000)
```

- **The global camera is authoritative and fine.** Read from `module+0x360F6B0`; it tracked every
  move I made (see §3). So the LEARN's own reference value was correct.
- **The scan window is 3.4 MB; the scan is capped at 512 KB.** `window=[0..3583232]` = 3.4 MB is
  the span of this frame's 1702 dynamic offsets. `learn()` computes `len = offMax - offMin`, then
  `if (len > LEARN_CAP) len = LEARN_CAP` with `LEARN_CAP = 512*1024`. So it memcpy'd and searched
  `[0, 512 KB)` — the first 15% — and the camera copies live somewhere in the other 85%. The log's
  "[0..3587328) = 512 KB" is the tell: the printed range is 3.4 MB but the KB figure is the capped
  scan length. (I have since fixed that log line too; §4.)
- **The column-3 assumption is NOT the problem.** `ringcam.c`'s `matches()` keys on
  `m[3]/m[7]/m[11] == cameraOrigin`, and `camhunt.c` (`camhunt.c:291,514-516`) uses the *identical*
  predicate and previously found **180 camera copies** scanning 96 MB. Same predicate, copies exist;
  the only material difference is scan width. So widening the scan is the right fix, high confidence,
  and "column 3 is wrong" (the other branch the log offered) is effectively ruled out.

## 3. The virtual pad drives DOOM — movement and look, isolated and reversible `[verified-live 2026-09-04, n=2 each]`

Pad created with `flat-to-vr-RE-toolkit/tools/virtual-pad.py` (ViGEmBus, `vgamepad`). Camera read
from the global via `ringstat` before and after each hold; DOOM foregrounded first.

| action | camera before | camera after | reading |
| --- | --- | --- | --- |
| left stick forward 2 s | pos (2163.26, 5695.20, 6335.29) | pos (1734.00, 6371.67, 6505.98) | ~820-unit move, **basis unchanged** ⇒ pure walk |
| right stick right 1.5 s | left=(-0.809,-0.588,0) @ pos (1761.26, 6361.02, 6476.61) | left=(-0.472, 0.881, 0) @ **same pos** | ~98 deg yaw, **pos unchanged** ⇒ pure look |
| right stick left 1.5 s | left=(-0.472, 0.881, 0) | left=(-0.804,-0.595, 0) @ same pos | yaw **reversed** to the pre-look heading |
| left stick back 1.5 s | pos (1761.26, 6361.02, 6476.61) | pos (2124.18, 5907.70, 6318.18) | move **reversed**, basis unchanged |

- **The game bound the pad as a real controller:** every time `virtual-pad.py` exited it destroyed
  the pad, and DOOM showed a "Controller Disconnected — Xbox 360 controller" toast (visible in
  `d15`, `d17`). Confirmation the game saw it, not just Windows.
- **Each axis is cleanly isolated** — the left stick moves with the basis fixed, the right stick
  turns with the position fixed — and **both reverse**, which is the discrimination that a drifting
  camera or scene noise cannot fake. This is the same bar (reversal) that validated `sendinput`
  look on 2026-08-31.
- Movement magnitude is `n=1` per direction; the *fact that the pad drives the game* is `n=2` per
  axis with reversal. XInput being imported directly (dossier §3) is why focus and DirectInput
  exclusive mode never entered into it.

**Why this matters:** the proxy's own `probe` still scores `vigem-pad` as `unavailable -- our
report path is the next thing to build` — that internal backend was never implemented. But the
*external* route (virtual-pad.py driving the OS-level pad) is now the proven way to drive DOOM
autonomously for camera RE, independent of the keyboard/mouse path. It also generalises: it is the
route ENSLAVED needs for its controller-chord debug camera.

## 4. The fix, built and deployed (needs the next launch to test)

`src/ringcam.c`: `LEARN_CAP` widened `512*1024` → `8*1024*1024`. 8 MB covers this scene's 3.4 MB
span 2.3x over; the one-off memcpy-then-scan is ~340 ms worst case at the ceiling (dossier 6g's
~42 ms/MB) versus the 2.7 s the 64 MB scan cost — a hitch, not a freeze, and LEARN runs once then
sets mode OFF. The LEARN log now prints the scanned window against the full offset span and warns
explicitly when the span still exceeds the ceiling, so a future larger scene is visible rather than
silent. `[compile-verified 2026-09-04]` — clean build, off-game smoke test passes. Deployed to
`DOOM\vulkan-1.dll` (169,472 B); the previous build is recoverable by rebuilding `1c31e28`.

**The resume test is unchanged, and now has a real chance:** `ringlearn` → `ringstat` (expect
`learned=1`, one or more deltas) → `ringyaw 20` → screenshot. View visibly rotates ⇒ the two-submit
stereo path is open to build. Still no rotation with deltas learned ⇒ the delta-based probe is
missing the write-time copy, which is the 2026-09-03 diagnostic.

## 5. Driving the game — profile created

No control profile existed for DOOM; one is created this session at
`ai-game-control-profiles/profiles/doom-2016.json`. Notes worth carrying:
- **The promo hub is a trap for the mouse.** A left-click at (155,140) aiming for the CAMPAIGN tab
  instead hit a "DOOM: The Dark Ages" promo tile and opened the **Steam overlay**. Drive the hub by
  keyboard: `Esc` clears the promo overlay (and raises a quit prompt — pick No), `Up` moves to the
  CAMPAIGN/MULTIPLAYER/SNAPMAP tab row, `Left`/`Right` between tabs, `Enter` selects.
- **Route to gameplay:** CAMPAIGN → SELECT CAMPAIGN (GAME SLOT 1 highlighted) → Enter → MAIN MENU
  (CONTINUE GAME highlighted) → Enter → loading → `Space` at "Press [SPACE] to continue" → gameplay.
- **Self-close:** `Esc` → 5x `Down` to EXIT TO DESKTOP (verify the highlight) → `Enter` → `Up` to
  Yes (the dialog defaults to No) → `Enter`. Process gone in ~5 s. Exercised this session.
- **Hazards:** SELECT CAMPAIGN carries `[R] DELETE GAME SLOT`, and NEW SLOT / ARCADE MODE sit below
  the real slots; the pause menu has RESTART MISSION; both quit dialogs default to No. Verify every
  highlight before Enter.

## 6. Automation on DOOM, scored (§5a)

1. **Menu → gameplay: proven** — full promo-hub-to-gameplay drive this session.
2. **Commands: proven** — the file command channel answered `ringlearn`/`ringstat` reliably; the
   in-game console path (`scan 0x29`) was verified earlier (dossier §10).
3. **Character + camera: proven, two independent routes** — `sendinput` (2026-08-31) and now a
   ViGEm virtual pad, the latter isolated and reversible on both axes this session.
4. **Self-close: proven, exercised** — quit through EXIT TO DESKTOP.

## 7. What is NOT established

- Whether the widened LEARN actually finds the camera and `ringyaw` rotates the view — needs the
  next launch (the whole point of the FLAT gate).
- Whether the camera copies are within 8 MB of `offMin` in *every* scene, or whether a denser scene
  needs a higher ceiling — the new warning line will say so if not.
- The proxy's *internal* `vigem` backend for `probe` is still unbuilt; the external virtual-pad.py
  route is what was proven. Building the internal one is optional now that the external one works.

## 8. Next

Live (`[FLAT]`): relaunch and run `ringlearn`→`ringstat`→`ringyaw 20`→screenshot on the widened
build. Static (`[PD]`): the eye-field reflection-table mining continues (unchanged). The virtual-pad
route is now the recommended way to drive DOOM's camera in any future live session.

---

## 10. CORRECTION, same day, second launch — the widened scan was run and STILL finds 0; the cap was not the cure

**Supersedes sections 2 and 4 above** (which concluded, in good faith, that the 512 KB cap was *the*
cause and that widening it gave the resume test "a real chance"). It did not. Recording the correction
next to the claim, per claim hygiene.

The user relaunched on the 8 MB build. `ringlearn` then `ringstat`:

```
[ringcam] LEARN scanned [0..3088384) = 3016 KB of a 3016 KB offset span (not 64 MB): 0 camera hit(s), 0 distinct delta(s)
[ringcam] mode=0 learned=0 deltas=0  offsets this frame=1708 window=[0..3084288]
[ringcam]   global cam OK (1728.00 5440.00 6372.16) left=(-0.500 0.866 0.000)
```

This time the scan covered the **entire** 3.0 MB offset span — no cap hit — and still matched nothing.
So the cap was real (and worth fixing: the new log is exactly how we can now tell the span was fully
covered), but it was **necessary to see the problem, not the cure.** `[verified-live 2026-09-04, n=1]`

### The copies exist, and they are in a different region than ringcam scans

`findvec 1728 5440 6372.16 2.0` (camhunt's value search across all mappings, background-threaded and
chunked — it does not freeze) returned **64 matches, capped, all in region index 2**, at addresses
clustered around `0x…2861xxxx` (a ~10 KB cluster at low offset). Both layouts appeared, including a
clean **column-3 view matrix**:

```
0.866 -0.500  0.000  1728.000
0.500  0.866  0.000  5440.000
0.000  0.000  1.000  6372.160
0.000  0.000  0.000  0.000
```

basis in the upper-left 3x3, camera origin in column 3 (m[3]/m[7]/m[11]) — exactly the shape
`ringcam`'s `matches()` looks for. So the predicate is right and the data is there.

### Root cause, from the code

`ringcam_onSubmit` scans `camhunt_biggestMapping()`, which returns whichever single mapping is
*largest* (`sz > bestSize`, first-wins on ties). There are two 64 MB ring mappings (one at instance
creation, one at level load) plus whole-size ones. The camera copies live in region 2, which is **not**
the one `biggestMapping` returns — so LEARN reads the wrong buffer's bytes at the recorded dynamic
offsets. The dynamic offsets `ringcam` records (from `vkCmdBindDescriptorSets`) index some buffer's
memory; applying them to `biggestMapping`'s base is a base/offset mismatch. **Widening the cap cannot
fix a wrong-base scan.**

### The redesign (now `[PD]`, needs no more launches to design)

- **Locate the camera region by value, then scan/patch THAT region.** `findvec` already proves the
  copies are a tight low-offset cluster in one region; a bounded per-frame scan of that region's first
  few hundred KB, verify-column-3-before-write, is cheap and hits them. This drops the fragile
  "dynamic offset + delta against biggestMapping" correlation entirely.
- **Or reuse camhunt's per-mapping flush path.** ⚠️ Region 2 reported `flushes=27462`, i.e. it IS
  flushed — which sits oddly against §6g's "the camera buffer is HOST_COHERENT, so the flush path is
  NOT its update route." Resolve which buffer §6g measured before relying on either path.
- Either way the write guard (only touch a slot whose column 3 still equals the expected origin) and
  the yaw/eye math in `applyOne` are unaffected and already correct.

### What this does NOT change

The virtual-pad result (§3) stands: movement and look, isolated and reversible, `n=2` per axis. The
`LEARN_CAP` → 8 MB change and the improved log stay in — they are how the full-span coverage was
confirmed. Only the *diagnosis* changed: from "scan too small" to "scan of the wrong region."

## 11. Gate

Static (`[PD]`): redesign `ringcam`'s region selection (value-locate the camera region, or per-mapping
flush path), then it needs a launch to test. The eye-field reflection mining is still `[PD]` too.
Live (`[FLAT]`): the `+com_allowconsole 1` gate probe remains a standalone launch item. Nothing needs
the headset.
