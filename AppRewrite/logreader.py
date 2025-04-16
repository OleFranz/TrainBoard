from crashreport import crash_report
import threading
import traceback
import variables
import settings
import hashlib
import ImageUI
import pickle
import graph
import numpy
import torch
import time
import cv2
import os


last_files = []
registered_files = {}


def clear_log_path():
    global last_files
    last_files = []
    variables.graphs = {}
    variables.images = {}
    variables.models = {}
    graph.graph_position = 0, 0
    graph.graph_zoom = 1
    variables.log_path = ""
    settings.set("log", "path", variables.log_path)
    ImageUI.SetInput("log_path_input", variables.log_path)


def set_log_path(path:str):
    if path != "":
        path = path.replace("'", "").replace('"', "").replace("\\", "/")
        if path[-1] == "/": path = path[:-1]

        if os.path.isdir(path):
            variables.log_path = path
            log_path_history = settings.get("log", "path_history", [])
            if variables.log_path not in log_path_history:
                log_path_history.insert(0, variables.log_path)
                variables.log_path_history = log_path_history
            settings.set("log", "path_history", log_path_history)
        else:
            ImageUI.Popup(Text="Invalid path",
                          StartX1=variables.background.shape[1] / 2 - 100,
                          StartY1=variables.background.shape[0],
                          StartX2=variables.background.shape[1] / 2 + 100,
                          StartY2=variables.background.shape[0] + 40,
                          EndX1=variables.background.shape[1] / 2 - 150,
                          EndY1=variables.background.shape[0] - 50,
                          EndX2=variables.background.shape[1] / 2 + 150,
                          EndY2=variables.background.shape[0] - 10,
                          ID="InvalidPathPopup",
                          ShowDuration=3,
                          RoundCorners=10,
                          TextColor=(50, 50, 255))

        settings.set("log", "path", variables.log_path)
        ImageUI.SetInput("log_path_input", variables.log_path)


def log_reader_thread():
    try:
        global last_files
        while variables.stop == False:
            start = time.time()
            if variables.log_path != "" and os.path.isdir(variables.log_path):
                files = []

                for file in os.listdir(variables.log_path):
                    if file.endswith(".pkl"):
                        try:
                            files.append((file, hashlib.md5(open(os.path.join(variables.log_path, file), "rb").read()).hexdigest()))
                        except:
                            crash_report("LogReader - Error while reading log hashes", traceback.format_exc())

                files_set = set(f[0] for f in files)
                last_files_set = set(f[0] for f in last_files)

                new_files = files_set - last_files_set
                removed_files = last_files_set - files_set

                for file in removed_files:
                    try:
                        if file.startswith("graph"):
                            name = registered_files[file]["name"]
                            epoch = registered_files[file]["epoch"]
                            del variables.graphs[name][epoch]
                        elif file.startswith("images"):
                            ...
                        elif file.startswith("model"):
                            ...
                    except:
                        crash_report("LogReader - Error while removing log items", traceback.format_exc())

                for file in new_files:
                    try:
                        with open(os.path.join(variables.log_path, file), "rb") as f:
                            data = pickle.load(f)
                            if file.startswith("graph"):
                                name = data["name"]
                                value = data["value"]
                                epoch = data["epoch"]
                                registered_files[file] = {"name": name, "epoch": epoch}
                                if name not in variables.graphs:
                                    variables.graphs[name] = {}
                                variables.graphs[name][epoch] = value
                            elif file.startswith("images"):
                                ...
                            elif file.startswith("model"):
                                ...
                    except:
                        crash_report("LogReader - Error while loading log files", traceback.format_exc())

                last_files = files

            elif os.path.exists(variables.log_path) == False:
         
                variables.graphs = {}
                variables.images = {}
                variables.models = {}

            else:

                last_files = []

            time_to_sleep = 1 - (time.time() - start)
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)
    except:
        crash_report("LogReader - Error in function log_reader_thread", traceback.format_exc())


def start_log_reader():
    try:
        threading.Thread(target=log_reader_thread, daemon=True).start()
    except:
        crash_report("LogReader - Error in function start_log_reader", traceback.format_exc())