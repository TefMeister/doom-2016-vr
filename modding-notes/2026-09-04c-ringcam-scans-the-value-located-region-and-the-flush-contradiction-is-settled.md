# 2026-09-04c (`/pd`, dev PC, static only) — `ringcam` now scans the region the camera is actually in, and the flush contradiction is settled without a launch

**The game was not launched, and nothing here has been run.** The starred `[PD]` row is closed, and
the warning it told me to resolve first turned out to be answerable on this machine from the driver
itself.

---

## 1. The blocker it was told to resolve first, resolved — and it needed no launch

The row carried a warning: region 2 reported 27,462 flushes, which read as a contradiction of the
dossier's claim that the camera buffer is `HOST_COHERENT` and therefore not updated through the
flush path. Until that was settled, neither redesign option could be trusted.

`/gr`'s inbox drop answered the general half from the Vulkan specification: `HOST_COHERENT` means
host cache management commands *"are not needed"*, **not** that they are forbidden
`[reported 2026-09-04, first-party source]`. An engine may flush a coherent mapping unconditionally,
so a flush **count carries no information about the update route**. That makes the two statements
consistent rather than contradictory — but only if region 2 really is coherent, and nothing in the
proxy knew any region's memory type, so the question could not be asked.

It can now, and on this machine the answer does not need a launch at all
`[verified-numerically 2026-09-04, against the installed driver]`:

```
memoryTypeCount=6 memoryHeapCount=3
  type  0: flags=0x00 heap=1
  type  1: flags=0x01 heap=0
  type  2: flags=0x01 heap=0
  type  3: flags=0x06 heap=1 HOST_VISIBLE HOST_COHERENT
  type  4: flags=0x0E heap=1 HOST_VISIBLE HOST_COHERENT
  type  5: flags=0x07 heap=2 HOST_VISIBLE HOST_COHERENT
```

**Every `HOST_VISIBLE` type on this GPU is also `HOST_COHERENT`; there is no host-visible,
non-coherent type at all.** `vkMapMemory` requires `HOST_VISIBLE`, so *any* mapped region on this
machine is necessarily coherent — region 2 included. The flush count is therefore uninformative, the
dossier's claim stands, and **the second redesign option (reuse the flush path) has no evidence
behind it.**

⚠️ **This is a property of this GPU (GTX 1660 SUPER), not of the game.** A different adapter may well
expose a host-visible non-coherent type, and on such a machine the question would be live again. The
per-region reporting below is what answers it there.

## 2. How that was verified rather than asserted

Reading memory properties meant hooking `vkAllocateMemory` (handle → type index) and
`vkGetPhysicalDeviceMemoryProperties` (the type table), then parsing two structures **by hardcoded
offset**, because no Vulkan headers are installed on this machine. Hardcoded offsets taken from a
specification rather than a header are exactly the sort of thing that silently produces plausible
rubbish, and the value riding on them decides whether an interception route is alive or dead.

So the offsets are checked against a **real driver, off-game**, by extending the existing smoke test
— which already loads the built proxy and drives a genuine Vulkan session through it. It now also
asserts the parse is sane: the type count is in range, the heap count is in range, every type names
a heap that exists, at least one type is `HOST_VISIBLE` (every implementation has one), and at least
one is host-visible **and** coherent. All pass, and the proxy's own log line
`[camhunt] memory types recorded: 6` confirms the table reached the consumer.

The code also announces its own misparse at runtime: an impossible type index or type count logs
once, loudly, that coherence reporting is untrustworthy that run — so a wrong assumption on some
other machine cannot quietly produce a confident wrong verdict.

Both game imports were confirmed present before the work: `vkAllocateMemory` and
`vkGetPhysicalDeviceMemoryProperties` are both in the game's import table, so both hooks will fire.

## 3. The actual fix: `ringcam` was reading the wrong buffer

`ringcam` selected its scan target with `camhunt_biggestMapping()`, on the reasoning that the
per-draw uniform ring is by far the largest host-visible mapping, so "largest" identifies it. Two
launches disproved that for the camera specifically: a LEARN scan over the **full 3.0 MB offset
span** of the biggest mapping matched nothing, and `findvec` then returned 64 camera hits —
including a clean column-3 view matrix — **all in region index 2**, at about 100 KB
`[verified-live 2026-09-04]`. No increase of the scan cap could ever have fixed that, which is
exactly why the first widening from 512 KB to 8 MB changed nothing.

**The value-located answer already existed in the code.** `runDiscovery()` records the region index
of every camera copy it finds. The new `camhunt_cameraMapping()` simply reports the region holding
the **most** of them, and `ringcam` uses that.

Two deliberate choices:

- **Most, not first.** Copies of the same transform legitimately appear in more than one mapping,
  and the busiest is the per-draw one whose blocks are rewritten every frame — which is what a
  per-frame patch needs. Ties go to the lower index so two runs on the same state agree.
- **No fallback to the biggest mapping.** If discovery has not run there is no honest answer, so
  `ringcam` says so and does nothing. A silent fallback to the buffer already proven not to contain
  the camera is precisely what made the last two runs look like a scan-size problem. It now names
  the region it chose, once, when the choice changes.

`[compile-verified 2026-09-04]`, builds clean at `-Wall -Wextra`, 246 exports, all 96 of the game's
imports covered, smoke test passing. **Deployed** to `DOOM\vulkan-1.dll` (173,056 B); the previous
build is kept as `vulkan-1.dll.bak-2026-09-04c-pre-region` and one copy reverts.

**NOT established:** that the patch now moves the view. The region selection is corrected and the
column-3 predicate and yaw/eye write maths were already right, but nothing has been run.

## 4. What the next launch answers

The sequence is unchanged except that it now needs discovery to have run first, and the log says so
if it has not.

| step | outcome and meaning |
| --- | --- |
| `getviewpos` then `camseed <x> <y> <z>`, then `camrescan` | discovery records which region the camera copies live in — **this is now a prerequisite**, and skipping it makes `ringcam` refuse rather than scan the wrong buffer |
| `ringlearn` | expect `scanning region N (…) - value-located, not the biggest mapping`, where N should be the region `findvec` named. **If it says there is no value-located region, discovery did not run or found nothing** |
| `ringstat` | `deltas` non-zero means LEARN finally matched something, which it never did while it was scanning the wrong buffer |
| `ringyaw 20`, then look | **the view visibly rotates ⇒ the whole ring path works** and the two-submit stereo route is open to build. No rotation with `deltas` non-zero ⇒ the offsets are found but the write is not reaching the GPU — check whether the copy postdates the descriptor bind |
| any `HIT … memory=NOT host-coherent` line from `findvec` | the coherence assumption fails on that machine; the flush path is live again and this needs recording as a correction with a `Supersedes:` line |
