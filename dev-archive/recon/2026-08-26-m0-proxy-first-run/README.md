# M0 proxy first run — the log, 2026-08-26 (dev PC)

Unedited output of `doom_vk_proxy_log.txt` from the first time our `vulkan-1.dll` proxy loaded
into `DOOMx64vk.exe`. This is the evidence behind `ENGINE-DOSSIER.md` §4 (injection vector that
works) and §8 (swapchain measured in-game).

Session: a full gameplay run, **4866 frames**, no crash, no visual artefact, clean detach.

What it establishes:

- **All 246 exports resolved, 0 missing** — the generated thunk table and the explicit System32
  resolution are correct against a real 96-import consumer, not just the off-game smoke test.
- **The swapchain**: `1280x720`, `format=44` (= `VK_FORMAT_B8G8R8A8_UNORM`), `minImageCount=2`
  and `imageCount=2` — double-buffered, and sized from `r_windowWidth`/`r_windowHeight` rather
  than a fixed internal resolution.
- **`vkQueuePresentKHR` is a usable frame boundary** — the throttled counter tracks real frames.

Timing note: the last logged frame is ~18:43:45 and detach is 18:44:47, so shutdown took roughly a
minute. It completed on its own (not a hang), and is most likely DOOM's own teardown — our detach
path is one file write and all Vulkan teardown calls pass through free `jmp` thunks. **Unverified**:
nobody has yet timed a quit without the proxy installed. Do that before attributing it to us.

The run did expose a real latent bug in the proxy's shutdown path (critical section + CRT I/O under
the loader lock, a potential permanent deadlock). Fixed the same day — see the modding-notes entry
`2026-08-26-m0-proxy-verified-in-game.md`.
