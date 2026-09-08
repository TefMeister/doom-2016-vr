"""doomdrive.py - drive DOOM (2016) from outside, for the /lm lane.

Mechanism from flat-to-vr-RE-toolkit/tools/game-harness.py (BitBlt capture, scancode keys,
focus first). Game-specific facts from ai-game-control-profiles/profiles/doom-2016.json:
  - the window title is "DOOMx64vk" (Vulkan) / "DOOMx64" (GL), NOT "DOOM" as the profile
    said; match on the "DOOMx64" prefix, never the bare substring "DOOM", or a terminal whose
    title merely mentions the game wins the search
  - DOOM must be the foreground window for synthetic keyboard/mouse (sendinput follows focus)
  - drive menus by KEYBOARD only: a mouse click on a main-menu promo tile opens the Steam
    store overlay
  - the window does not exist for several seconds after launch

Usage:
    python doomdrive.py state
    python doomdrive.py shot out.png
    python doomdrive.py key <name> [--repeat N]
"""
import ctypes
import ctypes.wintypes as w
import importlib.util
import os
import sys
import time

TOOLKIT_CANDIDATES = [
    r"D:\claude video game stuff\github-backups\flat-to-vr-RE-toolkit\tools\game-harness.py",
    r"C:\Users\TD3KX\github-backups\flat-to-vr-RE-toolkit\tools\game-harness.py",
]


def _toolkit():
    override = os.environ.get("DOOMDRIVE_TOOLKIT")
    cands = [override] if override else TOOLKIT_CANDIDATES
    for c in cands:
        if c and os.path.exists(c):
            return c
    raise SystemExit("game-harness.py not found; tried:\n  " + "\n  ".join(str(c) for c in cands))


spec = importlib.util.spec_from_file_location("harness", _toolkit())
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)
u = ctypes.windll.user32


def find_window():
    """EXACT title match on 'DOOM'. The profile records the title as exactly that, and a
    substring search here would happily return a shell window with DOOM in its title."""
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
    def cb(h, l):
        n = u.GetWindowTextLengthW(h)
        if n and u.IsWindowVisible(h):
            b = ctypes.create_unicode_buffer(n + 1)
            u.GetWindowTextW(h, b, n + 1)
            if b.value.strip().startswith("DOOMx64"):
                found.append((h, b.value))
        return True

    u.EnumWindows(cb, 0)
    if not found:
        raise SystemExit("no window whose title starts with 'DOOMx64'")
    return found[0]


if __name__ == "__main__":
    cmd, rest = sys.argv[1], sys.argv[2:]
    hwnd, title = find_window()

    if cmd == "state":
        r = w.RECT()
        u.GetWindowRect(hwnd, ctypes.byref(r))
        print("title=%r rect=(%d,%d)-(%d,%d) iconic=%d foreground=%s"
              % (title, r.left, r.top, r.right, r.bottom, u.IsIconic(hwnd),
                 u.GetForegroundWindow() == hwnd))
        sys.exit()

    if u.IsIconic(hwnd):
        u.ShowWindow(hwnd, 9)  # SW_RESTORE
        time.sleep(0.5)
    H.focus(hwnd)

    if cmd == "shot":
        H.grab(hwnd).save(rest[0])
        print("saved", rest[0])
    elif cmd == "key":
        rep = int(rest[rest.index("--repeat") + 1]) if "--repeat" in rest else 1
        for _ in range(rep):
            H.tap(rest[0], settle=0.7)
        print("tapped", rest[0], "x", rep)
    else:
        raise SystemExit("unknown command " + cmd)
