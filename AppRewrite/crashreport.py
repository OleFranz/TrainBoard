import console


RED = "\033[91m"
NORMAL = "\033[0m"


def crash_report(type:str, message:str):
    if message.strip() == "":
        return
    console.restore_console()
    while message.endswith("\n"):
        message = message[:-1]
    message = f"{RED}>{NORMAL} " + message.replace("\n", f"\n{RED}>{NORMAL} ")
    print(f"{RED}{type}{NORMAL}\n{message}\n")