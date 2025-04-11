import Console

RED = "\033[91m"
NORMAL = "\033[0m"

def CrashReport(Type:str, Message:str):
    if Message.strip() == "":
        return
    Console.RestoreConsole()
    while Message.endswith("\n"):
        Message = Message[:-1]
    Message = f"{RED}>{NORMAL} " + Message.replace("\n", f"\n{RED}>{NORMAL} ")
    print(f"{RED}{Type}{NORMAL}\n{Message}\n")