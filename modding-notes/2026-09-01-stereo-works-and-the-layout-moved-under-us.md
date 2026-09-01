# 2026-09-01 (afternoon) — stereo out of the static global, and a correction I had to make to myself

Second autonomous session of the day, on a relaunched game.

## The results

**The address survived the restart** `[verified-live 2026-09-01, n=2 process instances]`. The basis
was **predicted from `getviewpos` before the dump was read**, and matched to three decimals. Kept
honest: the module loaded at the **same base** both times, so this is not yet a test of ASLR
rebasing — that needs a reboot, not a relaunch. Meanwhile the address should be taken as
`GetModuleHandle(NULL) + 0x360F6B0`, which is right either way and costs nothing.

**⭐ Stereo works.** Holding the origin at `origin ± 32·left` renders the same scene from two
laterally-offset viewpoints with depth-correct parallax — a nearby crate swings hugely, distant
towers barely move — both frames clean. **Per-eye rendering does not need the dormant stereo path.**
Caveat: two sequential frames, not two eyes in one frame.

**Rotation needs the whole basis.** Writing only `forward`, rotated 20°, shears the image badly. The
vector is consumed by the renderer, but `forward` and `left` have to move together. `pholdyaw` was
built for that and is in the new build, waiting on a relaunch to install.

**`setviewpos` is not registered on retail** — the cross-check research proposed is gated after all.

## The correction I had to make to my own morning write-up

This morning I recorded that the 2026-08-31 console-key values "do not reproduce", and filed that to
the cross-engine library as a superseding correction. **That was itself wrong, and in an instructive
way.** This afternoon's launch reported keyboard layout `0x08090809`; the morning's was `0x04250425`.
Under the afternoon layout, scancode `0x29` is reached by `VK_OEM_8` (`0xDF`) — *exactly* what the
08-31 note recorded.

Nobody mis-measured. **The thing being measured moved between two launches of the same game on the
same machine, hours apart.**

I had the right lesson and the wrong claim attached to it. The lesson — *the physical scancode is
the stable fact, the VK that reaches it is not* — was correct and is now stronger, because the
instability is not "between machines" (which you could handle once at setup) but "between launches"
(which means **anything cached can be stale, including a helper script written an hour ago in the
same session**). The claim I built around it — that the older numbers were wrong — was an
overreach from a single measurement.

The convention handled this correctly and is worth the small cost it imposes: inbox files are
create-only, so the fix is a **new** file carrying `Supersedes:` and naming my own morning drop,
rather than a quiet edit. Anyone reading the library in order sees the original, then the
correction, and the reasoning behind both.

**One flaw found in the convention itself:** `grep -rn "^Supersedes:" inbox/` — the command
`CONVENTIONS.md` prescribes — **misses every drop that writes the header in bold markdown**
(`**Supersedes:**`), which is how both of today's `/gr` files and my own wrote it. A curator running
the prescribed check would have concluded there were no corrections pending. The grep needs to be
`grep -rni "supersedes" inbox/`.

## Research changed what I did, not just what I knew

Three `/gr` drops landed while I was working and were drained before I wrote any more code:

1. **id's own GPL Doom 3 BFG source** declares `idVec3 vieworg; // has already been adjusted for
   stereo world seperation`, with `stereoScreenSeparation` as a *separate* field. That supersedes
   the dossier's §6a caveat, which had concluded from a DOOM 2016 doc-comment that eye separation is
   applied downstream of view setup and that our override "probably belongs at the projection
   stage". Under the corrected reading, the address I found **is the lever the engine's own stereo
   code pulls**. I ran the eye-offset test because of that file, and it worked first try. Without it
   I would have been building toward the projection stage.
2. **Photo Mode is a shipped, ungated, detached free camera** with the player invisible. So this
   morning's elevated-camera result was not luck — the engine was **built** to render from a camera
   that is not the player's. `pm_photoModeMaxDist "5000"` suggests the engine's own leash is roughly
   eighty times our 64-unit clamp.
3. **The HUD loss cannot be culling** — the UI is drawn to its own render target and composited
   last, so it is not in the world frustum at all. That kills the fix I would have reached for and
   points at game state instead.

Worth stating plainly: the parallel research lane earned its keep today. One of those three turned a
planned line of work on its head *before* I spent a session on it.

## Next

1. **Photo Mode, by hand, no code** — does the HUD vanish there the same way? Cheapest test on the board.
2. **Install the new build at the next launch** and run `pholdyaw` — rotation is the untested half.
3. **Two minutes with a browser** on `doom_cvars.txt` (Ctrl-F `stereoRender`, `multiView`,
   `com_production`, `explicitProjection`) — the automated read of that 695 KB file is provably
   unreliable, and it would settle the dormant stereo path's reachability from a public source.
4. **Reboot, then re-check the address** — the only thing between us and "the RVA is stable".
5. **Two eyes in one frame** — the real remaining stereo question.
