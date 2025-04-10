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
        try: shutil.rmtree(Self.__LogPath__)
        except: pass
        try: os.makedirs(Self.__LogPath__, exist_ok=True)
        except: pass

    def Clear(Self):
        for Graph in Self.__Graphs__:
            Graph.Clear()
        for Image in Self.__Images__:
            Image.Clear()
        try: shutil.rmtree(Self.__LogPath__)
        except: pass


class Graph:
    def __init__(Self, TrainBoard:TrainBoard, Name:str):
        Self.__TrainBoard__ = TrainBoard
        Self.__TrainBoard__.__Graphs__.append(Self)
        Self.__LogFilePath__ = os.path.join(TrainBoard.__LogPath__, f"Graph{len(Self.__TrainBoard__.__Graphs__)}.pkl")
        Self.__Name__ = Name
        Self.__Graph__ = []
        try: os.remove(Self.__LogFilePath__)
        except: pass

    def Add(Self, Value:float):
        Self.__Graph__.append((Value, time.time()))
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

    def Add(Self, Value:numpy.ndarray | torch.Tensor):
        Self.__Images__.append((Value, time.time()))
        try:
            with open(Self.__LogFilePath__, "wb") as File:
                pickle.dump([Self.__Name__, Self.__Images__], File)
        except: pass

    def Clear(Self):
        Self.__Images__.clear()
        try: os.remove(Self.__LogFilePath__)
        except: pass