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
import os

SimpleWindow.Initialize(Name=Variables.WindowName,
                        Size=(Variables.WindowWidth, Variables.WindowHeight),
                        Position=(Variables.WindowX, Variables.WindowY),
                        TitleBarColor=Variables.Background[0][0],
                        Resizable=True,
                        TopMost=False,
                        Foreground=True,
                        Minimized=False,
                        Undestroyable=False,
                        Icon=f"{Variables.Path}Icon.ico",
                        NoWarnings=False)

LogReader.StartLogReader()
Console.HideConsole()
Mouse.Run()

LastLogPath = Settings.Get("Log", "Path", "")
if os.path.isdir(LastLogPath) and LastLogPath != "":
    Variables.LogPath = LastLogPath

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


    if Variables.LogPath != "":
        Graph.Update()

        ImageUI.Image(Image=Graph.Frame,
                    X1=Variables.GraphUIPositionX1,
                    Y1=Variables.GraphUIPositionY1,
                    X2=Variables.GraphUIPositionX2,
                    Y2=Variables.GraphUIPositionY2,
                    ID="GraphImage",
                    RoundCorners=20)

        ImageUI.Button(Text="Graphs",
                       X1=Variables.GraphUIPositionX1,
                       Y1=5,
                       X2=(Variables.GraphUIPositionX1 + Variables.GraphUIPositionX2) / 2 - 2.5,
                       Y2=Variables.GraphUIPositionY1 - 5,
                       ID="GraphsTab",
                       RoundCorners=10)

        ImageUI.Button(Text="Images",
                       X1=(Variables.GraphUIPositionX1 + Variables.GraphUIPositionX2) / 2 + 2.5,
                       Y1=5,
                       X2=Variables.GraphUIPositionX2,
                       Y2=Variables.GraphUIPositionY1 - 5,
                       ID="GraphsTab",
                       RoundCorners=10)

    else:

        ImageUI.Label(Text="TrainBoard",
                      X1=0,
                      Y1=Variables.Background.shape[0] / 2 - 30,
                      X2=Variables.Background.shape[1] - 1,
                      Y2=Variables.Background.shape[0] / 2 - 70,
                      Align="Center",
                      ID="LogPathLabel",
                      FontSize=25,
                      FontType="Candarab")

        ImageUI.Input(X1=Variables.Background.shape[1] / 2 - 250,
                      Y1=Variables.Background.shape[0] / 2 - 20,
                      X2=Variables.Background.shape[1] / 2 + 250,
                      Y2=Variables.Background.shape[0] / 2 + 20,
                      Placeholder="Enter the absolute path to the log folder",
                      TextAlign="Center",
                      ID="LogPathInput",
                      RoundCorners=10,
                      OnChange=lambda Text: None if Text == "" else {
                          setattr(Variables, "LogPath", Text.replace("'", "").replace('"', "").replace("\\", "/") + ("/" if Text[-1] != "/" else ""))
                          if os.path.isdir(Text.replace("'", "").replace('"', "")) else setattr(Variables, "LogPath", ""),
                          ImageUI.SetInput("LogPathInput", Variables.LogPath),
                          Settings.Set("Log", "Path", Variables.LogPath)
                          if os.path.isdir(Variables.LogPath) else
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
                      })


    WindowHandle = SimpleWindow.GetHandle(Name=Variables.WindowName)
    Frame = ImageUI.Update(WindowHWND=WindowHandle, Frame=Variables.Background)

    SimpleWindow.Show(Name=Variables.WindowName, Frame=Frame)
    if SimpleWindow.GetOpen(Name=Variables.WindowName) != True:
        Console.RestoreConsole()
        Variables.Break = True

    Time = time.time()
    if Time - Variables.LastMouseInput < 3 or Time - Variables.LastWindowResize < 3 or Time - Variables.LastWindowMove < 3:
        Variables.DynamicFPS = 60
    elif Variables.LogPath == "":
        Variables.DynamicFPS = 30
    else:
        Variables.DynamicFPS = 10

    TimeToSleep = 1/Variables.DynamicFPS - (time.perf_counter() - Start)
    if TimeToSleep > 0:
        time.sleep(TimeToSleep)

Console.CloseConsole()