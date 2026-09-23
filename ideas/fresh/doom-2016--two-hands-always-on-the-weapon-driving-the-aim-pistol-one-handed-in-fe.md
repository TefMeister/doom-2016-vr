# Two hands always on the weapon, driving the aim — pistol one-handed in feel, two-handed in look

Order: 2000
From: mod-ideas `games/doom-2016.md` (<https://github.com/TefMeister/mod-ideas/blob/main/games/doom-2016.md>), copied 2026-09-23

`[raw]` `[needs something we don't have]`

> *"2 hands always stay on the weapon and drive 2-handing, apart from a pistol where left hand does
> nothing, just visually stays on the weapon"* — 2026-09-12

Both hands hold the gun and **both contribute to where it points** — the real two-handed grip, where
the off hand steadies and steers rather than just being attached. The exception is the pistol: the
left hand still *sits* on the weapon so you never see a floating single hand, but it contributes
nothing to the aim.

**What it'd take**, in the order the pieces have to arrive:

1. **Motion-controller poses reaching the game at all.** Nothing in this project reads a controller
   today. That is the real blocker, and it is upstream of everything else here.
2. **Control of the first-person weapon transform.** Not known to be reachable — nobody has looked
   for where the viewmodel's transform lives. The camera globals were found by exactly this kind of
   hunt, so it is a known *shape* of problem, not a new one.
3. **The two-handed aim law itself** — the easy part, and the only part that is pure maths: aim
   direction from the dominant hand to the support hand, with the weapon's roll from the line between
   them. This is well-trodden in VR shooters and does not need the engine to cooperate.
4. **A second hand to show.** DOOM's viewmodels are authored with the arms baked into the weapon mesh
   in most cases, so "put the left hand on it" may mean *the model already has one* — in which case
   the pistol case is nearly free and the rifle case is about matching a pose, not adding a limb.
   Unchecked.

⚠️ **None of this has been checked against the engine** — it is reasoned from the project's recorded
state. Step 4 in particular could go either way and is cheap to settle by looking at one viewmodel.

**Cross-reference:** also a **weapons** idea (per-weapon behaviour: pistol differs from everything
else) and a **VR** idea (it only means anything once there is a headset view). Filed under controls
because what it *does* is change how you hold and aim.

---

_Categories appear as they arrive — gameplay, weapons, visuals, audio, VR, level design, UI, controls,
enemies, performance._

**To add one:** `[doom 2016] your idea` — anywhere, any time. ⚠️ `[doom]` on its own means classic
Doom 1 & 2 and lands on a different page.
