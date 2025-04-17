import variables
import json


def ensure_file(file_path:str):
    try:
        with open(file_path, "r") as f:
            try:
                json.load(f)
            except:
                with open(file_path, "w") as ff:
                    ff.write("{}")
    except:
        with open(file_path, "w") as f:
            f.write("{}")


def get(category:str, name:str, value:any=None):
    try:
        ensure_file(f"{variables.path}settings.json")
        with open(f"{variables.path}settings.json", "r") as f:
            settings = json.load(f)

        if settings[category][name] == None:
            return value

        return settings[category][name]
    except:
        if value != None:
            set(category, name, value)
            return value
        else:
            pass


def set(category:str, name:str, data:any):
    try:
        ensure_file(f"{variables.path}settings.json")
        with open(f"{variables.path}settings.json", "r") as f:
            settings = json.load(f)

        if not category in settings:
            settings[category] = {}
            settings[category][name] = data

        if category in settings:
            settings[category][name] = data

        with open(f"{variables.path}settings.json", "w") as f:
            f.truncate(0)
            json.dump(settings, f, indent=6)
    except:
        pass