import Settings
import numpy
import os

Path = os.path.dirname(os.path.abspath(__file__))
if Path[-1] != "/": Path += "/"

LogPath = ""

Break = False
DynamicFPS = 10

LastMouseInput = 0
LastWindowMove = 0
LastWindowResize = 0

Graphs = {}
Images = {}

WindowName = "TrainBoard"
WindowX = Settings.Get("Window", "X", 100)
WindowY = Settings.Get("Window", "Y", 100)
WindowWidth = Settings.Get("Window", "Width", 960)
WindowHeight = Settings.Get("Window", "Height", 540)

Background = numpy.zeros((WindowHeight, WindowWidth, 3), dtype=numpy.uint8)
Background[:] = (28, 28, 28)

ConsoleName = None
ConsoleHWND = None

GraphContent = []
GraphPosition = 0, 0
GraphZoom = 1
GraphUIPositionX1 = 250
GraphUIPositionY1 = 50
GraphUIPositionX2 = WindowWidth - 5
GraphUIPositionY2 = WindowHeight - 5
Graph = numpy.zeros((GraphUIPositionY2 - GraphUIPositionY1, GraphUIPositionX2 - GraphUIPositionX1, 3), dtype=numpy.uint8)
Graph[:] = (25, 25, 25)