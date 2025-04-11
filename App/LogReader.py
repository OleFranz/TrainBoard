from CrashReport import CrashReport
import threading
import traceback
import Variables
import Settings
import hashlib
import pickle
import time
import os


def LogReaderThread():
    try:
        LastFiles = []
        while Variables.Break == False:
            Start = time.time()
            if Variables.LogPath != "":
                Files = []

                for FileName in os.listdir(Variables.LogPath):
                    if FileName.endswith(".pkl"):
                        Files.append((FileName, hashlib.md5(open(Variables.LogPath + FileName, "rb").read()).hexdigest()))

                FilesSet = set(File[0] for File in Files)
                LastFilesSet = set(File[0] for File in LastFiles)
                
                NewFiles = FilesSet - LastFilesSet
                RemovedFiles = LastFilesSet - FilesSet
                ChangedFiles = set(File[0] for File in Files if File[0] not in NewFiles and File[1] != next((LastFile[1] for LastFile in LastFiles if LastFile[0] == File[0]), None))

                AnyGraphChanged = False
                AnyImageChanged = False

                for FileName in RemovedFiles:
                    if FileName.startswith("Graph"):
                        AnyGraphChanged = True
                        Variables.Graphs.pop(next(GraphName for GraphName in Variables.Graphs.keys() if Variables.Graphs[GraphName]["FileName"] == FileName), None)
                    elif FileName.startswith("Images"):
                        AnyImageChanged = True
                        Variables.Images.pop(next(ImageName for ImageName in Variables.Images.keys() if Variables.Images[ImageName]["FileName"] == FileName), None)

                for FileName in NewFiles | ChangedFiles:
                    try:
                        with open(os.path.join(Variables.LogPath, FileName), "rb") as File:
                            Data = pickle.load(File)
                            if FileName.startswith("Graph"):
                                AnyGraphChanged = True
                                ShowState = Settings.Get("Graphs", Data[0], True) if Data[0] not in Variables.Graphs else Variables.Graphs[Data[0]]["Show"]
                                Variables.Graphs[Data[0]] = {"FileName": FileName, "Show": ShowState, "Data": Data[1]}
                            elif FileName.startswith("Images"):
                                AnyImageChanged = True
                                ShowState = Settings.Get("Images", Data[0], True) if Data[0] not in Variables.Images else Variables.Images[Data[0]]["Show"]
                                Variables.Images[Data[0]] = {"FileName": FileName, "Show": ShowState, "Data": Data[1]}
                    except:
                        CrashReport("LogReader - Error while loading log file", traceback.format_exc())

                if AnyGraphChanged:
                    Graphs = []
                    for Graph in Variables.Graphs:
                        GraphName = Graph
                        Graph = Variables.Graphs[Graph]
                        GraphData = [(i, Graph["Data"][i][0]) for i in range(len(Graph["Data"]))]
                        ShowGraph = Graph["Show"]
                        if ShowGraph == True:
                            Graphs.append((GraphName, GraphData))
                    Variables.GraphContent = Graphs.copy()

                LastFiles = Files

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