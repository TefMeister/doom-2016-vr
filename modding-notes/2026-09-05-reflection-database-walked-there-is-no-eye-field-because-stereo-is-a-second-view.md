# The reflection database, walked: there is no eye field, because stereo is a second *view*

**Session:** `/pd`, home PC, 2026-09-05. **The game was not launched, and nothing was run.**
Everything below is a read-only static parse of `DOOMx64vk.exe` on disk (`pefile` + `numpy` +
`capstone`). Evidence and reproduction tooling:
`dev-archive/recon/2026-09-05-reflection-eye-field-hunt/`.

## What this closes

The `[PD]` OPEN row *"mine the reflection database for an eye field on the view object"*, open
since 2026-09-02 and narrowed but not closed on 2026-09-03. **It is closed — with a negative on
the literal question and a positive on the question behind it.**

The 2026-09-03 write-up ended by suggesting the obvious next move: *"the records are 72-byte and
walkable by pointer arithmetic — walking outward from a known-good anchor to enumerate
neighbouring field names is untried."* That is what this session did, and the table turned out to
be far more tractable than "walk outward from an anchor": it has a **class descriptor array**
sitting on top of it, so the whole database can be enumerated by name.

## 1. The database format, recovered end to end

Two structures in `.data`. `[verified-numerically 2026-09-05]`

**Class descriptor, 56-byte records**, in per-translation-unit arrays:
`+8` `char* className` · `+24` `u64 sizeof(class)` · `+40` `ptr` → field table.

**Field table, 72-byte records, terminated by an all-zero record**:
`+0` `char* typeName` · `+8` `char* arraySuffix` · `+16` `char* fieldName` ·
`+24` `u32 byteOffset | u32 size` · `+40` `char* developer comment`.

The `+24` packing and the `+40` comment slot were already established on 2026-09-03 from the
`leftFrameOffset` pair; the descriptor layer and the zero terminator are new. The layout
self-checks: `renderView_t`'s last field ends at 2124 against a declared `sizeof` of 2128;
`idScreenView`'s at 2324 against 2336; `idStaticList<idScreenView,1>` is 2368 = 1×2336+32 and
`idStaticList<idScreenView,2>` is 4704 = 2×2336+32. Four independent closures, from sizes read out
of three different places in the file.

**The tables are pure data with no code references at all.** No absolute immediates
(`static-disasm.py xrefs`) and no RIP-relative `lea`/`mov` sites (a scanner written for this,
`tools/riprefs.py` — the toolkit's `xrefs` only catches absolute immediates and E8/E9, so it
cannot see a RIP-relative reference and was never going to find one). Checked against five
different table and descriptor addresses. That is *why* 2026-09-03's string xrefs always landed in
`.data` and never in code: the whole database is walked generically at runtime.
`[verified-numerically 2026-09-05]`

## 2. Coverage — stated honestly, because the result is a negative

| | |
| --- | --- |
| records walked by the strict validator and censused | **57,214** |
| records found by a looser validator (type + name only), strings in `.rdata` | 57,228 |
| …same looser validator, string-pointer test widened to `.rdata`\|`.data` | 57,228 — **+3 candidates, +0 valid** |
| same 72-byte shape scanned in `.rdata` instead of `.data` | 1 (incidental) |
| named classes recovered via descriptors | **4,774** |

**Census coverage 57,214 / 57,228 = 99.98%** `[verified-numerically 2026-09-05]`. The 14 not
censused are dropped by the strict validator's array-suffix/size predicate, not by a region I
failed to visit. Widening the pointer filter moved the valid count by **zero** — that is the check
that says the total is bounded by the binary, not by my heuristic.

**Positive control, so the negative means something.** The same scan re-finds, unprompted, every
field previously established here by other means: `leftFrameOffset`/`rightFrameOffset` as
`unsigned char[256]` at +0/+256, `explicitProjectionMatrix`, `useExplicitProjectionMatrix`,
`forceIdentityViewMatrix`, `fov_x`, `fov_y`, `cramZNear`, `vieworg`, `viewaxis` — same types, now
with offsets the earlier pass could not derive. A search that finds all of those would have found
an eye field if one existed.

**A tidy side-result:** `leftFrameOffset`/`rightFrameOffset` turn out to be the first two of a
**four**-field table — followed by `unsigned short leftKeyOffset[256]` and `rightKeyOffset[256]`.
That is an animation frame/key index buffer set, and it retires the 2026-09-03 guess that they
were per-eye *path* buffers. The disproof stands; the explanation improves.
`[verified-numerically 2026-09-05]`

