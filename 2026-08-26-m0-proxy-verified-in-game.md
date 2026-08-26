# 2026-08-26 — M0: we are inside DOOM's Vulkan renderer

**Machine:** dev PC · **Live:** yes, user launched. Third session of the day, after
[Phase 0 static](./2026-08-26-phase0-static-recon.md) and
[Phase 0 live](./2026-08-26-phase0-complete-console-gated.md).

## Result

The `vulkan-1.dll` proxy loaded into `DOOMx64vk.exe` and ran a full gameplay session:

```
---- doom-2016-vr vulkan-1 proxy (M0) attached ----
real vulkan-1.dll loaded at 00007FFBBCDC0000; resolved 246/246 exports (0 missing)
vkCreateInstance     -> 0 (instance=000001A570424290)
vkCreateDevice       -> 0 (physDev=000001A570827E10 device=000001A57085D230)
vkCreateSwapchainKHR -> 0  1280x720 format=44 minImageCount=2
vkGetSwapchainImagesKHR -> 0  imageCount=2
vkQueuePresentKHR frame 1 / 10 / 100 / 1000 / 2000 / 3000 / 4000
---- detaching after 4866 frames ----
```

**4866 frames, no crash, no visual artefact, clean detach.** M0 is done: we own a position inside
the renderer, and uninstalling is deleting one file.

Real data for the dossier: the swapchain is **1280×720, format 44 = `VK_FORMAT_B8G8R8A8_UNORM`,
double-buffered** (`minImageCount=2`, `imageCount=2`), and its dimensions track
`r_windowWidth`/`r_windowHeight` rather than any fixed internal resolution.

## Getting there cost two wrong turns, both mine

**1. `r_renderAPI "1"` alone broke the game's launch.** I had written in the §9 cheat sheet that the
cvar "selects which exe launches". It does not — §3 of the same dossier said so correctly, and I
contradicted myself. The exes are separate build configurations, provable from their own PDB paths:

```
DOOMx64.exe    ->  ...\Zion\x64_gl\shippingretail\DOOMx64.pdb
DOOMx64vk.exe  ->  ...\Zion\x64_vulkan\shippingretail\DOOMx64vk.pdb
```

The GL build has no Vulkan backend and no reference to the vk exe, so setting the cvar to `1` while
Steam launches the GL binary asks it for a renderer it does not contain. It exits during renderer
init before writing anything — no window, no log, no Windows crash entry.

**2. Launching the vk exe directly failed too, for an unrelated reason.** No `steam_appid.txt` exists
in the game folder, and Steam normally passes the app id to the process it starts. Launched by hand
there is nothing to tell `steam_api64.dll` which app this is, `SteamAPI_Init` fails, and the game
exits instantly with the same silent signature. (`SteamAPI_RestartAppIfNecessary` is *not* imported,
so the relaunch mechanism I first suspected does not exist here.)

**The working recipe is both things together:** `r_renderAPI "1"` **and** launch `DOOMx64vk.exe`
directly with `SteamAppId=379720` in the environment. Either alone fails, with identical symptoms —
which is exactly why it took two attempts to separate.

### A methodology mistake worth recording
My "control test" was not a control. I gave two scripts intending to isolate GL-vs-Vulkan, but only
the Vulkan one set `SteamAppId` — so two variables differed again, and the tempting conclusion
("GL is broken, Vulkan works") is **not supported**. The likeliest reading is that `SteamAppId` is
required for *any* direct launch and the GL build is fine. Recorded so nobody treats "GL is broken"
as an established fact. The lesson is the obvious one: when you write the experiment yourself, check
that only one thing actually varies.

## Verdict on the Vulkan bet

Confirmed by measurement, not inference. The user reports the Vulkan build runs *"just fine, smooth
fps"* on the dev PC (GTX 1660 SUPER), and 4866 frames went through our proxy without incident. The
renderer decision from `-dev-archive/recon/2026-08-26-injection-surface/` stands.

## The slow quit, and a real bug it exposed

Quitting took roughly a minute (last frame ~18:43:45, detach logged 18:44:47). It did complete on
its own — not a hang.

Almost certainly DOOM's own teardown: our detach path is a single file write, and every Vulkan call
in shutdown goes through a free `jmp` thunk. **But it exposed a genuine latent bug in the proxy,
fixed regardless:** `DllMain`'s `DLL_PROCESS_DETACH` was taking a critical section and using CRT
file I/O while under the loader lock. If another thread were terminated holding that lock,
`EnterCriticalSection` would deadlock **forever** and the game would never finish quitting. It
didn't this time — that was luck, not design.

Fix: the final log line is now written with a bare `WriteFile` (lock-free, allocation-free, no CRT),
and `DeleteCriticalSection` only runs on a genuine dynamic `FreeLibrary` (`reserved == NULL`), never
on process termination, per MSDN. Rebuilt, smoke test still passes, both detach paths exercised.

**Not yet established:** whether an unmodified DOOM also takes ~60s to quit. A single quit without
the proxy installed would settle it, and is worth doing before anyone treats slow shutdown as ours.

## Next

1. Confirm the baseline quit time without the proxy (one launch, settles the question above).
2. **Find how `viewMatrix*` reaches the GPU** — instrument `vkMapMemory` /
   `vkFlushMappedMemoryRanges` / `vkUpdateDescriptorSets` and look for a per-frame buffer whose
   contents track the camera. We can validate arithmetically against `getviewpos`, since the basis
   (Z-up) and angle order are already known.
3. Then the stereo strategy decision.
