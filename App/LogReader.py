from CrashReport import CrashReport
import threading
import traceback
import Variables
import Settings
import hashlib
import ImageUI
import pickle
import time
import os


def ClearLogPath():
    Variables.Graphs = {}
    Variables.Images = {}
    Variables.GraphContent = []
    Variables.GraphPosition = 0, 0
    Variables.GraphZoom = 1
    Variables.LogPath = ""
    Settings.Set("Log", "Path", Variables.LogPath)
    ImageUI.SetInput("LogPathInput", Variables.LogPath)


def SetLogPath(Path:str):
    if Path != "":
        Path = Path.replace("'", "").replace('"', "").replace("\\", "/")
        if Path[-1] == "/": Path = Path[:-1]

        if os.path.isdir(Path):
            Variables.LogPath = Path
            LogPathHistory = Settings.Get("Log", "PathHistory", [])
            if Variables.LogPath not in LogPathHistory:
                LogPathHistory.insert(0, Variables.LogPath)
                Variables.LogPathHistory = LogPathHistory
            Settings.Set("Log", "PathHistory", LogPathHistory)
        else:
            ImageUI.Popup(Text="Invalid path",
                          StartX1=Variables.Background.shape[1] / 2 - 100,
                          StartY1=Variables.Background.shape[0],
                          StartX2=Variables.Background.shape[1] / 2 + 100,
                          StartY2=Variables.Background.shape[0] + 40,
                          EndX1=Variables.Background.shape[1] / 2 - 150,
                          EndY1=Variables.Background.shape[0] - 50,
                          EndX2=Variables.Background.shape[1] / 2 + 150,
                          EndY2=Variables.Background.shape[0] - 10,
                          ID="InvalidPathPopup",
                          ShowDuration=3,
                          RoundCorners=10,
                          TextColor=(50, 50, 255))

        Settings.Set("Log", "Path", Variables.LogPath)
        ImageUI.SetInput("LogPathInput", Variables.LogPath)


def LogReaderThread():
    try:
        LastFiles = []
        while Variables.Break == False:
            Start = time.time()
            if Variables.LogPath != "" and os.path.isdir(Variables.LogPath):
                Files = []

                for FileName in os.listdir(Variables.LogPath):
                    if FileName.endswith(".pkl"):
                        Files.append((FileName, hashlib.md5(open(os.path.join(Variables.LogPath, FileName), "rb").read()).hexdigest()))

                FilesSet = set(File[0] for File in Files)
                LastFilesSet = set(File[0] for File in LastFiles)
                
                NewFiles = FilesSet - LastFilesSet
                RemovedFiles = LastFilesSet - FilesSet
                ChangedFiles = set(File[0] for File in Files if File[0] not in NewFiles and File[1] != next((LastFile[1] for LastFile in LastFiles if LastFile[0] == File[0]), None))

                AnyGraphChanged = False
                AnyImageChanged = False
                AnyModelChanged = False

                for FileName in RemovedFiles:
                    if FileName.startswith("Graph"):
                        AnyGraphChanged = True
                        Variables.Graphs.pop(next(GraphName for GraphName in Variables.Graphs.keys() if Variables.Graphs[GraphName]["FileName"] == FileName), None)
                    elif FileName.startswith("Images"):
                        AnyImageChanged = True
                        Variables.Images.pop(next(ImageName for ImageName in Variables.Images.keys() if Variables.Images[ImageName]["FileName"] == FileName), None)
                    elif FileName.startswith("Model"):
                        AnyModelChanged = True
                        Variables.Models.pop(next(ModelName for ModelName in Variables.Models.keys() if Variables.Models[ModelName]["FileName"] == FileName), None)

                for FileName in NewFiles | ChangedFiles:
                    try:
                        with open(os.path.join(Variables.LogPath, FileName), "rb") as File:
                            Data = pickle.load(File)
                            if FileName.startswith("Graph"):
                                AnyGraphChanged = True
                                ShowState = Settings.Get("Graphs", Variables.LogPath + ":" + Data[0], True) if Data[0] not in Variables.Graphs else Variables.Graphs[Data[0]]["Show"]
                                Variables.Graphs[Data[0]] = {"FileName": FileName, "Show": ShowState, "Data": Data[1]}
                                Variables.Graphs = {K: V for K, V in sorted(Variables.Graphs.items(), key=lambda Item: Item[1]["Data"][0][2])}
                            elif FileName.startswith("Images"):
                                AnyImageChanged = True
                                ShowState = Settings.Get("Images", Variables.LogPath + ":" + Data[0], True) if Data[0] not in Variables.Images else Variables.Images[Data[0]]["Show"]
                                Variables.Images[Data[0]] = {"FileName": FileName, "Data": Data[1]}
                                Variables.Images = {K: V for K, V in sorted(Variables.Images.items(), key=lambda Item: Item[1]["Data"][0][2])}
                            elif FileName.startswith("Model"):
                                Variables.Models[Data[0]] = {"FileName": FileName, "Data": Data[1]}
                                Variables.Models = {K: V for K, V in sorted(Variables.Models.items(), key=lambda Item: Item[1]["Data"][1])}
                    except:
                        CrashReport("LogReader - Error while loading log file", traceback.format_exc())

                if AnyGraphChanged:
                    Graphs = []
                    for i, GraphName in enumerate(Variables.Graphs):
                        Graph = Variables.Graphs[GraphName]
                        GraphData = [(Graph["Data"][i][1], Graph["Data"][i][0]) for i in range(len(Graph["Data"]))]
                        Graphs.append((GraphName, Variables.GraphColors[i % len(Variables.GraphColors)], GraphData))
                    Variables.GraphContent = Graphs.copy()

                LastFiles = Files

            elif os.path.exists(Variables.LogPath) == False:
         
                Variables.Graphs = {}
                Variables.Images = {}
                Variables.Models = {}
                Variables.GraphContent = []

            else:

                LastFiles = []

            TimeToSleep = 1 - (time.time() - Start)
            if TimeToSleep > 0:
                time.sleep(TimeToSleep)
    except:
        CrashReport("LogReader - Error in function LogReaderThread", traceback.format_exc())


def StartLogReader():
    try:
        threading.Thread(target=LogReaderThread, daemon=True).start()
    except:
        CrashReport("LogReader - Error in function StartLogReader", traceback.format_exc())