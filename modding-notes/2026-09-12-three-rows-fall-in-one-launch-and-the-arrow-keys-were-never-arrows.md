# Three rows fall in one launch, `rvproj` is demoted, and the proxy's arrow keys were never arrows (2026-09-12, home PC `RTX`, `/lm`)

One launch, fully unattended: launched, menu-driven into gameplay, tested, and closed through
the game's own menu. Evidence: `dev-archive/recon/2026-09-12-cmdroute-viewpos-move-rvhold/`.

⚠️ **First, two install traps, both of which would have made this session report nonsense.**

1. **The home PC's proxy was two days stale, and `deployed.sh check` said `OK`.** It says the
   install still matches *what was stamped here* — the stamp was from 2026-09-09, before the
   2026-09-11 command-route build existed. A rebuild-and-hash-compare caught it in one command:
   the deployed DLL contained **no `cmdroute` string at all**. ⇒ The ⭐⭐ row could never have run
   on this machine. This is the third time this exact gap has bitten (`CONVENTIONS.md` lists two
   others); **rebuild and compare, every time, before believing a stamp.**
2. **`r_renderAPI` was `0` here, so the launch ran the OpenGL exe and the proxy never loaded** —
   the failure `_set-render-api.ps1` was written for, on this machine, in 2026-09-05. It recurred
   because the config had been rewritten since. `DOOMx64.exe` in the task list is not always a
   bootstrap; check for `DOOMx64vk.exe` **and** a proxy log before concluding anything.

---

## 1. ⭐⭐ §6o is settled: the command route is POINTER, and it works with no console

```
[cmdroute] idCmdSystem: POINTER (global holds idCmdSystem*)
[cmdroute] issuing 'r_fullscreen 0' via POINTER  self=00007FF6ED17B950 fn=00007FF6E7BF74D0 (module+0x2974D0)
```

- **`cmdroute` returned `POINTER`, not `OBJECT`, not `unresolved`, not `AMBIGUOUS`.** That is the
  exact ambiguity §6o's xref census could not separate, resolved on the first run
  `[verified-live 2026-09-12, n=1 launch]`. §6o's RVAs move from `[inferred-static 2026-09-10]`
  to `[verified-live]`.
- **`cmd <text>` lands.** `cmd r_fullscreen 0` was issued and **the engine acted on it** — it left
  fullscreen and rewrote `r_fullscreen "0"` into its own config. A console command now runs with
  no console, no scancode dance and no typing route. **The whole typing dance is retired.**
- **`viewpos` reads the camera from static memory, free.** Run twice (the cache holds the previous
  answer), it returned `pos 1728.000 5440.000 6372.160  pitch -0.000 yaw 30.000` — **identical to
  the worked example recorded in the control profile on 2026-09-10**, on a different machine and a
  different process `[verified-live 2026-09-12, n=1 launch]`. Two independent sessions agreeing to
  printed precision is what makes this one trustworthy.

⚠️ **HAZARD, found the hard way: `cmd r_fullscreen 0` WEDGES THE GAME.** The window minimised to
`-32000,-32000`, the process went `Responding=False`, and the proxy log shows it recreating the
swapchain in a tight loop (59 swapchains, six of them inside 100 ms) until it stopped presenting
altogether. It had to be force-killed. **A live fullscreen→windowed switch is not safe on this
build**; set `r_fullscreen` in `DOOMConfig.local` with the game closed and relaunch. Filed to the
profile's hazards.

## 2. ⭐ Movement works — and it is `sendinput`, never `inproc-keystate`

The row was right that the retracted "the proxy cannot move the player" was an argument error
(`move` takes `fwd`/`back`/`left`/`right`/`jump`; every old attempt passed `w`). Both halves now
measured, with the position read independently by `viewpos` rather than judged by eye:

| backend | `move fwd 150` | position after |
| --- | --- | --- |
| `inproc-keystate` (the default) | issued, `input released` | **1728.000 5440.000 6372.160 — unchanged** |
| `sendinput` | issued, `input released` | **2038.518 5619.566 6340.739 — moved** |

`[verified-live 2026-09-12, n=1 each]`. The step is 358.7 units in XY with direction
**(0.866, 0.501)** — and the view yaw was **30°**, whose cosine and sine are 0.866 and 0.500. So
the player moved forward along its own facing, to three decimal places. That is not a shape match;
it is the movement law.

⇒ **`inproc-keystate` is confirmed dead for gameplay** (consistent with `SysKeyboard` never being
hooked, verified in source 2026-09-10), and `sendinput` reaches gameplay whenever the game is the
foreground window. `status` reports `sendinput unavailable` while it is not — that line is a
foreground check, not a capability check.

## 3. ⭐⭐ §6c was already ANSWERED YES — and today shows `rvproj` cannot be trusted to find the view

⚠️ **I nearly filed the opposite of this.** The first draft of this note read the result below as
"§6c is still open". It is not: **§6j answered §6c YES on 2026-09-08**, by holding
`base + 0x360F6B0` and measuring a luma delta of 24–26 against a 7.24 animation floor, reverting on
release, with two different fov values giving different pictures `[verified-live 2026-09-08, n=2 arms]`.
That stands untouched. What today adds is a warning about the *tool used to pick an address*.

Two-pass `psearch` → `pnarrow` → `rvscan` on this process: 1525 candidates → 460 survivors →
**9 passing the shape test**, all `conf 100/100`, all reading
`vieworg=(2289.02 5763.50 6334.19) fov=(89.47 58.72)`. `rvproj` then sorted them:

