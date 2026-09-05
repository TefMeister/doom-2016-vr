# Reflection-database walk: the eye-field hunt, closed

**Session:** `/pd`, home PC, 2026-09-05. **The game was not launched; nothing here was run.**
Everything below is a read-only static parse of `DOOMx64vk.exe` already on disk (`pefile` +
`numpy` + `capstone`). The exe was opened `'rb'` and never written.

Supersedes nothing; it *completes* `modding-notes/2026-09-03-eye-field-hunt-two-disproofs-and-a-camrescan-status-check.md`,
whose closing suggestion — "walk outward from a known-good anchor, the records are 72-byte and
walkable" — is what this session did.

---

## 1. The database format, fully recovered

Two data structures in `.data`, both pure data with **no code references at all** (checked: no
absolute immediates via `static-disasm.py xrefs`, and no RIP-relative `lea`/`mov` sites via
`tools/riprefs.py`, for five different table and descriptor addresses). They are walked
generically at runtime, which is why the 2026-09-03 pass could only ever land in `.data` when it
xref'd a field-name string.

**Class descriptor — 56-byte records, in per-translation-unit arrays:**

```
 +0   void*   runtime slot (uninitialised .data/BSS; filled at registration)
 +8   char*   className          e.g. "renderView_t"
 +16  char*   "" (empty-string constant in every record seen)
 +24  u64     sizeof(class)      exact, not inferred
 +32  u64     0
 +40  ptr     -> field table
 +48  u64     0
```

**Field table — 72-byte records, terminated by an all-zero record:**

```
 +0   char*   typeName           e.g. "idRenderMatrix"
 +8   char*   arraySuffix        e.g. "[256]", or the ""-constant
 +16  char*   fieldName
 +24  u32     byteOffset  |  u32 size     (packed in one qword)
 +32  u64     0
 +40  char*   developer comment  (the ""-constant when absent)
 +48/+56/+64  0
```

`[verified-numerically 2026-09-05]` — the layout is self-checking and every class tested closes
exactly. `renderView_t`: last field `fogInscatterDirection` at +2112 size 12 = 2124, descriptor
`sizeof` = 2128 (4 bytes of tail padding). `idScreenView`: `guiOriginOffset` at +2320 size 4 =
2324, `sizeof` = 2336. `idRenderFrameInfo`: `idStaticList<idScreenView,1>` = 2368 = 1×2336 + 32
header, `idStaticList<idScreenView,2>` = 4704 = 2×2336 + 32. Four independent arithmetic closures
on sizes read out of three different places in the file.

## 2. Coverage — how much of the table this actually saw

| measure | count |
| --- | --- |
| records walked by `scan.py` (strict validator) and censused | **57,214** |
| records found by `coverage.py`'s looser validator, strings restricted to `.rdata` | 57,228 |
| …same looser validator, string-pointer test widened to `.rdata` \| `.data` | 57,228 (**+3 numeric candidates, +0 valid**) |
| same 72-byte shape scanned in `.rdata` instead of `.data` | 1 (incidental) |
| named classes recovered from descriptors | **4,774** |
| fields reachable from a named class | 36,290 |

`[verified-numerically 2026-09-05]` Census coverage of the field-record population is
**57,214 / 57,228 = 99.98%**. The residual 14 are records the strict validator drops on its
array-suffix / size predicate, not records in a region I failed to look at. Widening the pointer
filter moved the valid count by **zero**, which is the check that says the total is bounded by the
binary rather than by my own heuristic.

The 36,290-vs-57,214 gap is **not** missed coverage: it is field tables belonging to nested
structs and templates whose descriptor my stricter 56-byte pattern rejects. The census in
`eye-stereo-census.txt` runs over the full 57,214, not over the 36,290.

**Positive control (the search could have found a hit):** the same scan re-finds, unprompted,
every field the 2026-09-03 session had already established by other means —
`leftFrameOffset` / `rightFrameOffset` as `unsigned char[256]` at +0 and +256,
`explicitProjectionMatrix`, `useExplicitProjectionMatrix`, `forceIdentityViewMatrix`, `fov_x`,
`fov_y`, `cramZNear`, `vieworg`, `viewaxis` — with the same types, and now with offsets the
earlier pass could not derive.

## 3. Result

**Negative on the literal question, positive on the question behind it.**

- **There is no eye field on the view object, and no `stereo`-named field anywhere.**
  Zero of 57,214 field names contain `stereo`. All 59 `eye` name-hits are gameplay/AI/animation
  (`eyeJointIndex`, `eyeTrace`, `minEyePitch`, `idEyeInfo::perEyeInfo_t`, …) — **not one has a
  renderer-ish type or comment**. Every `ipd`/`hmd`/`oculus`/`vive`/`separation`/`parallax` hit is
  a substring false positive (`skipDynamic`, `reVIVE`, `convergeTime`, `meleeClipDimensions`).
  `[verified-numerically 2026-09-05, n=57,214 records, near-exhaustive]`

