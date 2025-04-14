from CrashReport import CrashReport
import threading
import traceback
import Variables
import Settings
import hashlib
import ImageUI
import pickle
import numpy
import torch
import time
import cv2
import os


LastFiles = []


def ClearLogPath():
    global LastFiles
    LastFiles = []
    Variables.Graphs = {}
    Variables.Images = {}
    Variables.GraphContent = []
    Variables.GraphPosition = 0, 0
    Variables.GraphZoom = 1
    Variables.ImageContent = []
    Variables.SelectedImage = ""
    Variables.SelectedImageEpoch = -1
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
        global LastFiles
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
                        Variables.ImageContent.pop(Variables.ImageContent.index(next((ImageData for ImageData in Variables.ImageContent if ImageData[0] not in list(Variables.Images.keys())), None)))
                        Variables.SelectedImage = ""
                    elif FileName.startswith("Model"):
                        AnyModelChanged = True
                        Variables.Models.pop(next(ModelName for ModelName in Variables.Models.keys() if Variables.Models[ModelName]["FileName"] == FileName), None)

                for FileName in NewFiles | ChangedFiles:
                    try:
                        with open(os.path.join(Variables.LogPath, FileName), "rb") as File:
                            Data = pickle.load(File)
                            if FileName.startswith("Graph"):
                                AnyGraphChanged = True
                                ShowState = Settings.Get("Graphs", Variables.LogPath + ":Show:" + Data[0], True) if Data[0] not in Variables.Graphs else Variables.Graphs[Data[0]]["Show"]
                                Variables.Graphs[Data[0]] = {"FileName": FileName, "Show": ShowState, "Data": Data[1]}
                                Variables.Graphs = {K: V for K, V in sorted(Variables.Graphs.items(), key=lambda Item: Item[1]["Data"][0][2])}
                            elif FileName.startswith("Images"):
                                AnyImageChanged = True
                                StrechState = Settings.Get("Images", Variables.LogPath + ":SwapRGBBGR:" + Data[0], False) if Data[0] not in Variables.Images else Variables.Images[Data[0]]["SwapRGBBGR"]
                                Variables.Images[Data[0]] = {"FileName": FileName, "SwapRGBBGR": StrechState, "Data": Data[1]}
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

                if AnyImageChanged:
                    if Variables.SelectedImage == "":
                        Name = Settings.Get("Images", Variables.LogPath + ":Selected:", "")
                        BeforeSelectedImage = Variables.SelectedImage
                        Variables.SelectedImage = (Name if Name in Variables.Images else next(iter(Variables.Images))) if Variables.Images else ""
                        if Variables.SelectedImage != BeforeSelectedImage:
                            Settings.Set("Images", Variables.LogPath + ":Selected:", Variables.SelectedImage)
                            ImageUI.SetDropdown(f"ImageDropdown{list(Variables.Images.keys())}",
                                                list(sorted(Variables.Images.keys(), key=lambda ImageName: Variables.Images[ImageName]["Data"][0][2])),
                                                Variables.SelectedImage)
                    if Variables.SelectedImageEpoch == -1:
                        Variables.SelectedImageEpoch = max(D[1] for D in Variables.Images[Variables.SelectedImage]["Data"])
                        ImageUI.SetInput(f"ImageInput{Variables.SelectedImage}", str(Variables.SelectedImageEpoch))
                    Images = []
                    for ImageName in Variables.Images:
                        Image = Variables.Images[ImageName]
                        SwapRGBBGR = Image["SwapRGBBGR"]
                        ImageTemp = []
                        for i, (Img, Epoch, Time) in enumerate(Image["Data"]):
                            if Img.dtype == numpy.uint8:
                                if Img.shape[2] == 1:
                                    Img = cv2.cvtColor(Img, cv2.COLOR_GRAY2BGR)
                            elif Img.dtype == numpy.float32:
                                Img = (Img * 255).astype(numpy.uint8)
                                if Img.shape[2] == 1:
                                    Img = cv2.cvtColor(Img, cv2.COLOR_GRAY2BGR)
                            elif Img.dtype == numpy.float64:
                                Img = (Img * 255).astype(numpy.uint8)
                                if Img.shape[2] == 1:
                                    Img = cv2.cvtColor(Img, cv2.COLOR_GRAY2BGR)
                            elif Img.dtype != torch.float32:
                                Img = Img.to(torch.float32).numpy().transpose(1, 2, 0)
                                Img = numpy.clip(Img, 0, 1)
                                Img = (Img * 255).astype(numpy.uint8)
                            elif Img.dtype == torch.float32:
                                Img = Img.numpy().transpose(1, 2, 0)
                                Img = numpy.clip(Img, 0, 1)
                                Img = (Img * 255).astype(numpy.uint8)
                            ImageTemp.append((Img, Epoch, Time))
                        Image["Data"] = ImageTemp.copy()
                        ImageData = [(Image["Data"][i][0], Image["Data"][i][1]) for i in range(len(Image["Data"]))]
                        Images.append((ImageName, ImageData))
                    if Variables.ImageContent == [] or Variables.ImageContent[-1][1][-1][1] == Variables.SelectedImageEpoch:
                        Variables.SelectedImageEpoch = Images[-1][1][-1][1]
                        ImageUI.SetInput(f"ImageInput{Variables.SelectedImage}", str(Variables.SelectedImageEpoch))
                    Variables.ImageContent = Images

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