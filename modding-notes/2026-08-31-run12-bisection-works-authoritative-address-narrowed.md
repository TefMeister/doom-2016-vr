# 2026-08-31 (run 12) — Holding the candidate set moves the game; bisection works

## The result

Holding **all 765** process-memory candidates offset by +40 X produced a **large, unmistakable
change**: the HUD vanished entirely, the weapon model vanished (only the gauntlet left), and the
view moved. `[verified-live 2026-08-31]`

Bisection then behaved exactly as a working bisection should:

| Set held | Result |
|---|---|
| all 765 | **dramatic effect** |
| first half (382) | **no effect** — HUD and weapon intact |
| second half (303) | **same dramatic effect**, reproduced |

So the authoritative address is real, it is in the candidate set, and it is in the second half.
About eight more halvings should isolate it.

## The metric under-reported again — by a lot

The pixel diff called the dramatic case **3.46%** against a 1.45% baseline, because the scene is
uniformly dark red and a moved camera in a cave still looks like a cave. Opening the image settled
it in one second.

That is the **third** time in this project a derived number pointed the wrong way while a
screenshot was unambiguous — after the input probe scoring a working backend as "no reaction", and
after the mean-pixel-diff reading 0.93% for a backend that had walked the player 15 metres. The
lesson is not "that metric was badly chosen"; it is that **a number summarising an image is not a
substitute for the image** when the question is "did the game react".

## Tooling flaw, found the hard way

`phalve` discarded the half it dropped. The first half tested negative — and the half that mattered
had already been thrown away, costing a full `psearch` / move / `pnarrow` rebuild to get back.

Fixed: `phalve` now **saves** the dropped half and **`pother`** switches to it. A negative result is
one command instead of two minutes. That turns bisection from ~20 minutes into a few minutes.

## The guards did their job, unprompted

Across three hold-all runs of 765, 382 and 303 addresses:

- every hold **auto-expired** at 599 frames
- **all originals restored** — 765/765, 382/382, 303/303
- `getviewpos` read **identical before and after** a hold, so nothing drifted
- the game held **60 fps** throughout, no freeze, no intervention needed

Given the previous run hung the game hard enough to need Task Manager, writing to 765 live
addresses at once and coming back clean every time is the guards earning their place.

## What is still unknown

The effect might not be the camera as such. Losing the HUD *and* the weapon while the view moves
looks more like the **player entity's position** being displaced — which drives the view, so it is
upstream either way, but it is not the same thing as a free camera. `pdump` on the isolated address
will show the surrounding struct and settle what we have actually found.

## Next session

1. `psearch` → move → `pnarrow` → `pholdall 40 0 0`, confirm the effect.
2. `phalve1`; if no effect, `pother`; repeat. ~8 rounds to a single address.
3. `pdump` it, read the struct, and decide whether it is the camera or the player origin.
