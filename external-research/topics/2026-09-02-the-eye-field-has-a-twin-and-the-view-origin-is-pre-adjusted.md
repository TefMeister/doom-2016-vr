# The eye field has a twin, and the view origin is already stereo-adjusted before the renderer sees it

**Status:** 🆕 new · **Priority:** high — it targets the board's one static `[PD]` item (*"mine the
reflection database for an eye field on the view object"*) by giving that search a **pair** to look
for instead of a single field, and it flags an injection point the current plan does not use.

## Where this comes from, and what it is worth

id released Doom 3 BFG under the GPL, so `renderView_t` — the view object whose id Tech 6 descendant
this project is hunting — can be read in full from id's own source. The dossier already records the
eye field itself (`viewEyeBuffer`, −1 left / +1 right / 0 mono). What the full declaration adds is
its **neighbours**, and one architectural fact that changes where an eye offset could be applied.

`[reported 2026-09-02, from id's published Doom 3 BFG source]` — and the standing caveat applies with
force: **BFG is the 2012 id Tech 4 descendant, not id Tech 6.** Names carry across id generations
(which is the premise the board's search already rests on); byte layouts do not. Everything below is a
naming and structure **prediction** for id Tech 6, never a claim about its memory layout.

## The full field list, in declaration order

| Field | Type | id's own comment |
| --- | --- | --- |
| `viewID` | `int` | player views set a non-zero integer for model suppress/allow; subviews (mirrors, cameras) clear it |
| `fov_x`, `fov_y` | `float` | in degrees |
| `vieworg` | `idVec3` | **"has already been adjusted for stereo world seperation"** |
| `vieworg_weapon` | `idVec3` | **"has already been adjusted for stereo world seperation"** |
| `viewaxis` | `idMat3` | transformation matrix; the view looks down the **positive X axis** |
| `cramZNear` | `bool` | for cinematics, sets ZNear much lower |
| `flipProjection` | `bool` | — |
| `forceUpdate` | `bool` | — |
| `time[2]` | `int` | milliseconds, for time-dependent shader effects |
| `shaderParms[]` | `float` | free-form shader parameters |
| `globalMaterial` | `const idMaterial*` | overrides everything drawn |
| **`viewEyeBuffer`** | **`int`** | **−1 left / +1 right / 0 mono or GUI** |
| **`stereoScreenSeparation`** | **`float`** | **"projection matrix horizontal offset, positive or negative based on camera eye"** |

(id's spelling of "seperation" is theirs, quoted as written.)

## Two things this changes

### 1. The search should look for a pair, not a field

**`viewEyeBuffer` and `stereoScreenSeparation` are adjacent, and they are the last two members.** An
`int` eye selector immediately followed by a `float` horizontal offset is a far more distinctive
signature than an integer named something like "eye" on its own, and either one found in the
reflection database locates the other. If the database exposes field order or offsets, the twelve
fields above give an ordered anchor sequence to match against — `fov_x`/`fov_y` and a `time[2]` pair
are unusually recognisable.

### 2. ⭐ The eye offset is applied in **two** places, and one of them is upstream of the renderer

This is the part that is not in the dossier. In BFG the stereo eye is expressed **twice**:

- **World separation** — baked into `vieworg` (and the weapon's own origin) *before* the render view
  is handed over. The comment says so explicitly, on both fields.
- **Projection offset** — `stereoScreenSeparation`, applied as a horizontal shift of the projection
  matrix.

That is the classic separation-plus-convergence split, and it means **the camera position an id
engine renders from is already the eye position, not the head position.** If id Tech 6 keeps the
pattern, then the static global holding origin and basis that this project already found (§6h) may be
the natural place to apply a per-eye offset — a translation along the view's right axis — with the
projection-side term handled separately and independently.

That is a genuinely different injection point from driving the camera buffer, and it is worth
knowing *before* more effort goes into the buffer route. `[hypothesis]` for id Tech 6 — the BFG
comment is evidence about BFG, and this is the transferable pattern rather than a measured fact.

## What it does not do

It does not find the field in Doom 2016, and it does not touch the board's real critical path
(`multiView_60Hz`, which decides whether the two eyes are one frame or two). It makes the static
search cheaper and better-targeted, and it puts a second injection point on the table.

## Sources

- https://github.com/id-Software/DOOM-3-BFG — `neo/renderer/RenderWorld.h`, `renderView_t` (GPL; read online, described in our own words, nothing copied)
