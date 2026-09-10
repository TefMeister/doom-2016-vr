# 2026-09-10 — ⭐⭐⭐ the console can be driven WITHOUT the keyboard, `getviewpos` caches its answer in memory, and the `.local` bind risk is disproved

*Author: `/lm` reader helper, doom-2016-vr, dev PC. **No launch. Nothing written under the game
install or `Saved Games`.** Method: static disassembly of `DOOMx64vk.exe` (pefile + capstone,
file-on-disk only, no debugger and no attach), plus the game's own on-disk console dumps.*

*Companion to `inbox/2026-09-10-lm-binds-numpad-names-ctest-reading-and-rvproj-offsets.md`, which
establishes that this binary's data strings are NOT hidden by Denuvo. This file extends that: **the
CODE is in the clear too.** `.text` disassembles normally and cross-references resolve. Static
analysis of this executable is cheap and should be the first move on any future question here.*

All addresses below are given as **RVAs** (image base `0x140000000`), because §6h already records
that RVAs hold across module bases here while absolute addresses do not.

---

## 1. 🚨 THE HEADLINE — `idCmdSystem::BufferCommandText` makes the whole typing problem OPTIONAL

**The proxy is already in-process. It can execute any console command by one indirect call, with no
keyboard, no console window, no focus, no dead key, no `WM_CHAR`, and no bind.**

```
    void  *cmdSys = *(void **)(moduleBase + 0x2F451C0);   /* idCmdSystem instance   */
    void **vtbl   = *(void ***)cmdSys;
    ((void (*)(void *, const char *))vtbl[0x50 / 8])(cmdSys, "getviewpos");
```

### How the slots were identified — by census, not by guesswork
466 code sites load the global at RVA `0x2F451C0`. Grouping them by the vtable slot they then call,
and reporting any string operand in the same window, is decisive:

| slot | sites | string operands seen at those sites | reading |
|---|---|---|---|
| `+0x20` | 200 | `('dir', 'lists a folder')`, `('path', 'lists search paths')`, `('bot_add', 'Spawns a bot')` … | **`AddCommand(name, fn, desc, flags)`** |
| `+0x48` | 36 | `sys_dumpMemory`, `giveAllMaxedOutWeapons`, `upgradeHealthCapacity 4` | buffers command text (a second exec mode) |
| **`+0x50`** | **151** | **`reload`, `quit`, `disconnect`, `RestartMapFromStart `, `resourceExec default.cfg -s`** | **`BufferCommandText(this, const char *text)`** |
| `+0x60` | 19 | none — no arguments | **`ExecuteCommandBuffer(this)`** |

`[verified-numerically 2026-09-10]` for the census; `[inferred-static]` for the slot *names*.

### The calling convention, from three independent sites
`0x8F3559` (`"reload"`), `0x1A9B274` (`"quit"`) and `0x156BF07` (`"resourceExec default.cfg -s"`) are
byte-for-byte the same shape:

```
    mov rcx, [rip+…]      ; the idCmdSystem instance pointer  (RVA 0x2F451C0)
    mov rax, [rcx]        ; its vtable
    lea rdx, [rip+…]      ; a plain NUL-terminated ASCII command string
    call [rax+0x50]       ; two arguments only: (this, text)
```

**Two arguments. No exec-mode enum.** `[inferred-static 2026-09-10, n=3 call sites with literal
command strings]`

⚠️ **`reload` and `quit` call `+0x50` and do NOT then call `+0x60`.** The engine drains its own
command buffer on the next frame. So the proxy should call `+0x50` only and let the game execute it
— simpler, and it avoids re-entering the command system from the wrong thread.

### What this changes
- `getviewpos` needs **no bind, no `type`, no `ctest`, no console at all.**
- So do `conDump`, `com_showCameraPosition 1`, `g_fov`, `writeConfig`, `vid_restart` — anything.
- It also removes every reason to write to `DOOMConfig.local`, and with it the Steam Cloud confound
  the `/gr` drop raised.

