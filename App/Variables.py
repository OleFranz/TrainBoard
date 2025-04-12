import Settings
import numpy
import os

Path = os.path.dirname(os.path.abspath(__file__))
if Path[-1] != "/": Path += "/"

LogPath = Settings.Get("Log", "Path", "")
LogPathHistory = Settings.Get("Log", "PathHistory", [])

Break = False
DynamicFPS = 10

LastMouseMove = 0
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

GraphColors = [
    (203, 181, 18),
    (146, 37, 229),
    (0, 171, 249),
    (230, 52, 147),
    (66, 179, 124),
    (10, 113, 232),
    (163, 152, 142)
]

GraphContent = []
GraphPosition = 0, 0
GraphZoom = 1
GraphUIPositionX1 = 200
GraphUIPositionY1 = 50
GraphUIPositionX2 = WindowWidth - 6
GraphUIPositionY2 = WindowHeight - 6
Graph = numpy.zeros((GraphUIPositionY2 - GraphUIPositionY1, GraphUIPositionX2 - GraphUIPositionX1, 3), dtype=numpy.uint8)
Graph[:] = (25, 25, 25)