- **Stereo in id Tech 6 is not a field, it is a second view.** The reflection DB's own developer
  comments say so, in six places and nowhere else:

  - `idRenderFrameInfo::worldViews` — `idStaticList<idScreenView, 2>` at +2368:
    *"There is normally just one, but there will be two unique ones in split-screen multiplayer
    and **two identical ones in stereo-3D (both centered between the eyes)**."*
  - `idRenderFrameInfo::screenViews` — `idStaticList<idScreenView, 1>` at +0:
    *"…but split-screen multiplayer or **stereo-3D will define two views**."*
  - `idScreenView::viewIndex` — `int` at **+16**:
    *"determines which viewColor image will be rendered to, and which idRenderView from world
    will be used."*  ← **this is the eye selector the BFG search was looking for.**
  - `idScreenView::guiOriginOffset` — `float` at **+2320**:
    *"**for stereo 3D, the guis can be offset differently in each screenView**."*  ← the only
    surviving per-view stereo *scalar*, and it is for GUIs, not the world camera.
  - `idScreenView::screenRect` — `idScreenRect` at +0: scanout *"can be larger than
    GetWidth()/GetHeight() **when in stereo 3D modes**."*
  - `renderView_t::inhibitModelFovScale` — `bool` at +15: *"For steroescopic 3D rendering, we
    don't want to allow the hands/weapons to use a custom (inconsistant) FOV"* (id's typo).

  `[verified-numerically 2026-09-05]` for the names, types and offsets; the *reading* of them —
  that populating a second `worldViews` entry is how stereo is meant to be driven — is
  `[inferred-static 2026-09-05]`, because no code path was traced.

- **`worldViews` has compiled-in capacity 2.** Not 1. `sizeof` 4704 = 2×2336 + 32 header. The
  container the stereo path needs is present in the shipped retail binary.
  `[verified-numerically 2026-09-05]`

- **⚠️ Prior-art note, so this is not read as a new discovery:** the *"both centered between the
  eyes"* comment itself has been on the board since **2026-08-26** (Phase 0 static pass), found by
  plain string extraction, and it is the basis of dossier §6a. What is new here is that the string
  is now **attached to a field**: it is the doc comment on `idRenderFrameInfo::worldViews`, an
  `idStaticList<idScreenView, 2>` at byte +2368 of a 7,088-byte class. The floating sentence is now
  a typed container with a known capacity, a known element type and a known offset — which is what
  makes it actionable rather than merely suggestive.

  Read together with §6a: separation is applied **downstream of `renderView_t`**, in whatever
  builds `idRenderView::projectionMatrix` from it, not by any field the game sets on the view.

- **Bonus, and probably the most immediately usable thing here:** `idRenderView` (sizeof 5616)
  holds **two** `renderView_t` copies — `g` at +0 *"view parameters set by the game"* and `r` at
  **+2272** *"**latched from 'g' at EndFrame time for renderer use**"* — followed by every render
  matrix at a known fixed offset: `projectionMatrix` +4400, `projectionMatrixNoJitter` +4464,
  `inverseProjectionMatrix` +4528, `viewMatrix` +4592, `inverseViewMatrix` +4656,
  `worldSpaceMVPMatrix` +4720, and the relative-to-camera variants +4848…+5104.
  `[verified-numerically 2026-09-05]`

## 4. Files

| file | what |
| --- | --- |
| `view-family-fields.txt` | complete reflected field listing, with id's comments, for `renderView_t`, `idRenderView`, `idScreenView`, `idRenderFrameInfo`, `idViewBypass`, `idView`, `idAutoMapParms_t`, `envBlend_t`, `envBlendParms_t` |
| `eye-stereo-census.txt` | the negative result in full: every keyword sweep with its hit list, plus every stereo-mentioning comment in the whole DB |
| `class-index.txt` | all 4,774 class names with exact `sizeof` and reflected-field count |
| `camera-view-classes.txt` | the 205-class camera/view/render shortlist for the next pass |
| `tools/` | the scripts, so the whole thing re-runs in about 5 seconds |

Reproduce: `cd tools && python scan.py runs.json && python dbwalk.py && python coverage.py &&
python emit.py`. `DOOM_EXE` env var overrides the exe path (defaults to the Steam install).

## 5. What is NOT established

- No code path was traced. Nothing here shows *where* `viewIndex` is read, or what a second
  populated `worldViews` entry would do. `riprefs.py` proves only that the reflection tables
  themselves are data-only.
- Whether the stereo render path still functions when driven by populating a second worldView is
  **untested and needs the game running.**
- Whether the per-eye projection skew still exists downstream at all. The reflection DB does not
  describe it, because it lives in renderer code, not in a serialised field.