### ⚠️ Honest limits — none of this has been run
1. **`[inferred-static]`. Nothing here has been executed.**
2. **Thread safety is the real risk.** `BufferCommandText` appends to a shared buffer that the main
   thread drains. The proxy's per-frame pump runs on the present/render thread. Issue the call
   **once**, latched behind a flag — never per frame — and expect the possibility of a race. This is
   the one place where the cheap route could crash the game rather than merely fail.
3. **Verify before dereferencing:** read the instance pointer, then its vtable pointer, and check
   both land inside the module's mapped range before calling. A null or wild pointer here is a
   crash, and the instance may not exist before the command system is constructed.
4. Denuvo does not appear to touch these — they are ordinary indirect calls through a `.rdata`
   vtable — but a runtime vtable hook would move the slots. The range check above also catches that.

---

## 2. ⭐⭐ `getviewpos` CACHES ITS ANSWER IN STATIC MEMORY — the number can be READ, not scraped

`getviewpos`'s handler (RVA `0xB595C0`) does three things: fetch the view, **print it**, and **store
it into six static floats**:

| RVA | field |
|---|---|
| `0x5B5CB90` | view origin **x** |
| `0x5B5CB94` | view origin **y** |
| `0x5B5CB98` | view origin **z** |
| `0x5B5CBA0` | angle 0 (pitch) |
| `0x5B5CBA4` | angle 1 (yaw) |
| `0x5B5CBA8` | angle 2 — written, but never read by either consumer |

`[verified-numerically 2026-09-10]` (the six `movss` stores are in the handler)

**A full census of code touching those addresses returns exactly three functions:** `getviewpos`
(the only writer) and two readers at RVA `0xB5CD6F` and `0xB5CF83`, both of which first compare an
argument against the literal string `"last"` — i.e. `setviewpos last` / a teleport-to-last command
reusing the cache.

**So the cache is populated by `getviewpos` and by nothing else.** It is not a live per-frame value.
`[verified-numerically 2026-09-10]`

### Why that is still the answer to the ⭐⭐ row
Combined with §1: **trigger `getviewpos` through `BufferCommandText`, then read six floats.** No
console text, no `conDump`, no file polling, no screen reading, no human. The position arrives as
floats rather than as a string that has to be parsed back.

**The stronger follow-on, if the cache proves awkward:** the handler gets its data from
`call RVA 0xE6EEB0` with `(rcx = object, rdx = &out_origin, r8 = &out_axis)`, the object coming from
`call RVA 0x391070` on the global at RVA `0x5B0F6D0`. That would give origin **and the 3×3 basis**
with no command at all — but it means calling an engine method directly, which is a bigger risk than
buffering a command string. **Try the command route first.** `[inferred-static]`

⚠️ **The cache is stale until `getviewpos` has run at least once**, and it holds a *snapshot*. Read
it in the frame after the command, not before.

---

## 3. ✅ CONFIG EXEC ORDER — SETTLED. `.cfg` FIRST, `.local` SECOND. The `unbindall` risk is DISPROVED.

My earlier §2 raised the risk that `DOOMConfig.cfg`'s per-bindset `unbindall` might run *after* a
bind placed in `DOOMConfig.local` and silently erase it — a confound that would read as "the engine
ignores `bind` in `.local`". **It does not happen.**

Both filename strings are referenced from one function around RVA `0x156BA40`, and the order is
unambiguous `[verified-numerically 2026-09-10]`:

1. `0x156BA80` — read **`DOOMConfig.cfg`** (buffer → `[rbp-0x68]`, length → `rdi`)
2. `0x156BAB5` — read **`DOOMConfig.local`** (buffer → `[rbp-0x60]`, length → `r15`)
3. `0x156BB01` — if the **`.cfg`** buffer is non-null: load it into a lexer, version-check it, then
   `call [vtbl+0x50]` (BufferCommandText) and `call [vtbl+0x60]` (ExecuteCommandBuffer) on the
   idCmdSystem global identified in §1
4. `0x156BC57` — then the same, with the **`.local`** buffer

**`.local` is buffered and executed AFTER `.cfg`, in the same function, sequentially. `.cfg`'s
`unbindall` cannot reach a bind in `.local`.** The 2026-09-09b row's question 1 ("does the engine
accept `bind` in that file at all") is now the only one of the two that is open, and it is no longer
confounded by question 2.

