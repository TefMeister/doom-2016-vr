"""test_find_window_decoy.py - prove the harness refuses an impostor window.

WHY THIS EXISTS, and why it is a DECOY rather than an assertion.

On 2026-09-09 `alice_harness.py` matched the user's Chrome tab, because the tab's
title contained "ALICE" and the harness matched titles by substring. The next
call would have typed menu keys into their browser. The board's fix was "match by
process, not title" - and the board also said, correctly:

    "Verify any fix with a decoy window whose title matches - that decoy is what
     exposed it."

So this makes one. It creates a real, visible top-level window titled
`DOOMx64vk` owned by **python.exe**, and requires that:

  1. the OLD behaviour (title only) FINDS it        - the bug is reproduced
  2. the NEW behaviour (title + process) REFUSES it - the fix works
  3. the refusal names the impostor and its process - it is loud, not silent

Check 1 is what stops this being a test that would pass on a broken fix: if the
decoy were not actually matching the title, check 2 would pass for the wrong
reason and prove nothing.

⚠️ THE GAME IS NOT LAUNCHED AND IS NOT REQUIRED. The decoy is a plain Win32
window made by this script. Nothing here reads or writes game memory.

    python test_find_window_decoy.py
"""
import ctypes
import ctypes.wintypes as w
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

u = ctypes.windll.user32
k = ctypes.windll.kernel32

DECOY_TITLE = "DOOMx64vk"          # exactly what find_window() looks for
WS_OVERLAPPEDWINDOW = 0x00CF0000
SW_SHOWNA = 8


def load_doomdrive():
    """Import doomdrive without running its __main__ block."""
    path = os.path.join(HERE, "doomdrive.py")
    spec = importlib.util.spec_from_file_location("doomdrive_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    saved, sys.argv = sys.argv, [path]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = saved
    return mod


def make_decoy():
    """A real visible top-level window titled exactly like DOOM's, owned by us."""
    WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, w.HWND, ctypes.c_uint,
                                 w.WPARAM, w.LPARAM)
    proc = WNDPROC(lambda h, m, wp, lp: u.DefWindowProcW(h, m, wp, lp))

    class WNDCLASS(ctypes.Structure):
        _fields_ = [("style", ctypes.c_uint), ("lpfnWndProc", WNDPROC),
                    ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
                    ("hInstance", w.HINSTANCE), ("hIcon", w.HICON),
                    ("hCursor", w.HANDLE), ("hbrBackground", w.HBRUSH),
                    ("lpszMenuName", w.LPCWSTR), ("lpszClassName", w.LPCWSTR)]

    # ⚠️ argtypes/restype are REQUIRED on 64-bit: without them ctypes assumes
    # int-sized handles and CreateWindowExW's HINSTANCE overflows before the
    # call is even made. The failure looks like a bad argument, not like a
    # missing declaration.
    k.GetModuleHandleW.restype = w.HMODULE
    k.GetModuleHandleW.argtypes = [w.LPCWSTR]
    u.CreateWindowExW.restype = w.HWND
    u.CreateWindowExW.argtypes = [
        w.DWORD, w.LPCWSTR, w.LPCWSTR, w.DWORD,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        w.HWND, w.HMENU, w.HINSTANCE, w.LPVOID]
    u.DefWindowProcW.restype = ctypes.c_long
    u.DefWindowProcW.argtypes = [w.HWND, ctypes.c_uint, w.WPARAM, w.LPARAM]

    wc = WNDCLASS()
    wc.lpfnWndProc = proc
    wc.hInstance = k.GetModuleHandleW(None)
    wc.lpszClassName = "PdDecoyClass"
    if not u.RegisterClassW(ctypes.byref(wc)):
        raise SystemExit("could not register the decoy window class")

    hwnd = u.CreateWindowExW(0, "PdDecoyClass", DECOY_TITLE, WS_OVERLAPPEDWINDOW,
                             10, 10, 220, 120, None, None, wc.hInstance, None)
    if not hwnd:
        raise SystemExit("could not create the decoy window")
    u.ShowWindow(hwnd, SW_SHOWNA)
    u.UpdateWindow(hwnd)
    return hwnd, proc, wc          # keep proc/wc alive or the callback is freed


def main():
    fails = 0
    dd = load_doomdrive()
    hwnd, _proc, _wc = make_decoy()
    try:
        me = os.path.basename(sys.executable).lower()
        print("decoy window 0x%X titled %r, owned by %s" % (hwnd, DECOY_TITLE, me))

        owner = dd.window_process_name(hwnd)
        if owner == me:
            print("  [PASS] the owning process is read correctly (%s)" % owner)
        else:
            print("  [FAIL] owner read as %r, expected %r" % (owner, me)); fails += 1

        # 1. the OLD behaviour must FIND it - otherwise checks 2/3 prove nothing
        try:
            h, t = dd.find_window(require_process=False)
            if h == hwnd:
                print("  [PASS] title-only matching FINDS the impostor "
                      "(the 2026-09-09 bug, reproduced)")
            else:
                print("  [FAIL] title-only matching found 0x%X, not the decoy" % h); fails += 1
        except SystemExit as e:
            print("  [FAIL] title-only matching found nothing: %s" % e); fails += 1

        # 2 + 3. the NEW behaviour must REFUSE it, and say so out loud
        try:
            h, t = dd.find_window()
            print("  [FAIL] process-checked matching ACCEPTED the impostor 0x%X" % h)
            fails += 1
        except SystemExit as e:
            msg = str(e)
            if "NOT owned by" in msg and me in msg:
                print("  [PASS] process-checked matching REFUSES it")
                print("  [PASS] and the refusal names the impostor and its process")
            else:
                print("  [FAIL] refused, but unhelpfully: %s" % msg); fails += 1
    finally:
        u.DestroyWindow(hwnd)

    print("\n%s (%d failure%s)" % ("ALL CHECKS PASSED" if not fails else "*** FAILURES ***",
                                   fails, "" if fails == 1 else "s"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
