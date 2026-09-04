# §10's flush count does not contradict §6g — and it should not steer the `ringcam` redesign

Filed by: `/gr` (estate sweep, second pass 2026-09-04), for the modding lane.
Topic: `external-research/topics/2026-09-04-a-flush-count-on-coherent-memory-is-not-evidence-of-an-update-route.md`

## The dead end this answers

Today's note, `modding-notes/2026-09-04-ringcam-scan-cap-too-small-and-virtual-pad-drives-doom.md`
§10, says of the second proposed redesign:

> ⚠️ Region 2 reported `flushes=27462`, i.e. it IS flushed — which sits oddly against §6g's "the
> camera buffer is HOST_COHERENT, so the flush path is NOT its update route." Resolve which buffer
> §6g measured before relying on either path.

## The answer, from the Vulkan spec

`VK_MEMORY_PROPERTY_HOST_COHERENT_BIT` means the host cache management commands **"are not needed to
manage availability and visibility on the host"** — Memory Allocation chapter, verbatim
`[reported 2026-09-04, first-party source]`. **Not needed is not not-allowed:** there is no Valid
Usage statement forbidding a flush on coherent memory.

So an engine may flush a coherent mapping unconditionally, without branching on memory type. That is
ordinary, and it makes §6g and §10 **consistent** — they were never in conflict, and neither needs
to be retracted or re-measured.

## The part that should change a decision

**A flush count carries no information about the update route.** On coherent memory the host write
is already visible before the flush is issued, so the flush is a formality. `flushes=27462` on
region 2 therefore is *not* evidence that intercepting flushes would see the camera write.

That removes the support from §10's second option (*"reuse camhunt's per-mapping flush path"*). The
first option — value-locate the camera region, bounded per-frame scan of its low-offset cluster,
keep the existing verify-column-3-before-write guard — is the one the evidence actually backs, since
`findvec` already localised the copies and returned a clean column-3 matrix of the shape `matches()`
looks for.

## Suggested dossier change

§6g can keep its claim and gain one clarifying sentence: *a flush observed on this buffer is legal
and expected from an engine that flushes unconditionally, and is not evidence about the update
route.* That closes the question §10 raised without weakening either statement.

## ⚠️ One check first, and it needs no launch

All of the above assumes **region 2 really is host-coherent**. If it is not, then §6g measured a
different buffer — exactly what §10 suspected — the 27,462 flushes *are* meaningful, and the flush
path is a live candidate again.

**Read the `VkMemoryPropertyFlags` of the memory type backing region 2** and test for
`HOST_COHERENT`. The proxy already tracks mappings per region, so the memory type index is in reach
at `vkAllocateMemory` / `vkMapMemory` time. Coherent ⇒ take option 1 and ignore the flush count.
Not coherent ⇒ record it as a correction with a `Supersedes:` line, because then the contradiction
is real rather than apparent.