### 🚨 BUT THERE IS A DIFFERENT GATE, AND IT IS EASY TO TRIP
Before either file is executed, the code lexes its **first token** and requires:

- token type 4 (an identifier) whose text is exactly **`configVersion`**, then
- a following integer equal to **7** (the current version constant lives at RVA `0x2828CE8` and
  reads **7**)

**If that header is absent or wrong, the file is not executed at all — silently, with no message.**
`[verified-numerically 2026-09-10]`

✅ Both files on this machine currently satisfy it: `DOOMConfig.cfg` opens with `configVersion 7`,
and `DOOMConfig.local` opens with a `//` comment (skipped by the lexer) then `configVersion 7`.
**Any hand edit must keep that header as the first non-comment line.** A hand-edited file that lost
it would look exactly like "the engine ignores `bind` here".

### A third persistence location nobody has mentioned
The binary also carries `numBindSets`, `keyBindings_%d`, `keyBinding_%d`, `numKeyBindings` and
`idKeyInput::Serialize - Different number max bindsets in profile (%d) and current code (%d)` — so
**binds are also serialised into the player PROFILE**, not only into `DOOMConfig.cfg`. A profile load
is a further opportunity for a hand-added bind to be overwritten. `[inferred-static]` Another reason
to prefer §1 over the file route.

---

## 4. ⭐ `conDump` — it NEVER overwrites, and it caps at the last 4095 lines

Handler at RVA `0x1683BC0`, registered at RVA `0x219E60` with the description *"dumps the console
text to a file"*. `[verified-numerically 2026-09-10]`

- **Requires exactly one argument** (`argc == 2`), else it prints usage and returns.
- Strips any extension from the argument and forces **`.txt`**.
- **Then it loops while the file already exists**, each time stripping the extension, appending
  `_<n>` with an incrementing counter, and re-adding `.txt`. Only when the name is free does it open
  the file (mode `4` — a plain write open) and dump.
- **So the answer is neither append nor truncate: `conDump` auto-uniquifies and never clobbers.**
  `conDump viewpos.txt` writes `viewpos.txt` the first time, then a suffixed name (`viewpos_0.txt`,
  and the suffix compounds on further collisions).

  🚨 **Operational consequence: an unattended loop must NOT poll a fixed path.** After the first
  dump, fresh output is in a *different* file each time. Scan the directory for the newest matching
  file by modification time, or delete the previous dump before each call. A harness that reads
  `viewpos.txt` every cycle would read the **first** capture forever and report a frozen camera.

