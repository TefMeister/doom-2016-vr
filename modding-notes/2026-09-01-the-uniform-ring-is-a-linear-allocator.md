# 2026-09-01 (evening) — resubmission is legal, the uniform buffer is a linear allocator, and I nearly froze the game

Fourth session of the day. Two good measurements, one useful failure, and one live hazard I caused.

## The address question is closed

The module rebased on its own (`0x7FF74D320000` → `0x7FF71A5E0000`, no reboot), and
`base + 0x360F6B0` still held the camera — origin matching `getviewpos`, basis matching what I
predicted before dumping. **n=4 process instances across two load bases.** The offset is the
invariant; this project never needs the address hunt again.

## Both eyes can come from one recorded frame

`framespy` measured a frame: **43 render passes, 328–501 draws, 8 command buffers.** The world pass
is unmistakable at 364 draws + 3 indirect.

- **Dynamic offsets are near-universal** — 360 of the world pass's 365 descriptor binds carry them.
- **`ONE_TIME_SUBMIT` is set on none of the 8 command buffers**, and DOOM imports neither
  `vkResetCommandBuffer` nor `vkResetCommandPool`.

So the game's own command buffers may legally be **resubmitted**. That is the cheap route to
single-frame stereo: submit with the left view in the uniform buffer, copy the result out, rewrite
with the right view, submit the same buffers again. No command mirroring, and crucially **both eyes
from the same game tick** — strictly better than the alternate-frame fallback I had sketched.

## The finding that actually matters, because it invalidates an old conclusion

**The uniform buffer is a linear allocator.** Dynamic offsets climb monotonically through the frame —
656,640 → 794,112 in one capture, ~137 KB per frame, and 2.34 MB later in the session. A camera
copy's address is therefore **different every frame**.

Measured: `camrescan` found **180 copies**; the verify-before-write guard then passed **5 of 180 on
the next submit, and 0 after that.**

Two consequences, and the second is the important one:

1. Cached offsets cannot work here, by construction. Nothing is wrong with the discovery scan; the
   thing it discovers has moved by the time it is used.
2. **This retro-explains the "1–2% image change when patching camera-to-world across 72 blocks"
   result from 2026-08-31**, which was used as evidence that the GPU-side camera is *downstream*.
   That experiment was almost certainly patching stale slots the GPU no longer reads. **The
   downstream conclusion is not supported by that evidence and goes back to `[hypothesis]`.**

And by the same token my own test today — `camyaw 20` at the submit path producing no rotation — is
**untested, not disproved**. With 5 and then 0 copies actually written, it could not have produced a
positive. This is the third time on this project that a conclusion rested on a mechanism that was not
verified to be doing anything, and I walked into it again while explicitly quoting the rule.

## The live hazard, and it was the scan not the write

**`camrescan` nearly froze the game, twice, both times reported by the user.** It scans **64 MB of
write-combined memory**, which §6g already measured at **~42 ms/MB** — about **2.7 seconds** of
stalled reads competing with the renderer for memory it is actively writing. The game recovered on
its own both times, and the HUD, frame counter and gameplay were all normal afterwards.

Worth being precise about blame: **our writes were not the cause.** `patched last submit` read 0 at
the time, so nothing of ours was being written. It is the scan.

I should have predicted this. §6g contains the exact number that makes it obvious, in this same
dossier, written by an earlier session on this project. Reading "42 ms per MB" and then running a
64 MB scan against a live renderer is not a subtle mistake.

**Standing rule earned: do not run `camrescan` against a live game until it is bounded.** Everything
was disarmed the moment the user said something (`camoff`, `pholdoff`, `pholdyawoff`, `pholdalloff`,
`stop`), and the game was verified healthy afterwards.

## The tracker drifts too

After a rescan, `camstat` reported the tracked camera at `(-0.13 -11.50 9.31)` while `getviewpos`
said `(-8092.47 -2937.10 8347.39)`. The follow-the-camera logic had locked onto something that is not
the camera — which is why every guard check afterwards failed. Re-seeding from `getviewpos` is
reliable; letting it track is not.

## The fix, which comes straight out of the measurement

**Stop scanning 64 MB and stop caching addresses.** The per-frame uniform window is ~137 KB, and its
bounds are known live from the dynamic offsets flowing through `vkCmdBindDescriptorSets` — which we
now hook. So:

- scan **only the range written this frame**, at submit,
- **every frame**, never trusting an address across frames,
- and re-seed the expected camera value from the static global at `+0x360F6B0`, which is authoritative
  and free, instead of from a drifting tracker.

That is ~500× less memory touched per scan, removes the freeze risk, and removes staleness by
construction. Both problems have the same fix, which is usually a sign the diagnosis is right.

## Next

1. Build the bounded per-frame locator described above.
2. Then the two-submit stereo path, which is now known to be legal.
3. Only then worry about compositing the two eyes side by side.