| candidate | `rvproj` verdict | what it actually does |
| --- | --- | --- |
| `00000237324DA0D0` | ✅ "the hit is `idRenderView::g`" | **held at fov 55 → picture UNCHANGED** |
| `00000237C323F450` | ✅ "the hit is `idRenderView::g`" | not held this session |
| `000000818C3E9200` (strongest by conf) | ✗ neither placement confirmed | — |
| **`00007FF6EAF6F6B0` = module+`0x360F6B0`** | ✗ **neither placement confirmed** | **§6j's KNOWN-GOOD address — visibly drives the picture** |
| `000002383900A660` | ✗ neither placement confirmed | — |

`[verified-live 2026-09-12, n=1 launch]`

⇒ **`rvproj`'s +4400/+4528 placement check gives a FALSE NEGATIVE on the one address proven to
drive the frame, and false positives on two heap hits that do not.** Its own output already says
"the offsets are verified, the identification of any one hit is not" — today puts a measurement
behind that sentence. **Do not use `rvproj` to choose which candidate to hold.** The live
experiment is the identifier; the structural check is not.

⚠️ And the same trap sits in the 2026-09-10 board row, which recommended trying the **image
addresses first "for reproducibility"**. That advice was right for the wrong stated reason: the
image address is the right one not because it is static but because §6j already proved it drives
the picture. It is also the camera global the control profile records from `pdump`.

**The hold that was run, for the record.** `rvhold 00000237324DA0D0 55 900`, captured inside the
arming window (checked against the release timestamp — the trap that made 2026-09-08's first
attempt read as a null):

- Picture identical before and after: same framing, same fov, same compass bearing (258.8).
- Counters: `present writes=899 HELD=899 ZEROED=0` / `submit writes=1800 HELD=900 ZEROED=899 flag-cleared=899`.

⚠️ **The ZEROED-at-submit pattern is NOT the explanation**, which is the other thing the first
draft got wrong: §6j's two successful arms show the *same* pattern (submit ZEROED 3443 and 3579 of
~7200) and the picture changed anyway. The engine clearing at submit is normal here. The honest
reading of today's null is simply **this heap address is not the view the frame is drawn from**,
`[verified-live 2026-09-12, n=1]`.

**What is genuinely new and useful:** the candidate set can be cut from 9 to 1 by asking §6j's
address first, and `rvproj` should be demoted from "identifier" to "structural hint".

## 4. ⚠️ NEW DEFECT: the proxy's arrow keys are not arrow keys

`key 0x28` (VK_DOWN) sent **five times** at the pause menu — the highlight never left `RESUME`.
An external `SendInput` with **scancode `0x50` + `KEYEVENTF_EXTENDEDKEY`** moved it to
`EXIT TO DESKTOP` on the first try `[verified-live 2026-09-12, n=1 each, same menu, seconds apart]`.

This is exactly the primitive the control profile already warns about in general terms — *"arrow
keys need `KEYEVENTF_EXTENDEDKEY`; without it scancode `0x50` is numpad-2, the menu ignores it, and
nothing errors"* — and **the proxy itself has the bug.** `key esc` and `key enter` work fine, which
is what hides it: navigation looks like "this game ignores the keyboard" while confirmation works.

⚠️ **It also means every earlier "the arrows did nothing" reading from this proxy is void** — the
arrows were never delivered as arrows. Nothing in this session depended on one, because the whole
menu route happens to be Enter on an already-correct default.

**Fix (one `[PD]` job):** set `KEYEVENTF_EXTENDEDKEY` for the extended set — arrows, Home/End,
PgUp/PgDn, Insert/Delete, right-Ctrl/Alt — in the proxy's `sendinput` path. Helper that proves it:
`scripts/sendkey.ps1` shape in this session's recon folder.

## 5. All five automation capabilities, by name

| # | capability | this session |
| --- | --- | --- |
| 1 | self-launch | ✅ Steam URL, twice (second after the renderer fix) |
| 2 | menu → gameplay | ✅ unattended: main menu → CAMPAIGN → GAME SLOT 1 → CONTINUE → Space → Mars surface |
| 3 | console / exec commands | ✅ **with no console at all** (`cmd`), plus the file channel |
| 4 | character + camera | ✅ `move fwd` on `sendinput`, confirmed by an independent position read |
| 5 | self-close | ✅ gracefully through the pause menu, highlight verified at every destructive step |

⚠️ Capability 2 currently depends on every menu step being **Enter on an already-correct default**.
It is not general navigation until §4 is fixed — any route needing an arrow will silently fail.

## 6. What is NOT established

- **What the two `rvproj`-confirmed heap hits actually are.** One was held and did nothing; the
  other was not held at all. They may be copies, shadow/cubemap views, or a stale frame's view.
- **Why `rvproj` rejects module+`0x360F6B0`.** Either the +4400/+4528 offsets do not hold for that
  object, or it is a camera field inside something that is not an `idRenderView` — and §6j's result
  means the engine renders from it regardless. Not investigated today.
- **Whether §6j's inverted fov mapping is still inverted.** Not re-tested; today's hold was on the
  wrong address to tell.
- **Whether the `cmd` wedge is specific to `r_fullscreen`** or to any cvar that forces a swapchain
  rebuild. Only one command was tried, deliberately.