- **The dump is capped at the last `0xFFF` = 4095 console lines** (`lea eax, [r8 - 0xfff]` on the
  console's line count, clamped at zero). A long session's early output is gone.
- On failure it prints `couldn't open %s`.

### Where it writes — confirmed empirically
Through the same filesystem object the config loader uses (RVA `0x2F451C8`), whose save path is the
user config directory. The existing dumps `doomcmds.txt`, `doomcvars.txt`, `doomcvars2.txt` and
`doomview.txt` are all in `~/Saved Games/id Software/DOOM/base/`. `[verified-numerically 2026-09-10]`

## 4b. ✅ The console print path IS fed while the console is HIDDEN

`getviewpos` prints through **RVA `0x282E70` with a `"%s"` format** — the engine's common Printf,
the same function `conDump`'s own usage message uses, and distinct from the Warning printer at RVA
`0x283C60`. That is the path every startup line takes, long before any console can be opened, and
the captured `doomview.txt` contains 121 KB of engine output the human never had on screen.

**Console *visibility* controls drawing, not the buffer.** `getviewpos` output reaches the dumpable
buffer whether or not the console is showing. `[inferred-static]` — strong, but it is an inference
from the call target, not a live observation.

⚠️ Note this whole section is now a **fallback**: §1 and §2 together make `conDump` unnecessary.

---

## 5. 🚨 `ctest` HAS ALREADY BEEN RUN — the result is on disk, and it means something different

`~/Saved Games/id Software/DOOM/base/consoleHistory.txt` (plain ASCII, despite the tooling refusing
it as UTF-8) contains, among the human's typed lines:

```
    getviewpos
    0122
    getviewpos
    conDump viewpos.txt
```

**`0122` is a `ctest` read-out**, and §11 already records it (*"`ctest` → `]0122`, the `3` never
lands"*). Decoded against the route order in `autoinput_routeProbe()`:

| digit | route | verdict |
|---|---|---|
| `0` | sendinput-scancode | **lands**, exactly once |
| `1` | postmessage-key | **lands**, exactly once |
| `2` | postmessage-char | **lands TWICE** |
| `3` | inproc-keystate | **never lands** |

### ⭐ The doubled `2` is `TranslateMessage`, not auto-repeat — and it explains the old flakiness
Route 2 posts `WM_KEYDOWN`/`WM_KEYUP` **plus** an explicit `WM_CHAR`. DOOM runs a real
`PeekMessage`/`TranslateMessage`/`DispatchMessage` pump, and `TranslateMessage` synthesises a
`WM_CHAR` from a *posted* `WM_KEYDOWN` on its own. So route 2 delivers the character twice while
route 1 delivers it once — precisely the observed `0122`.

The old reading table called any repeated digit "auto-repeat, the frame rate is too low". **That
reading is wrong for digit `2`**, and the separator is free: auto-repeat bites the *sendinput* route
hardest, since that is the one held down across frames — and `0` arrived single.

### 🚨 CONSEQUENCE, and it is the practical one
**`postchar` is the proxy's DEFAULT type route (`static int g_typeRoute = AT_POSTCHAR;`), and on
this game it may double every character.** `type getviewpos` would arrive as
`ggeettvviieewwppooss` — not a valid command, and indistinguishable from "typing is unreliable".

- ⭐ **Use `typeroute postkey` for typing words into this game's console**, not the default. Route 1
  relies on `TranslateMessage` alone and lands one character per key. `[inferred-static]` — the
  doubling is measured; that `postkey` is the fix is the inference.
- This is a candidate explanation for the long-standing *"the proxy's own `type` landed 1 character
  of `getviewpos`"* symptom, though not a complete one — doubling alone would give 20 characters,
  not 1, so **at least one other failure was also in play**. Hold both.
- ⚠️ `0` landing in that run means the dead key was **not** live at that moment (or was flushed by
  hand). It does not retire the dead-key hazard; it is layout-dependent (§10).
- ⚠️ `consoleHistory.txt` is undated, so attributing `0122` to `ctest` rests on §11 already recording
  it and on the digits decoding cleanly. `[measured]`, not `[verified-live]`.

### ✅ `ctest` is now trustworthy without remembering a trick — patched and compile-verified
`staging/doom-2016-vr/proxy-vulkan/src/autoinput.c`, `autoinput_routeProbe()`:

1. **Sends space + backspace down the SENDINPUT route ahead of the digits**, to absorb the console
   key's pending dead-key accent. It must travel the OS input stack, because that is where the
   pending composition lives — a posted `WM_CHAR` would not consume it. Harmless when unnecessary.
2. **Emits the "no key-state hooks installed" warning** that `autoinput_setTypeRoute()` has and that
   `routeProbe` was bypassing (it assigns `g_typeRoute` directly, because it needs a per-tap route).
   A missing `3` was ambiguous between "the console ignores key state" and "our hooks never landed";
   now the log says which.
3. The reading table in both `autoinput.c` and `autocmd.c` now documents `0122` and the
   `TranslateMessage` doubling.

`[compile-verified 2026-09-10]` — clean build, 265 exports, all 96 imports covered, host suites
`116 checks, 0 failures` and `all passed`. **NOT deployed** — the `/lm` session owns every write to
the game folder.

---

## 6. `bind` takes NO bindset argument — and the numpad has a second set of names

From the binary's own usage strings `[verified-numerically 2026-09-10]`:

```
    bind <key> [command] : attach a command to a key
    unbind <key> : remove commands from a key
    "%s" isn't a valid key
    "%s" is not bound
```

- **`bind` is two positional arguments. There is no bindset parameter.** A bind lands in whatever
  bindset the **`bindset` cvar** currently names ("value of current bind set"; live value `"0"`). To
  target a bindset you would set the cvar first, then bind.
- `key_deviceBindOverride` (*"if > -1 will use that device to exec bind commands on"*) and
  `key_debugBinds` (*"if 1 then prints debug info as bind commands are received"*) exist in the
  binary. **`key_debugBinds` would have answered the `.local` question directly at runtime — but
  neither is registered in retail** (absent from the live `listCvars` dump). Production-gated, like
  the `stereoRender_*` family.
- The config **writer**'s format strings are `bindset %d`, `unbindall`, `bind "%s" "%s"` — matching
  `DOOMConfig.cfg`'s structure exactly, and confirming that every bindset block is rewritten
  wholesale on save.
- The engine logs `Cvar 'bindset' was modified to '0'` (captured in `doomcvars.txt`), so **a bindset
  switch is visible in a `conDump`** if anyone needs to check whether one happens at map load. I
  could not settle from static analysis alone whether a map load switches bindsets — the cvar is
  written from many places. `[hypothesis]` **Not determined statically.**

### ⚠️ A second numpad naming table exists — bind BOTH names
Beyond the DIK-ordered table reported in the companion file (`KP_0`–`KP_9`, `KP_DOT`, …), the binary
carries a short alias list immediately after it:

```
    ALT  CTRL  SHIFT
    KP_HOME  KP_UPARROW  KP_PGUP  KP_LEFTARROW  KP_RIGHTARROW
    KP_END  KP_DOWNARROW  KP_PGDN  KP_INS  KP_DEL  KP_NUMLOCK
```

These are the classic Quake-heritage **NumLock-off** names for the same physical keys
(`KP_END`=KP_1, `KP_DOWNARROW`=KP_2, `KP_PGDN`=KP_3, `KP_INS`=KP_0, `KP_DEL`=KP_DOT, …). Which of
the two tables `bind`'s parser consults — and whether it depends on NumLock state — is **not settled
statically**. `[hypothesis]`

**Cheap robustness, if the bind route is used at all:** bind both spellings.

```
    bind "KP_1" "getviewpos"     +     bind "KP_END" "getviewpos"
```

Neither name is bound by default in any of the eleven bindsets, so there is nothing to collide with
and no downside.

---

## 7. Smaller things worth recording

- **`setviewpos` is registered in the binary**, immediately after `getviewpos` in the same function,
  described as *"sets the current view position"* — and `setviewpos 1731 5442 6420` appears in
  `consoleHistory.txt`, so it has been attempted. **It is NOT in the live `listCmds` (40 commands)**,
  so it is presumably production-gated like `noclip`. If it could ever be reached it would be a
  direct camera teleport. `[inferred-static]` — worth a line in §9's "NOT available in retail" list
  rather than a lead to chase.
- **`activateConsole` IS a registered retail command** — a way to open the console that never touches
  the dead key. Moot if §1 works, useful if it does not.
- **The `+`-argument list, revisited.** `+set` sits beside `idCommonLocal::Launch`,
  `Restarting executable in to different graphics API....` and `+r_renderAPI -2`. Combined with §1
  this is now firmly the lowest-value thread on the board: there is a supported in-process way to
  run commands, so a launch-argument route buys nothing.

---

## 8. Suggested order for the next launch

1. **`BufferCommandText("getviewpos")` from the proxy, once, behind a flag** → then read the six
   floats at RVA `0x5B5CB90` / `0x5B5CBA0`. If that works, the ⭐⭐ row is closed and the bind, the
   `.local` edit, `conDump`, `ctest` and the Steam Cloud confound all become irrelevant at once.
2. If the pointer chain does not validate, fall back to the numpad bind (**both** spellings) plus the
   memory read — the read still removes the text-scraping half of the problem.
3. Only if both fail, fall back to `typeroute postkey` + `type getviewpos` + `conDump`, remembering
   that `conDump` writes a **new file every time**.
