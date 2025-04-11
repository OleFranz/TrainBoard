import SimpleWindow
import LogReader
import Variables
import Settings
import Console
import ImageUI
import Graph
import Mouse
import numpy
import time


SimpleWindow.Initialize(Name=Variables.WindowName,
                        Size=(Variables.WindowWidth, Variables.WindowHeight),
                        Position=(Variables.WindowX, Variables.WindowY),
                        TitleBarColor=Variables.Background[0][0],
                        Resizable=True,
                        TopMost=False,
                        Foreground=True,
                        Minimized=False,
                        Undestroyable=False,
                        Icon="",
                        NoWarnings=False)

LogReader.StartLogReader()
Console.HideConsole()
Mouse.Run()

while Variables.Break == False:
    Start = time.perf_counter()

    WindowSize = SimpleWindow.GetSize(Name=Variables.WindowName)
    WindowPosition = SimpleWindow.GetPosition(Name=Variables.WindowName)

    if WindowSize[0] != Variables.WindowWidth or WindowSize[1] != Variables.WindowHeight:
        Variables.LastWindowResize = time.time()
        Variables.WindowWidth = WindowSize[0]
        Variables.WindowHeight = WindowSize[1]
        Variables.Background = numpy.zeros((Variables.WindowHeight, Variables.WindowWidth, 3), dtype=numpy.uint8)
        Variables.Background[:] = (28, 28, 28)
        Settings.Set("Window", "Width", Variables.WindowWidth)
        Settings.Set("Window", "Height", Variables.WindowHeight)

    if WindowPosition[0] != Variables.WindowX or WindowPosition[1] != Variables.WindowY:
        Variables.LastWindowMove = time.time()
        Variables.WindowX = WindowPosition[0]
        Variables.WindowY = WindowPosition[1]
        Settings.Set("Window", "X", Variables.WindowX)
        Settings.Set("Window", "Y", Variables.WindowY)

    Graph.Update()

    ImageUI.Image(Image=Graph.Frame,
                  X1=Variables.GraphUIPositionX1,
                  Y1=Variables.GraphUIPositionY1,
                  X2=Variables.GraphUIPositionX2,
                  Y2=Variables.GraphUIPositionY2,
                  ID="Graph",
                  RoundCorners=20)

    WindowHandle = SimpleWindow.GetHandle(Name=Variables.WindowName)
    Frame = ImageUI.Update(WindowHWND=WindowHandle, Frame=Variables.Background)

    SimpleWindow.Show(Name=Variables.WindowName, Frame=Frame)
    if SimpleWindow.GetOpen(Name=Variables.WindowName) != True:
        Variables.Break = True

    Time = time.time()
    if Time - Variables.LastMouseInput < 3 or Time - Variables.LastWindowResize < 3 or Time - Variables.LastWindowMove < 3:
        Variables.DynamicFPS = 60
    else:
        Variables.DynamicFPS = 10

    TimeToSleep = 1/Variables.DynamicFPS - (time.perf_counter() - Start)
    if TimeToSleep > 0:
        time.sleep(TimeToSleep)