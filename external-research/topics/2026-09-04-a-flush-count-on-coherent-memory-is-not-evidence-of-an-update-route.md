# A flush count on coherent memory is not evidence of an update route — §10's contradiction with §6g dissolves

**Status:** 🆕 new · **Priority:** medium-high — it resolves a contradiction today's note explicitly
asked to be resolved *before relying on either path*, and it eliminates one of the two proposed
`ringcam` redesigns on the grounds that it rests on a non-signal.

## The contradiction, as recorded today

`modding-notes/2026-09-04-ringcam-scan-cap-too-small-and-virtual-pad-drives-doom.md` §10 proposes
two redesigns for `ringcam`'s region selection, and flags a problem with the second:

> ⚠️ Region 2 reported `flushes=27462`, i.e. it IS flushed — which sits oddly against §6g's "the
> camera buffer is HOST_COHERENT, so the flush path is NOT its update route." Resolve which buffer
> §6g measured before relying on either path.

The note is right to stop there. But the resolution does not require re-measuring anything: **the
two observations were never in conflict**, and the reason is in the Vulkan specification.

## What the specification actually says

From the Memory Allocation chapter, verbatim `[reported 2026-09-04, first-party source]`:

> "`VK_MEMORY_PROPERTY_HOST_COHERENT_BIT` bit specifies that the host cache management commands
> `vkFlushMappedMemoryRanges` and `vkInvalidateMappedMemoryRanges` are **not needed** to manage
> availability and visibility on the host."

**"Not needed" is not "not allowed".** The chapter carries no Valid Usage statement forbidding a
flush on coherent memory, and none was found on the `VkMemoryPropertyFlagBits` reference page
either. So an engine may call `vkFlushMappedMemoryRanges` on a coherent mapping as often as it
likes; the call is well-formed and simply does no work that was not already done.

*(Method note, because a negative from a fetch is only evidence if the fetch could have found a
positive: the same fetch that failed to find a prohibition **did** return the "not needed" sentence,
so the page was read successfully. A secondary claim seen in search summaries — that the calls are
"unnecessary and may have a performance cost" — was **not** found on either first-party page and is
therefore not repeated here as spec text.)*

## What follows for this project

**1. Neither recorded claim needs retracting.** §6g's "the camera buffer is `HOST_COHERENT`, so the
flush path is not its update route" and §10's `flushes=27462` on region 2 are both consistent with a
single ordinary explanation: **an engine that flushes unconditionally**, without branching on the
memory type. That is a common and entirely legal pattern, and it costs the engine nothing but a
call.

**2. The flush count carries no information about the update route.** This is the load-bearing
consequence. A high flush count on a mapping tells you the engine calls flush on it — not that the
flush is how data arrives there, and not that intercepting flushes would see the camera write. On
coherent memory the write is already visible before the flush is issued; the flush is a formality.
So §10's second redesign option — *"reuse camhunt's per-mapping flush path"* — **rests on a
non-signal** and should not be chosen on the strength of that number.

**3. The first option is the sound one, and it is already evidenced.** `findvec` localised the
camera copies to a tight low-offset cluster in region 2 and returned a clean column-3 view matrix of
exactly the shape `ringcam`'s `matches()` predicate looks for. A bounded per-frame scan of *that*
region's first few hundred KB, with the existing verify-column-3-before-write guard, needs no
correlation between a recorded dynamic offset and `biggestMapping`'s base — which is the exact
base/offset mismatch §10 identified as the root cause.

## ⚠️ The one thing this does not settle, and the cheap check that would

All of the above assumes **region 2 is in fact host-coherent**. If it is not — if §6g measured a
different buffer, which is precisely what §10 suspected — then those 27,462 flushes **are**
meaningful, and the flush path becomes a real candidate again.

That is a static, no-launch discriminator: **read the `VkMemoryPropertyFlags` of the memory type
backing region 2** and check for `VK_MEMORY_PROPERTY_HOST_COHERENT_BIT`. The proxy already tracks
mappings per region, so the type index is in reach at `vkAllocateMemory` / `vkMapMemory` time.

- **Coherent** ⇒ everything above holds; take redesign option 1 and ignore the flush count.
- **Not coherent** ⇒ §6g measured a different buffer, the contradiction is real rather than
  apparent, and it should be recorded as a correction with a `Supersedes:` line rather than quietly
  resolved.

Either way the answer is one field read, and it decides between two redesigns before either is
built.

## Sources

- https://docs.vulkan.org/spec/latest/chapters/memory.html — Vulkan specification, Memory Allocation
  chapter (Khronos Group). The "not needed" wording and the absence of any prohibiting Valid Usage
  statement.
- https://docs.vulkan.org/refpages/latest/refpages/source/VkMemoryPropertyFlagBits.html — checked for
  a performance note; none present.
