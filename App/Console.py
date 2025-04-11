import win32gui, win32con, win32console
import traceback
import Variables
import ctypes

RED = "\033[91m"
NORMAL = "\033[0m"

def RestoreConsole():
    try:
        if Variables.ConsoleHWND != None and Variables.ConsoleName != None:
            win32gui.ShowWindow(Variables.ConsoleHWND, win32con.SW_RESTORE)
        else:
            Variables.ConsoleName = win32console.GetConsoleTitle()
            Variables.ConsoleHWND = win32gui.FindWindow(None, str(Variables.ConsoleName))
            win32gui.ShowWindow(Variables.ConsoleHWND, win32con.SW_RESTORE)
    except:
        Type = "\nConsole - Restore Error."
        Message = str(traceback.format_exc())
        while Message.endswith("\n"):
            Message = Message[:-1]
        Message = f"{RED}>{NORMAL} " + Message.replace("\n", f"\n{RED}>{NORMAL} ")
        print(f"{RED}{Type}{NORMAL}\n{Message}\n")

def HideConsole():
    try:
        if Variables.ConsoleHWND != None and Variables.ConsoleName != None:
            win32gui.ShowWindow(Variables.ConsoleHWND, win32con.SW_HIDE)
        else:
            Variables.ConsoleName = win32console.GetConsoleTitle()
            Variables.ConsoleHWND = win32gui.FindWindow(None, str(Variables.ConsoleName))
            win32gui.ShowWindow(Variables.ConsoleHWND, win32con.SW_HIDE)
    except:
        Type = "\nConsole - Hide Error."
        Message = str(traceback.format_exc())
        while Message.endswith("\n"):
            Message = Message[:-1]
        Message = f"{RED}>{NORMAL} " + Message.replace("\n", f"\n{RED}>{NORMAL} ")
        print(f"{RED}{Type}{NORMAL}\n{Message}\n")

def CloseConsole():
    try:
        if Variables.ConsoleHWND != None and Variables.ConsoleName != None:
            ctypes.windll.user32.PostMessageW(Variables.ConsoleHWND, 0x10, 0, 0)
        else:
            Variables.ConsoleName = win32console.GetConsoleTitle()
            Variables.ConsoleHWND = win32gui.FindWindow(None, str(Variables.ConsoleName))
            ctypes.windll.user32.PostMessageW(Variables.ConsoleHWND, 0x10, 0, 0)
    except:
        Type = "\nConsole - Close Error."
        Message = str(traceback.format_exc())
        while Message.endswith("\n"):
            Message = Message[:-1]
        Message = f"{RED}>{NORMAL} " + Message.replace("\n", f"\n{RED}>{NORMAL} ")
        print(f"{RED}{Type}{NORMAL}\n{Message}\n")