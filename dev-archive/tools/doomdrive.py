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


def window_process_name(hwnd):
    """The lower-cased exe name that owns `hwnd`, or None.

    QueryFullProcessImageNameW rather than GetModuleFileNameEx: it needs only
    PROCESS_QUERY_LIMITED_INFORMATION, which a normal user holds for a normal
    process, where the module-based calls need PROCESS_VM_READ and fail."""
    k = ctypes.windll.kernel32
    pid = w.DWORD(0)
    u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return None
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    h = k.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not h:
        return None
    try:
        size = w.DWORD(32768)
        buf = ctypes.create_unicode_buffer(size.value)
        if not k.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
            return None
        return buf.value.rsplit("\\", 1)[-1].lower()
    finally:
        k.CloseHandle(h)


def find_window(require_process=True):
    """Find DOOM's window by TITLE **and** by the process that owns it.

    ⚠️ WHY THE PROCESS CHECK EXISTS, and it is not hypothetical. On 2026-09-09
    `alice_harness.py` matched the user's CHROME TAB, because the tab's title
    contained "ALICE" and that harness matches titles by substring. The next call
    would have typed menu keys into their browser. A title is USER DATA - a
    browser tab, an editor, a chat window, this very session's terminal can each
    contain a game's name - so a title match alone can never establish that a
    window belongs to the game.

    The owning process CAN establish it: a window whose process image is
    `doomx64*.exe` is DOOM's, whatever its title says.

    The title prefix is kept as well, because DOOM makes more than one window and
    the title is what separates the render window from its splash. Title narrows;
    process VERIFIES. Neither alone is enough.

    `require_process=False` exists only so the self-test can demonstrate the old
    title-only behaviour. It is not a way to make a failing match succeed."""
    found = []
    rejected = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
    def cb(h, l):
        n = u.GetWindowTextLengthW(h)
        if n and u.IsWindowVisible(h):
            b = ctypes.create_unicode_buffer(n + 1)
            u.GetWindowTextW(h, b, n + 1)
            if b.value.strip().startswith("DOOMx64"):
                proc = window_process_name(h)
                if not require_process or (proc and proc.startswith("doomx64")):
                    found.append((h, b.value, proc))
                else:
                    rejected.append((h, b.value, proc))
        return True

    u.EnumWindows(cb, 0)
    if not found:
        if rejected:
            # Name what was refused and why. A silent "not found" would read
            # identically to "the game is not running", and the entire point is
            # that an impostor window is LOUD rather than invisible.
            lines = "\n".join("    %r  owned by %s" % (t, p or "<unknown>")
                              for _, t, p in rejected)
            raise SystemExit(
                "no DOOM window. %d window(s) matched the title but are NOT owned "
                "by doomx64*.exe, so they were refused:\n%s"
                % (len(rejected), lines))
        raise SystemExit("no window whose title starts with 'DOOMx64'")
    return found[0][0], found[0][1]


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
