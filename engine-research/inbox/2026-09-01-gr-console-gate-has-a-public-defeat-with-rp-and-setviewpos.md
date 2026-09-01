# The production-mode console gate has a public defeat — and the unlocked command set contains `rp` and `setviewpos`

**From:** `/gr doom-2016-vr`, 2026-09-01 (dev PC)
**For:** the modding session — fold into `ENGINE-DOSSIER.md` §7, §9, §12 and §13.
**Full write-up:** `external-research/topics/2026-09-01-doomlegacymod-unlocks-the-gated-console-rp-and-setviewpos.md`

## The dossier text this targets

§12: *"If gated cvars are never **constructed** (rather than merely hidden), then in-process cvar
registration won't resurrect them either and the stereo path must be driven by calling the render
code directly. **Unknown which of those two it is** — determining that is a good early proxy
milestone."*

§9, on the "❌ NOT available in retail" list: *"This is the single most important line in the
dossier."*

## What public research found

**`DOOMLegacyMod`** (emoose, updated 2024 by brunoanc) is a public mod that re-adds DOOM 2016's
hidden console interface on **retail**, **without dev mode**, via a **`dinput8.dll` proxy** that
patches *"the moment the game is started, before the Engine is even initialized."*

It reports **39 commands / 170 cvars → 290 / 6592** `[reported, /gr 2026-09-01]`. Our own live
session measured **40 / 171** `[verified-live 2026-08-26, n=1]` — the same two numbers to within one
each. It is describing the gate we measured.

The repo publishes **`doom_cmds.txt`** (377 commands with help text). It was fetched and read **in
full** this pass. Quoted verbatim:

```
rp                               Displays or modifies a renderparm
renameRenderProg                 temporarily replace a renderProg with a different one
setviewpos                       sets the current view position
setplayerviewpos                 sets the current view positon for a given player
envshot                          takes an environment shot
testImage                        displays the given image centered on screen
```

## Suggested dossier change

1. **§12 — answer the open question, at `[reported]` confidence.** 6,592 cvars with help text is an
   enumeration of structures that exist, not a modder's invention; combined with "no dev mode
   needed", the economical reading is **hidden and constructible, not absent**. Not `[verified]` —
   untested on our build.
2. **§9 — split the "NOT available in retail" list.** `rp`, `renameRenderProg`, `setviewpos`,
   `setplayerviewpos`, `envshot` and `testImage` are now confirmed real engine commands with real
   help text. They belong in a new "available *if* the gate is opened" row, not alongside things of
   uncertain status.
3. **§7 — `rp` is reachable.** The dossier already calls it *"an outstanding zero-code verification
   tool"*. It is a named read/write window onto `globalViewOrigin`, `viewMatrix*`,
   `projectionMatrix*` and the `explicitProjectionMatrix` / `explicitFov_*` family from §6c — a
   typed equivalent of everything §6h does by writing twelve floats at `+0x360F6B0`.
4. **§13 — `setviewpos` is a free cross-check for §6h.** Call it, then dump `+0x360F6B0` and see
   whether the twelve floats follow. That is a second independent confirmation of the project's most
   important address, obtained without writing memory.
5. **§11 — the `devMode_enable` dead end is now mostly moot as a *route*.** It stays interesting as
   a fact, but there is a documented path around it that needs no dev mode at all.

## Caveats to carry into the dossier with the claim

- **Closed-source** (*"The source code isn't available"*), **no licence stated**. Prior art and
  feasibility proof, not something to study line-by-line — same category as Vk3DVision. The repo
  also commits an IDA database (`dinput8.dll.i64`); that is someone else's RE work, not ours to mine.
- **Build compatibility unverified.** It targets "the April 2024 Update"; we are on
  `20240321-104810-ginger-fuchsia`. Plausibly the same release, not verified.
- **No filename collision with our proxy** (`dinput8` vs `vulkan-1`, both imported by DOOM per §11),
  but **both hook deliberately early**. If ever run together, run each alone first.
- Whether to install and run it is **the user's call**, not research's.

## The one open item, and it needs a human rather than a session

`doom_cvars.txt` is **695 KB / 11,103 lines** and automated fetch reads only the head of the
alphabet. A first attempt reported "no `stereoRender_*`" — **that negative is invalid and provably
so**, because the same pass also missed `g_fov`, which we have verified live. Recorded as a worked
instance of §11's own standing rule about negatives.

**Ask the user for two minutes with a browser: open `doom_cvars.txt` on GitHub and Ctrl-F for
`stereoRender`, `multiView`, `com_production`, `explicitProjection`.** That either confirms or kills
the dormant stereo path's reachability (§6a, §12) from a public source, before anything is installed
or launched. It is the cheapest high-value move currently on this project.

## One thing your inbox drop asked that needs no research

The 2026-08-31 drop asked whether public research could settle `GetRawInputData` vs
`GetRawInputBuffer` for id Tech 6. **Our own measurement already settles it and beats any public
source:** §11 records `llvm-objdump -p` on both shipped executables showing **zero** raw-input
imports of any kind `[measured 2026-08-31]`. Neither function is called, so the "known open risk"
noted in §10 for `autoinput_init` does not exist. No research time was spent on it.
