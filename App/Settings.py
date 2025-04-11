import Variables
import json

def EnsureFile(FilePath:str):
    try:
        with open(FilePath, "r") as File:
            try:
                json.load(File)
            except:
                with open(FilePath, "w") as FileFile:
                    FileFile.write("{}")
    except:
        with open(FilePath, "w") as File:
            File.write("{}")

def Get(Category:str, Name:str, Value:any=None):
    try:
        EnsureFile(f"{Variables.Path}Settings.json")
        with open(f"{Variables.Path}Settings.json", "r") as File:
            Settings = json.load(File)

        if Settings[Category][Name] == None:
            return Value

        return Settings[Category][Name]
    except:
        if Value != None:
            Set(Category, Name, Value)
            return Value
        else:
            pass

def Set(Category:str, Name:str, Data:any):
    try:
        EnsureFile(f"{Variables.Path}Settings.json")
        with open(f"{Variables.Path}Settings.json", "r") as File:
            Settings = json.load(File)

        if not Category in Settings:
            Settings[Category] = {}
            Settings[Category][Name] = Data

        if Category in Settings:
            Settings[Category][Name] = Data

        with open(f"{Variables.Path}Settings.json", "w") as File:
            File.truncate(0)
            json.dump(Settings, File, indent=6)
    except:
        pass