import win32gui, win32con, win32console
import traceback
import ctypes


RED = "\033[91m"
NORMAL = "\033[0m"

console_hwnd = None
console_name = None


def restore_console():
    global console_hwnd, console_name
    try:
        if console_hwnd != None and console_name != None:
            win32gui.ShowWindow(console_hwnd, win32con.SW_RESTORE)
        else:
            console_name = win32console.GetConsoleTitle()
            console_hwnd = win32gui.FindWindow(None, str(console_name))
            win32gui.ShowWindow(console_hwnd, win32con.SW_RESTORE)
    except:
        type = "\nConsole - Restore Error."
        message = str(traceback.format_exc())
        while message.endswith("\n"):
            message = message[:-1]
        message = f"{RED}>{NORMAL} " + message.replace("\n", f"\n{RED}>{NORMAL} ")
        print(f"{RED}{type}{NORMAL}\n{message}\n")


def hide_console():
    global console_hwnd, console_name
    try:
        if console_hwnd != None and console_name != None:
            win32gui.ShowWindow(console_hwnd, win32con.SW_HIDE)
        else:
            console_name = win32console.GetConsoleTitle()
            console_hwnd = win32gui.FindWindow(None, str(console_name))
            win32gui.ShowWindow(console_hwnd, win32con.SW_HIDE)
    except:
        type = "\nConsole - Hide Error."
        message = str(traceback.format_exc())
        while message.endswith("\n"):
            message = message[:-1]
        message = f"{RED}>{NORMAL} " + message.replace("\n", f"\n{RED}>{NORMAL} ")
        print(f"{RED}{type}{NORMAL}\n{message}\n")


def close_console():
    global console_hwnd, console_name
    try:
        if console_hwnd != None and console_name != None:
            ctypes.windll.user32.PostMessageW(console_hwnd, 0x10, 0, 0)
        else:
            console_name = win32console.GetConsoleTitle()
            console_hwnd = win32gui.FindWindow(None, str(console_name))
            ctypes.windll.user32.PostMessageW(console_hwnd, 0x10, 0, 0)
    except:
        type = "\nConsole - Close Error."
        message = str(traceback.format_exc())
        while message.endswith("\n"):
            message = message[:-1]
        message = f"{RED}>{NORMAL} " + message.replace("\n", f"\n{RED}>{NORMAL} ")
        print(f"{RED}{type}{NORMAL}\n{message}\n")