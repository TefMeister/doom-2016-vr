# DOOM 2016 ships a real, retail, ungated Photo Mode whose camera detaches from the player — and the world keeps running

**Status:** 🆕 new · **Priority:** high. `ENGINE-DOSSIER.md` §9 spotted `pm_photoModeFriction` and
`pm_photoModeMaxDist "5000"` in the retail cvar set and flagged them as *"a native detached camera
exists — unexplored"*. This is that exploration, done from public sources.

## What was found

Photo Mode in DOOM (2016) is not a leftover or a developer artefact. It is a **shipped, documented,
player-facing feature**, added in a post-launch update and labelled **"DOOM Photo Mode [BETA]"** in
the game's own options menu. Critically for this project, **it is behind no console gate, no dev
mode and no cheat mode** — it is a checkbox.

**How it is reached** `[reported, multiple independent sources, 2016–2017]`:

1. From **Mission Select** (not from a normal in-progress campaign load) → **Options** → **Game** →
   enable **DOOM Photo Mode [BETA]**.
2. In-game, press **`\`** to enter it.
3. It must be re-enabled each time a level is loaded.

**What it does, once in:**

- **The camera detaches and flies free through the level**, moved with **WASD**. Users describe
  moving it well away from where the player is standing.
- **The game does not pause.** Frames are advanced individually with **E**, and *holding* E runs at
  normal speed. Enemies stay live and — in users' own words — *"the demons will follow the cam in
  photomode."*
- **The player is invisible.** One user: *"you're basically invisible in photo mode but you can see
  bullet, plasma and rocket out of invisible doomguy."* Reporting from the update's release adds the
  blunter version: **DOOM Guy has no character model**, so there is nothing to see in third person.
- **FOV is adjustable**, alongside filters and lens effects. The arrow keys move the on-screen GUI,
  and there is a key that hides the interface entirely.

**What it will not do** `[reported]`: it is restricted to **mission replay** (a deliberate
anti-cheat decision — a free camera during a first playthrough would scout enemies, pickups and
secrets), requires the campaign to have been **completed**, is **unavailable on Nightmare**, and
**refuses camera control during scripted animations and glory kills** — you may photograph them,
but not move the camera during them.

## Why this matters for this project specifically

**1. The engine already has a sanctioned "camera is not at the player" state, and it renders
correctly.** §6h's elevated-camera test proved that displacing `globalViewOrigin` by +60 units
renders the world correctly with no culling collapse and no black void — the thing Psychonauts
spent weeks failing to get. Photo Mode is the reason that works: id built and shipped a detached
camera, so the culling path was always designed to follow the camera rather than the player. What
looked like unexpected good luck is a designed-in property.

**2. The engine's own leash is 5000 units; ours is 64.** `pm_photoModeMaxDist "5000"` is visible in
our retail 171 and is almost certainly the maximum distance the photo camera may travel from the
player. The proxy's `HOLD_MAX_DELTA` currently refuses a jump over **64 units** (§6h). The engine
itself is comfortable with roughly **eighty times** that displacement. That is not an argument for
removing our clamp — it is a well-founded reason to believe a much larger safe envelope exists, and
`pm_photoModeFriction` (a smoothing/damping term) is the shape of knob a comfortable VR camera
wants.

**3. It is a free, zero-code cross-check for the `+0x360F6B0` finding.** The RVA is currently
`[verified-live 2026-09-01, n=1 process instance]` with stability only `[inferred-static]`. Entering
Photo Mode, flying the camera, and watching whether those twelve floats track the *photo* camera
rather than the player would confirm — with no memory writes at all — that the address is **the
view**, exactly as §6h concluded from the stored pitch. A second, independent line of evidence for
the project's single most important address, obtained by pressing a key.

**4. It reframes the HUD question.** §6h ends on *"find out why the HUD and weapon drop out at all —
a VR camera that costs the HUD is not finished."* Photo Mode **deliberately** hides the HUD and
leaves the player invisible with no body model. If detaching the view triggers the engine's own
"first-person elements are not valid from here" behaviour, then the HUD loss under displacement may
not be damage we are causing at all — it may be the engine doing what it was built to do. See the
companion topic on the HUD and weapon for the render-pass evidence behind that reading.

**5. A trap that will otherwise cost a session.** The activation key is documented as `\`, but a
Spanish-keyboard user reports it arriving as **`ç`**. That is the same class of failure the dossier
recorded at §10 for the console key on 2026-09-01: **DOOM binds physical scancodes, and the
character that reaches one is layout-dependent.** Any automation that opens Photo Mode must ask
`MapVirtualKeyA` at the moment it needs the key, exactly as the console command now must.

## Honest caveats

- Every fact above is `[reported]` — Steam Community threads and contemporary games-press coverage,
  most of it from 2016–2017, none of it tested by us and none of it on our `20240321` build.
- **Nobody in the sources states the actual distance limit**, whether the camera can roll, or
  whether the weapon viewmodel is drawn. The `5000` figure is our own reading of a retail cvar name,
  not something a source confirms `[inferred-static]`.
- The mission-replay restriction is a real constraint on using Photo Mode as a *development
  instrument*: it means the observations above cannot be made from an arbitrary save.
- It is a "[BETA]" feature that users at the time reported as buggy in some modes.

## Concrete next steps

1. **Next time DOOM is launched anyway** — the session already has "re-measure the RVA before
   anything else" queued (§13.1) — enable Photo Mode from Mission Select and, in it, read
   `getviewpos` and dump `+0x360F6B0`. If both follow the photo camera, §6h's "it is the view, not
   the player body" is confirmed a second way, for free.
2. Check whether the HUD and the weapon are suppressed by Photo Mode. That single observation
   discriminates between "our write breaks the HUD" and "the engine hides the HUD whenever the view
   detaches" — two very different problems with two very different fixes.
3. Read back `pm_photoModeMaxDist` and `pm_photoModeFriction` while in Photo Mode, and try raising
   the former. They are already in our retail 171, so this costs nothing and needs no unlock.
4. File `pm_photoMode*` under §6/§9 as a **live camera-decoupling lever**, not merely an "unexplored"
   curiosity.

## Sources

- [How do I use Photo mode? — DOOM General Discussions, Steam Community](https://steamcommunity.com/app/379720/discussions/0/351660338715209462/)
- [Where is my Photo mode — DOOM General Discussions, Steam Community](https://steamcommunity.com/app/379720/discussions/0/351660338713879695/)
- [Cant find Photo mode? — DOOM General Discussions, Steam Community](https://steamcommunity.com/app/379720/discussions/0/351660338713472121/)
- [Doom photomode is missing — DOOM General Discussions, Steam Community](https://steamcommunity.com/app/379720/discussions/0/351660338716958160)
- [DOOM has a gory new photo mode, here's how to use it — Critical Hit](https://www.criticalhit.net/gaming/doom-has-a-gory-new-photo-mode-heres-how-to-use-it/)
