# Phase 0 static recon — DOOM (2016), 2026-08-26 (dev PC)

Raw evidence behind the modding-notes entry
`2026-08-26-phase0-static-recon.md` and the `ENGINE-DOSSIER.md` rewrite of the same date.

**No live testing.** The game was not launched. Everything here is offline inspection of the
installed executables at `D:\Program Files (x86)\Steam\steamapps\common\DOOM`.

## Files

| file | what it is | why it matters |
|---|---|---|
| `pe-sections-and-imports.txt` | `llvm-objdump -h` / `-p` output for both exes | Proves **no Denuvo** (clean MSVC sections, full import table), that ASLR + Control Flow Guard are on, and that the **renderer choice is an exe-level fork** — `DOOMx64.exe` imports `OPENGL32.dll` only, `DOOMx64vk.exe` imports `vulkan-1.dll` only. Also enumerates the injection footholds (`OPENGL32`, `winmm`, `dinput8`, `dbghelp`, `wsock32`, `msimg32`). |
| `stereo-strings.txt` | every `stereo`-matching string in `DOOMx64.exe` | The headline find: id Tech 6 carries an **inherited stereo-3D render path** — `stereoRenderMode_t`, the `stereoRender_*` cvars, and the engine doc-comment stating the two stereo world views are *"both centered between the eyes"*. |
| `renderparm-camera-table.txt` | the camera slice of the renderparm name table | The engine's shader constants are **named**: `viewMatrix*`, `projectionMatrix*`, `mvpMatrix*`, `viewProjectionMatrix*`, `globalViewOrigin/Fwd/Left/Up`, and the TAA pair `mvpMatrixNoJitter*` / `mvpMatrixLast*`. |
| `cvar-block-stereo-context.txt` | the cvar registration block around the stereo cvars | Shows the `help → default → name` string layout of id Tech 6's cvar table, and captures the developers' own help text for each `stereoRender_*` cvar verbatim. |

## Method

Strings were extracted with `llvm-strings -n 4` (from the llvm-mingw toolchain already on this
machine) and searched offline. Section/import data came from `llvm-objdump -h` and `-p`.

Only **curated extracts** are committed here, never the full dumps — per the project rule, generated
interface metadata (name tables, export dumps) is fine to publish, but bulk extraction of game
content is not, and the full string dumps run to ~670k and ~750k lines respectively.

## Reproducing

```bash
cd "/d/Program Files (x86)/Steam/steamapps/common/DOOM"
llvm-objdump -h DOOMx64.exe
llvm-objdump -p DOOMx64.exe | grep -i "DLL Name" | sort -u
llvm-strings -n 4 DOOMx64.exe > gl_strings.txt
grep -iE "stereo" gl_strings.txt | sort -u
```

## Status

Everything here is **static**. The key follow-ups all need the game running and therefore wait on
the user — chiefly: does the inherited stereo path still actually render, or is it vestigial?