## 3. The negative

- **Zero of 57,214 field names contain `stereo`.** Not one.
- **All 59 `eye` name-hits are gameplay, AI or animation** — `eyeJointIndex`, `eyeTrace`,
  `minEyePitch`, `idEyeInfo::perEyeInfo_t`, `crouchedEyeOffset`… **Not one has a renderer-ish type
  or a renderer-ish comment.**
- Every `ipd` / `hmd` / `oculus` / `vive` / `separation` / `parallax` hit is a substring false
  positive (`skipDynamic`, `re`**`vive`**`Threshold`, `convergeTime`, `meleeClipDimensions`).

`[verified-numerically 2026-09-05, n=57,214 records, near-exhaustive]`

**There is no eye field on the view object.** `renderView_t` is fully enumerated — 61 fields,
sizeof 2128, listed in `view-family-fields.txt` — and contains nothing per-eye. So is `idView`
(110 fields, sizeof 12896), `idRenderView` (35), `idScreenView` (8), `idViewBypass` (6),
`idRenderFrameInfo` (4). The BFG-derived hypothesis is not merely unmatched by name; **the
mechanism it describes is not in this engine.**

## 4. The positive — stereo is expressed as a second view, not as a field

The reflection DB carries id's own doc comments, which is a second search surface the earlier
passes never used. Searching *comments* for stereo across all 57,214 records returns exactly six
hits, and five of them are the renderer:

- **`idRenderFrameInfo::worldViews`** — `idStaticList<idScreenView, 2>` at **+2368**, sizeof 4704:
  *"There is normally just one, but there will be two unique ones in split-screen multiplayer and
  two identical ones in stereo-3D (both centered between the eyes)."*
- **`idRenderFrameInfo::screenViews`** — `idStaticList<idScreenView, 1>` at **+0**:
  *"…but split-screen multiplayer or stereo-3D will define two views."*
- **`idScreenView::viewIndex`** — `int` at **+16**: *"determines which viewColor image will be
  rendered to, and which idRenderView from world will be used."*
- **`idScreenView::guiOriginOffset`** — `float` at **+2320**: *"for stereo 3D, the guis can be
  offset differently in each screenView."*
- **`idScreenView::screenRect`** — scanout *"can be larger than GetWidth()/GetHeight() when in
  stereo 3D modes."*
- (the sixth: `renderView_t::inhibitModelFovScale`, `bool` at **+15**, id's own typo intact —
  *"For steroescopic 3D rendering…"*)

`[verified-numerically 2026-09-05]` for every name, type and offset above.

**Reading it:** the thing that selects the eye is **`idScreenView::viewIndex`** — a per-view `int`,
not a field on the view struct. Stereo is two `idScreenView` entries in
`idRenderFrameInfo::worldViews`, each with its own `viewIndex` picking its own `viewColor` target
and its own `idRenderView`. **`worldViews` has compiled-in capacity 2 in the shipped retail
binary** — 4704 = 2×2336 + 32 header, not a 1-element list. `[verified-numerically 2026-09-05]`
That the right way to drive stereo is therefore *to populate the second worldView* is
`[inferred-static 2026-09-05]` — no code path was traced.

**And `guiOriginOffset` is the only per-view stereo *scalar* left in the engine — and it is for
GUIs.** That is where `stereoRender_guiOffset` lands. There is no world-camera counterpart, which
is the structural reason the `viewEyeBuffer`/`stereoScreenSeparation` search could never have
succeeded: BFG's scalar was folded away, and what replaced it is a second view object.

⚠️ **Prior-art honesty.** The *"both centered between the eyes"* sentence is **not new** — it has
been on the board since the 2026-08-26 Phase 0 pass, found by plain string extraction, and it is
the basis of dossier §6a. What is new is that it is now **attached to a field**: a typed container,
`idStaticList<idScreenView,2>`, at a known offset, with a known capacity. A floating sentence
became a structure.

## 5. The most immediately usable thing here — `idRenderView`'s layout

`idRenderView`, sizeof 5616, holds **two** `renderView_t` copies and then every render matrix at a
fixed offset `[verified-numerically 2026-09-05]`:

