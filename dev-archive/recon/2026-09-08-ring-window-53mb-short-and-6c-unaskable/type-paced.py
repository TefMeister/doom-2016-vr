"""
type-paced.py - type a string into a foreground game window one scancode at a
time, with a settable gap.

Why: DOOM 2016's console is open (scancode 0x29) but a burst-typed string lands
as a single character - the proxy's `type` sent "getviewpos" and only "g"
appeared at the prompt. A per-character gap is the difference between a console
that "ignores the keyboard" and one that works.

Usage: python type-paced.py <window-substring> <text> [gap_seconds]
       python type-paced.py DOOMx64vk "getviewpos" 0.06
"""
import ctypes
import ctypes.wintypes as w
import sys
import time

u = ctypes.windll.user32
HOLD = 0.045   # key-down duration: DOOM samples the console per frame, and a
               # 12 ms tap was silently coalesced away roughly 1 char in 4.
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP, KEYEVENTF_SCANCODE = 0x0002, 0x0008

# US-layout scancodes for the characters a console command needs.
SC = {
    "a": 0x1E, "b": 0x30, "c": 0x2E, "d": 0x20, "e": 0x12, "f": 0x21, "g": 0x22,
    "h": 0x23, "i": 0x17, "j": 0x24, "k": 0x25, "l": 0x26, "m": 0x32, "n": 0x31,
    "o": 0x18, "p": 0x19, "q": 0x10, "r": 0x13, "s": 0x1F, "t": 0x14, "u": 0x16,
    "v": 0x2F, "w": 0x11, "x": 0x2D, "y": 0x15, "z": 0x2C,
    "1": 0x02, "2": 0x03, "3": 0x04, "4": 0x05, "5": 0x06,
    "6": 0x07, "7": 0x08, "8": 0x09, "9": 0x0A, "0": 0x0B,
    " ": 0x39, "-": 0x0C, "_": 0x0C, ".": 0x34, "/": 0x35,
    "\n": 0x1C, "\b": 0x0E,
}


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", w.WORD), ("wScan", w.WORD), ("dwFlags", w.DWORD),
                ("time", w.DWORD), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]
    _anonymous_ = ("u",)
    _fields_ = [("type", w.DWORD), ("u", _U)]


def find_window(sub):
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
    def cb(h, _):
        n = u.GetWindowTextLengthW(h)
        if n:
            b = ctypes.create_unicode_buffer(n + 1)
            u.GetWindowTextW(h, b, n + 1)
            if sub.lower() in b.value.lower() and u.IsWindowVisible(h):
                found.append((h, b.value))
        return True

    u.EnumWindows(cb, 0)
    if not found:
        raise SystemExit("no window matching %r" % sub)
    return found[0]


def tap(scan, gap):
    for flags in (KEYEVENTF_SCANCODE, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP):
        i = INPUT(type=INPUT_KEYBOARD)
        i.ki = KEYBDINPUT(0, scan, flags, 0, None)
        u.SendInput(1, ctypes.byref(i), ctypes.sizeof(INPUT))
        time.sleep(HOLD)
    time.sleep(gap)


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    hwnd, title = find_window(sys.argv[1])
    text = sys.argv[2]
    gap = float(sys.argv[3]) if len(sys.argv) > 3 else 0.06

    u.SetForegroundWindow(hwnd)
    time.sleep(0.35)
    sent = 0
    for ch in text:
        s = SC.get(ch.lower())
        if s is None:
            print("skipping unmapped character %r" % ch)
            continue
        tap(s, gap)
        sent += 1
    print("typed %d/%d chars into '%s' at %.0f ms/char" % (sent, len(text), title, gap * 1000))


main()
