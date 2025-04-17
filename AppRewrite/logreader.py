from crashreport import crash_report
import threading
import traceback
import variables
import settings
import hashlib
import ImageUI
import pickle
import graph
import model
import time
import os


last_files = []
registered_files = {}

unsync_graphs = {}
unsync_models = {}


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
        global unsync_graphs
        global unsync_models
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
                changed_files = set(f[0] for f in files if f[0] not in new_files and f[1] != next((last_f[1] for last_f in last_files if last_f[0] == f[0]), None))

                unsync_temp_graphs = graph.graphs.copy()
                unsync_temp_models = model.models.copy()

                for file in removed_files:
                    try:
                        if file.startswith("graph"):
                            name = registered_files[file]["name"]
                            epoch = registered_files[file]["epoch"]
                            if name in unsync_temp_graphs:
                                if epoch in unsync_temp_graphs[name]["data"]:
                                    del unsync_temp_graphs[name]["data"][epoch]
                                if len(unsync_temp_graphs[name]["data"]) == 0:
                                    del unsync_temp_graphs[name]
                        elif file.startswith("images"):
                            ...
                        elif file.startswith("model"):
                            name = registered_files[file]["name"]
                            if name in unsync_temp_models:
                                del unsync_temp_models[name]
                    except:
                        crash_report("LogReader - Error while removing log items", traceback.format_exc())

                for file in new_files or changed_files:
                    try:
                        with open(os.path.join(variables.log_path, file), "rb") as f:
                            data = pickle.load(f)
                            if file.startswith("graph"):
                                name, value, epoch, timestamp = data["name"], data["value"], data["epoch"], data["time"] # read the data from the log file
                                registered_files[file] = {"name": name, "epoch": epoch} # register so we can delete the datapoint if the file is removed
                                if name not in unsync_temp_graphs:
                                    unsync_temp_graphs[name] = {"data": {},
                                                          "color": (0, 0, 0),
                                                          "show": settings.get("graph", f"{variables.log_path}:{name}:show", True)}
                                unsync_temp_graphs[name]["data"][epoch] = (value, timestamp)
                                unsync_temp_graphs[name]["data"] = dict(sorted(unsync_temp_graphs[name]["data"].items(), key=lambda item: item[1][1])) # sort the epochs by lowest time first
                                unsync_temp_graphs = dict(sorted(unsync_temp_graphs.items(), key=lambda item: next(iter(item[1]["data"].values()))[1])) # sort the graphs by the graph with the first datapoint first
                            elif file.startswith("images"):
                                ...
                            elif file.startswith("model"):
                                name = data["name"]
                                total_parameters = data["total_parameters"]
                                trainable_parameters = data["trainable_parameters"]
                                non_trainable_parameters = data["non_trainable_parameters"]
                                model_size = data["model_size"]
                                timestamp = data["time"]
                                registered_files[file] = {"name": name}
                                unsync_temp_models[name] = {"total_parameters": total_parameters,
                                                          "trainable_parameters": trainable_parameters,
                                                          "non_trainable_parameters": non_trainable_parameters,
                                                          "model_size": model_size,
                                                          "time": timestamp}
                                unsync_temp_models = dict(sorted(unsync_temp_models.items(), key=lambda item: item[1]["time"]))
                    except:
                        crash_report("LogReader - Error while loading log files", traceback.format_exc())

                for i, graph_name in enumerate(unsync_temp_graphs):
                    if unsync_temp_graphs[graph_name]["color"] == (0, 0, 0):
                        unsync_temp_graphs[graph_name]["color"] = graph.graph_colors[i % len(graph.graph_colors)]

                unsync_graphs = unsync_temp_graphs.copy()
                unsync_models = unsync_temp_models.copy()

                last_files = files

            elif os.path.exists(variables.log_path) == False:
         
                graph.graphs = {}

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


def sync_data():
    graph.graphs = unsync_graphs
    model.models = unsync_models