```
  +0     renderView_t     g       // view parameters set by the game
  +2128  int              viewIndex          // index of this view for feedback composition
  +2272  renderView_t     r       // latched from 'g' at EndFrame time for renderer use
  +4400  idRenderMatrix   projectionMatrix
  +4464  idRenderMatrix   projectionMatrixNoJitter
  +4528  idRenderMatrix   inverseProjectionMatrix
  +4592  idRenderMatrix   viewMatrix
  +4656  idRenderMatrix   inverseViewMatrix
  +4720  idRenderMatrix   worldSpaceMVPMatrix
  +4784  idRenderMatrix   worldSpaceInverseMVPMatrix
  +4848  idRenderMatrix   viewMatrixRC        // relative-to-camera variants
  +4912  idRenderMatrix   inverseViewMatrixRC
  +4976  idRenderMatrix   worldSpaceMVPMatrixRC
  +5040  idRenderMatrix   worldSpaceInverseMVPMatrixRC
  +5296  int windowWidth / windowHeight / renderWidth / renderHeight / feedbackWidth / feedbackHeight
```

**Two things fall straight out of this.**

**(a) There is a latch, and writing after it is a no-op.** `r` is *"latched from `g` at EndFrame
time for renderer use"*. Any write to the game-side view that lands after EndFrame is discarded
for that frame. This is a candidate explanation to keep on file for future write-timing surprises
in the ring path — **but it is `[hypothesis]` as an explanation of anything we have actually
observed**, and it must not be mistaken for a diagnosis of the ring test until something is
measured against it. The trap to avoid is the familiar one: a fix that removes a symptom while
also stopping the failing path from running has proved nothing.

**(b) `renderView_t`'s layout gives the existing value-scan an anchor.** `camhunt`'s `findvec`
already locates copies of the camera origin by value. If a hit is `renderView_t::vieworg`, then
from that address `A`:

```
  A-96 = renderView_t base       A-80 = fov_x      A-76 = fov_y
  A-68 = explicitProjectionMatrix (64 bytes)       A-4  = useExplicitProjectionMatrix (bool)
  A+12 = viewaxis (idMat3, 36)   A+48 = viewBypass (idViewBypass, 72)
  A+120 = forceIdentityViewMatrix (bool)
```

A found origin can now be **verified as a `renderView_t`** rather than assumed — check that `fov_x`
and `fov_y` at `A-80`/`A-76` are plausible floats and that the bools at `A-4`/`A+120` are 0 or 1 —
and, if it verifies, `useExplicitProjectionMatrix` and `explicitProjectionMatrix` are directly
addressable. Dossier §6c has called `explicitProjectionMatrix` *"the single highest-value thing to
test live"* since 2026-08-26; this is the first time we have known where it sits.
`[inferred-static 2026-09-05]` — the offsets are verified, the identification of a `findvec` hit
as a `renderView_t` is not, and only a live read can confirm it.

## 6. Artefacts

`dev-archive/recon/2026-09-05-reflection-eye-field-hunt/`

| file | what |
| --- | --- |
| `README.md` | method, format spec, coverage, result |
| `view-family-fields.txt` | complete field listings for the nine view-chain classes, with id's comments |
| `eye-stereo-census.txt` | the negative in full — every keyword sweep with hit lists, plus every stereo comment in the DB |
| `class-index.txt` | all 4,774 class names with exact `sizeof` and field count |
| `camera-view-classes.txt` | the 205-class camera/view/render shortlist for the next pass |
| `tools/` | the scripts; the whole walk re-runs in about 5 seconds |

Field names, types, offsets and class sizes are interface metadata, not game content. No exe bytes
and no string dumps were kept.

## 7. What is NOT established

- **No code path was traced.** Nothing here shows where `viewIndex` is read, what populates
  `worldViews`, or what a second populated entry would do. The reflection tables have no code
  references at all, so there is no static anchor from them into the renderer.
- **Whether the inherited stereo path still functions** when driven by populating a second
  worldView is untested and needs the game running.
- **Whether the per-eye projection skew still exists downstream.** The reflection DB cannot answer
  this: it describes serialised fields, and the skew lives in renderer code.
- **Absence from the reflection table is not absence from the class.** These tables list
  *reflected* members only. `idRenderView` declares 35 reflected fields in 5,616 bytes — most of
  the class is unreflected. The negative in §3 is therefore exact for *"is there a reflected eye
  field"* and only strongly suggestive for *"is there an eye field"*. It is nonetheless decisive
  for the original question, because the field we were hunting was one id would certainly have
  reflected: BFG reflected its whole `renderView_t`, and this engine reflects all 61 of its own.
