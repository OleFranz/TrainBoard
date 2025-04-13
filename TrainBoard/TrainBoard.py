import pickle
import shutil
import numpy
import torch
import time
import os


class TrainBoard:
    def __init__(Self, LogPath:str):
        Self.__LogPath__ = os.path.abspath(LogPath)
        Self.__Graphs__ = []
        Self.__Images__ = []
        Self.__Models__ = []
        os.makedirs(Self.__LogPath__, exist_ok=True)
        for File in os.listdir(Self.__LogPath__):
            if File.startswith("Graph") or File.startswith("Images") or File.startswith("Model"):
                try: os.remove(os.path.join(Self.__LogPath__, File))
                except: pass

    def Clear(Self):
        for Graph in Self.__Graphs__:
            Graph.Clear()
        for Image in Self.__Images__:
            Image.Clear()
        for Model in Self.__Models__:
            Model.Clear()


class Graph:
    def __init__(Self, TrainBoard:TrainBoard, Name:str):
        Self.__TrainBoard__ = TrainBoard
        Self.__TrainBoard__.__Graphs__.append(Self)
        Self.__LogFilePath__ = os.path.join(TrainBoard.__LogPath__, f"Graph{len(Self.__TrainBoard__.__Graphs__)}.pkl")
        Self.__Name__ = Name
        Self.__Graph__ = []
        try: os.remove(Self.__LogFilePath__)
        except: pass

    def Add(Self, Value:float, Epoch:int):
        Self.__Graph__.append((Value, Epoch, time.time()))
        try:
            with open(Self.__LogFilePath__, "wb") as File:
                pickle.dump([Self.__Name__, Self.__Graph__], File)
        except: pass

    def Clear(Self):
        Self.__Graph__.clear()
        try: os.remove(Self.__LogFilePath__)
        except: pass


class Image:
    def __init__(Self, TrainBoard:TrainBoard, Name:str):
        Self.__TrainBoard__ = TrainBoard
        Self.__TrainBoard__.__Images__.append(Self)
        Self.__LogFilePath__ = os.path.join(TrainBoard.__LogPath__, f"Images{len(Self.__TrainBoard__.__Images__)}.pkl")
        Self.__Name__ = Name
        Self.__Images__ = []
        try: os.remove(Self.__LogFilePath__)
        except: pass

    def Add(Self, Image:numpy.ndarray | torch.Tensor, Epoch:int):
        Self.__Images__.append((Image, Epoch, time.time()))
        try:
            with open(Self.__LogFilePath__, "wb") as File:
                pickle.dump([Self.__Name__, Self.__Images__], File)
        except: pass

    def Clear(Self):
        Self.__Images__.clear()
        try: os.remove(Self.__LogFilePath__)
        except: pass


class Model:
    def __init__(Self, TrainBoard:TrainBoard, Name:str, Model:torch.nn.Module):
        Self.__TrainBoard__ = TrainBoard
        Self.__TrainBoard__.__Models__.append(Self)
        Self.__LogFilePath__ = os.path.join(TrainBoard.__LogPath__, f"Model{len(Self.__TrainBoard__.__Models__)}.pkl")
        Self.__Name__ = Name
        try: os.remove(Self.__LogFilePath__)
        except: pass

        Self.TotalParameters = 0
        for Parameter in Model.parameters():
            ParamCount = 1
            for Dim in Parameter.size():
                ParamCount *= int(Dim)
            Self.TotalParameters += ParamCount
        Self.TrainableParameters = sum(Parameter.numel() for Parameter in Model.parameters() if Parameter.requires_grad)
        Self.NonTrainableParameters = Self.TotalParameters - Self.TrainableParameters
        BytesPerParameter = next(Model.parameters()).element_size()
        Self.ModelSize = (Self.TotalParameters * BytesPerParameter) / (1024 ** 2)

        Self.__Model__ = ({"TotalParameters": Self.TotalParameters,
                            "TrainableParameters": Self.TrainableParameters,
                            "NonTrainableParameters": Self.NonTrainableParameters,
                            "ModelSize": Self.ModelSize},
                          time.time())
        try:
            with open(Self.__LogFilePath__, "wb") as File:
                pickle.dump([Self.__Name__, Self.__Model__], File)
        except: pass

    def Clear(Self):
        Self.__Model__ = None
        try: os.remove(Self.__LogFilePath__)
        except: pass