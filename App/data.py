import threading
import variables
import hashlib
import pickle
import torch
import numpy
import time
import os


def LogReaderThread():
    LastFiles = []
    while True:
        Start = time.time()
        if variables.LogPath != "":
            Files = []

            for FileName in os.listdir(variables.LogPath):
                Files.append((FileName, hashlib.md5(open(variables.LogPath + FileName, "rb").read()).hexdigest()))

            FilesSet = set(File[0] for File in Files)
            LastFilesSet = set(File[0] for File in LastFiles)
            
            NewFiles = FilesSet - LastFilesSet
            RemovedFiles = LastFilesSet - FilesSet
            ChangedFiles = set(File[0] for File in Files if File[0] not in NewFiles and File[1] != next((LastFile[1] for LastFile in LastFiles if LastFile[0] == File[0]), None))

            for FileName in RemovedFiles:
                if FileName.startswith("Graph"):
                    variables.Graphs.pop(next(GraphName for GraphName in variables.Graphs.keys() if variables.Graphs[GraphName][0] == FileName), None)
                elif FileName.startswith("Images"):
                    variables.Images.pop(next(ImageName for ImageName in variables.Images.keys() if variables.Images[ImageName][0] == FileName), None)

            for FileName in NewFiles | ChangedFiles:
                try:
                    with open(os.path.join(variables.LogPath, FileName), "rb") as File:
                        Data = pickle.load(File)
                        if FileName.startswith("Graph"):
                            variables.Graphs[Data[0]] = (FileName, Data[1])
                        elif FileName.startswith("Images"):
                            variables.Images[Data[0]] = (FileName, Data[1])
                except:
                    pass

            print(variables.Graphs, variables.Images)

            LastFiles = Files

        TimeToSleep = 1 - (time.time() - Start)
        if TimeToSleep > 0:
            time.sleep(TimeToSleep)


def StartLogReader():
    threading.Thread(target=LogReaderThread, daemon=True).start()