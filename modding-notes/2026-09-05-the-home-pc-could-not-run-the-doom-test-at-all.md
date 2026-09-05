# The home PC could not run the DOOM test at all — three hard-coded dev-PC paths and a config file that does not exist

`/pd`, home PC, 2026-09-05. **The game was not launched; nothing here was run.**

## What was wrong

The board has carried `install-and-launch.bat` as *the* DOOM launch route since 2026-08. On the
home PC it could never have worked, for four separate reasons found in one sitting:

1. **No proxy was deployed here at all.** `C:\Steam\steamapps\common\DOOM` contained no
   `vulkan-1.dll`. The starred `[FLAT]` row says "Deployed (`DOOM\vulkan-1.dll` 173,056 B)" — that
   was the dev PC. `[verified-numerically 2026-09-05]`
2. **`install-and-launch.bat` hard-coded `D:\Program Files (x86)\Steam\...`.** Home Steam is
   `C:\Steam\`. The copy would have failed, and — because the failure is a `copy` error, not an
   abort — the `cd /d` would then have failed too and `start "" "DOOMx64vk.exe"` would have run
   from the *script* folder.
3. **`restore-normal-play.bat` and `doom-auto.ps1` hard-coded the same dev path**, so the undo and
   the automation channel were broken here as well. `doom-auto.ps1` threw outright.
4. **⚠️ The worst one: `DOOMConfig.local` does not exist on this machine.** Both scripts set
   `r_renderAPI` with
   `(Get-Content $f) -replace '^r_renderAPI .*', 'r_renderAPI "1"' | Set-Content $f`,
   which only works if the file already exists *and* already contains the key. With the file
   absent, `Get-Content` errors, the pipeline yields nothing, and `Set-Content` **creates an empty
   file**. The Vulkan switch never happens, the launch silently runs the OpenGL build, and the
   proxy is never loaded — a run that would have looked like a proxy failure and cost a live
   session to diagnose. `[verified-numerically 2026-09-05]` — the config directory here holds
   `DOOMConfig.cfg` (445 lines, no `r_renderAPI` anywhere) and no `.local`.

## What was done

- **`scripts/_doom-paths.bat`** (new) — locates the install by looking for `DOOMx64vk.exe` across a
  candidate list, so a leftover empty directory cannot win, with `DOOM_GAME_DIR` as an override.
  Both batch files now call it. Verified on this machine: resolves to
  `C:\Steam\steamapps\common\DOOM`, exit code 0, marker present. `[verified-numerically 2026-09-05]`
- **`scripts/_set-render-api.ps1`** (new) — creates the config directory and file when absent,
  appends the key when missing, replaces it when present, keeps one dated backup the first time it
  touches an existing file, and **reads the value back** rather than trusting the write. Verified
  by a 0 → 1 → 0 round trip with read-back confirmation at each step, starting from the file not
  existing. `[verified-numerically 2026-09-05]`
- `install-and-launch.bat` now **aborts** if the render-API step fails, instead of launching into
  the silent-OpenGL trap. `restore-normal-play.bat` still resets `r_renderAPI` even when the
  install cannot be located, because that half of the restore is what unbreaks a normal Steam
  launch.
- **`doom-auto.ps1`** resolves the same candidate list when `-GameDir` is not given, and names what
  it tried if it fails.
- **The proxy is built and deployed here**: `DOOM\vulkan-1.dll`, 175,104 B, hash-verified against
  the build output. Nothing was overwritten (no file was there).

**DOOM is left at `r_renderAPI "0"`**, i.e. normal Steam play works right now. The install script
sets it to 1 when you run it.

## An honest difference to record: 175,104 B here vs 173,056 B on the dev PC

Not a source difference. `build.sh` regenerates the export list from **the local machine's**
`C:\Windows\System32\vulkan-1.dll`, and this machine's loader exports **265** functions against the
dev PC's **246** — a newer driver/loader. 19 extra thunks and names account for the 2,048-byte
difference. `[verified-numerically 2026-09-05]` The build's own check passed either way: all 96
Vulkan imports `DOOMx64vk.exe` needs are present.

**Consequence worth knowing:** `gen/vulkan-1.exports.txt`, `src/exports.def`,
`src/generated_names.h` and `src/thunks.S` are tracked in git but regenerated from the local system
DLL on every build, so building on the two machines produces opposite diffs indefinitely. I
**reverted** those four files rather than commit the churn, so the repo keeps the dev-PC baseline
and the deployed home-PC DLL was simply built from the local regeneration. The clean fix — stop
tracking generated files, or generate to a build directory — changes repo topology and is Tefa's
call, so it is flagged rather than done. `[inferred-static 2026-09-05]`

## What this does NOT establish

Nothing about whether the ring path works. The `[FLAT]` row's outcome table is untouched and
unaffected; all that has changed is that running it on this machine is now possible. The one thing
that would show this work itself is wrong is `install-and-launch.bat` reporting a game folder that
is not where DOOM actually lives, or the r_renderAPI helper failing its own read-back — both of
which now say so loudly instead of continuing.
