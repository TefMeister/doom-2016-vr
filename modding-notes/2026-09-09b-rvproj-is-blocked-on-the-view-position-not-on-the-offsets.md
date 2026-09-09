# 2026-09-09b — `rvproj` is blocked on getting the VIEW POSITION, not on the offsets

*Session: `/lm doom-2016-vr`, dev PC, one launch, fully autonomous — and the **first live run of the
new TANDEM workflow**, joining a `/pd` reader's seat. Evidence:
`dev-archive/recon/2026-09-09b-rvproj-blocked-on-the-view-position/`.*

## What was attempted

The board's ⭐⭐ row: run `psearch` → `pnarrow` → `rvscan`, then `rvproj <addr>` on the strongest
survivor, and read the engine's own `projectionMatrix`.

## What actually happened, in order

1. **Launched, reached gameplay, command channel confirmed live.** `DOOMx64vk.exe` with
   `SteamAppId=379720`, automation marker present. `help` lists `rvproj` in the deployed build, so
   the instrument is really there. Deployed `vulkan-1.dll` rebuilt from source this session and
   **sha256-identical** to what is deployed (`fef97dd4…`) — the stamp is the newest build.
2. **`camhunt` (`snapa` → `move` → `snapb`) produced camera-shaped transforms with world positions**
   in the 1700–2800 / 5400–5700 / 6250–6570 range — the same coordinate space the 2026-09-07
   `psearch 1728 5440 6372` used, so the space is right.
3. **`psearch 2207.05 5667.51 6259.55 tol 1.0` → 14 candidates** across 4618 regions (image 1,
   heap 13). So that position IS live in process memory.
4. **`rvscan 14` → 0 of 14 passed**, and the histogram is uniform:
   `rejected by: fov_x=14  fov_y=0  fov_pair=0  useExplicit=0  forceIdentity=0  vieworg=0`.
5. `rvcheck` on the three `camhunt` addresses directly: all three **REJECTED — "fov_x not a
   plausible angle"**, with `fov=(0.00,0.00)`, `(0.60,0.13)`, `(1.00,1.00)`.

## The reading, and it is the tool's own

**Every rejection is on `fov_x`, and none on `vieworg`.** The dossier's own guidance for this
histogram is that the candidate SET is more likely wrong than the offsets. `[measured 2026-09-09]`

The cause is now identifiable: **the position searched for was not the player's view origin.** It
came from a `camhunt` candidate — a transform that happened to be moving — which can be any object
in the world (a prop, a demon, a light). `psearch` faithfully found 14 places holding that value,
and none of them is inside a `renderView_t`, which is exactly what you would expect for the wrong
point.

⚠️ **NOT established, and this matters:** nothing here says the `+4304` / `+2032` offsets are wrong,
or that `rvproj` does not work. It has **never been reached**. The row is untouched, not disproved.

## ⭐ THE ACTUAL BLOCKER — and it is a harness gap, not an engine one

`psearch` needs the **player's view origin**, and the only known source is the game console's
`getviewpos`. **The harness cannot type it.**

- DOOM's console **reads `WM_CHAR`**, not key state (dossier §10, `ctest`).
- The toolkit harness sends **scancodes**, and its key table has no `g`, `t`, `p` or `o` — so
  `getviewpos` cannot even be spelled, let alone delivered as characters.

That is why every earlier session that used `psearch` had a position: a human read it off the
console. **The automation has never had that number on its own.**

## The fix, prepared but UNTESTED

Typing can be avoided entirely by making the console commands a **key bind**, since a bind is one
keypress and the harness has F-keys. Added to
`~/Saved Games/id Software/DOOM/base/DOOMConfig.local` with the game closed (backup
`DOOMConfig.local.bak-2026-09-09-pre-viewpos-bind`):

```
bind "F9"  "getviewpos"
bind "F10" "condump viewpos.txt"
```

⚠️ **`[hypothesis]` — none of this has been run.** Three separate things could each defeat it and
the next session should check them in this order:

1. **Does the engine accept `bind` lines in `DOOMConfig.local` at all?** The file as shipped
   contains only cvars — **zero** `bind` lines — so binds may live somewhere else entirely
   (an `autoexec.cfg`, or the binds section of `DOOMConfig.cfg`).
2. **Does the bind survive the game's own config rewrite on exit?** DOOM rewrites this file when it
   quits. If the line is gone after one launch, that answers question 1 too.
3. **Does `condump` write where we expect**, and does `getviewpos` output reach the dump buffer
   without the console being visible?

**If the bind route fails, the fallback is a real capability:** teach the harness to post `WM_CHAR`
messages, which the dossier already records as the thing DOOM's console accepts (`postmessage` is
listed as an available backend in the proxy's own `status`). That is the durable fix and it would
serve every future console command, not just this one.

## Also this session

- **First live run of the TANDEM workflow.** `gate-scan --next --tag FLAT` printed
  `TANDEM: /pd is seated on doom-2016-vr - joining it there.` and the rendezvous worked exactly as
  designed — the game was chosen without anyone naming it. The `/pd` rider's
  `engine-research/inbox/` was empty at session start and at session end.
- **A harness bug found on the Alice side does NOT affect DOOM.** `doomdrive.py` already matches on
  the `DOOMx64` title **prefix**, with a comment saying a bare `DOOM` substring "would happily
  return a shell window". `alice_harness.py` has the substring bug; `enslaved_harness.py` uses
  `"enslav"` and should be checked. **No harness on the estate matches by owning process.**
