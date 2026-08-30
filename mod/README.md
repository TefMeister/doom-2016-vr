# DOOM (2016) VR

A VR conversion mod for **DOOM** (2016) — the goal is stereo rendering and
6DOF head tracking, built on the game's **id Tech 6** engine foundation.

> **Status: work in progress — nothing playable released yet, no code written
> yet.** This repository will hold releases only; watch it if you want to know
> the moment there is something to try.

## What this will be

DOOM (2016) runs on id Tech 6 (id Software's own successor to id Tech 5),
so this project starts from the general shape of an id Tech VR conversion:
locate the camera/projection delivery, get stereo rendering with a per-eye
view offset, then layer head tracking on top. Nothing has been
reverse-engineered yet — this repository was created to get the project
structure in place before that work begins. The real goal, as with all of
our projects, is the knowledge gained on the way there, written down and
shared so anyone can do the same for any game — see the
[engine dossier](https://github.com/TefMeister/doom-2016-vr-engine-research)
and the cross-engine
[flat-to-VR library](https://github.com/TefMeister/flat-to-vr-cross-engine-research).

## What you will need

- Your own legitimate copy of **DOOM** (2016) (this mod contains **no**
  game files).
- A PC VR headset (target runtime to be decided — SteamVR/OpenXR, in line with
  our other projects).

## The six repositories for DOOM (2016) VR

Everything for this game lives in six repositories, each with one job — so you
always know where to look. You are in **doom-2016-vr-mod**.

| Repository | What lives here |
| --- | --- |
| **doom-2016-vr-mod** ← you are here | The mod itself — once code exists, it lands here. |
| [doom-2016-vr-dev-archive](https://github.com/TefMeister/doom-2016-vr-dev-archive) | Full development history — snapshots, probes, dead ends, raw recon. |
| [doom-2016-vr-modding-notes](https://github.com/TefMeister/doom-2016-vr-modding-notes) | Readable field notes / progress ledger. |
| [doom-2016-vr-staging](https://github.com/TefMeister/doom-2016-vr-staging) 🔒 | **Private** — unverified WIP builds, cross-machine handoff. |
| [doom-2016-vr-engine-research](https://github.com/TefMeister/doom-2016-vr-engine-research) | Distilled engine reference (dossier) + reusable VR RE playbook. |
| [doom-2016-vr-external-research](https://github.com/TefMeister/doom-2016-vr-external-research) | Ongoing public-research leads, gathered separately from hands-on modding work. |

## Credits, scope, and legality

Non-commercial fan project; requires an owned copy; redistributes no original
assets. We credit everyone whose work this builds on — see
[`CREDITS.md`](CREDITS.md) — and we honour correction/removal requests from
rights holders promptly.

## Contributing & policy

See [CONTRIBUTING.md](CONTRIBUTING.md) — how we credit and link sources, our
**study-everything-public but write-our-own-code** rule (we copy no one else's
source code or files, any license or price), the terms for reusing our work
(free, with credit), and how to request a correction or removal.
