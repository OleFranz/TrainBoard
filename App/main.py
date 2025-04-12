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

ImageUI.Colors.SwitchEnabledColor = (30, 125, 255)
ImageUI.Colors.SwitchEnabledHoverColor = (30, 125, 255)

while Variables.Break == False:
    Start = time.perf_counter()

    WindowSize = SimpleWindow.GetSize(Name=Variables.WindowName)
    WindowPosition = SimpleWindow.GetPosition(Name=Variables.WindowName)

    if WindowSize[0] != Variables.WindowWidth or WindowSize[1] != Variables.WindowHeight:
        Variables.LastWindowResize = time.time()
        Variables.WindowWidth = WindowSize[0]
        Variables.WindowHeight = WindowSize[1]
        Variables.GraphUIPositionX2 = WindowSize[0] - 6
        Variables.GraphUIPositionY2 = WindowSize[1] - 6
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


    Left = 0
    Right = Variables.Background.shape[1] - 1
    Top = 0
    Bottom = Variables.Background.shape[0] - 1

    if Variables.LogPath != "":
        Graph.Update()

        ImageUI.Image(Image=Graph.Frame,
                    X1=Variables.GraphUIPositionX1,
                    Y1=Variables.GraphUIPositionY1,
                    X2=Variables.GraphUIPositionX2,
                    Y2=Variables.GraphUIPositionY2,
                    ID="GraphImage",
                    RoundCorners=20)

        ImageUI.Label(Text="TrainBoard",
                      X1=0,
                      Y1=0,
                      X2=Variables.GraphUIPositionX1,
                      Y2=Variables.GraphUIPositionY1,
                      Align="Center",
                      ID="LogPathLabel",
                      FontSize=25,
                      FontType="Candarab")

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

        ImageUI.Button(Text="Center the graph",
                       X1=5,
                       Y1=Variables.GraphUIPositionY2 - 85,
                       X2=Variables.GraphUIPositionX1 - 5,
                       Y2=Variables.GraphUIPositionY2 - 45,
                       ID="CenterGraphButton",
                       RoundCorners=10,
                       OnPress=lambda: {
                            setattr(Variables, "GraphPosition", (0, 0)),
                            setattr(Variables, "GraphZoom", 1)
                       })

        ImageUI.Button(Text="Change the log path",
                       X1=5,
                       Y1=Variables.GraphUIPositionY2 - 40,
                       X2=Variables.GraphUIPositionX1 - 5,
                       Y2=Variables.GraphUIPositionY2,
                       ID="ChangeLogPathButton",
                       RoundCorners=10,
                       OnPress=LogReader.ClearLogPath)

        for i, GraphName in enumerate(Variables.Graphs):
            FileName = Variables.Graphs[GraphName]["FileName"]
            ShowState = Variables.Graphs[GraphName]["Show"]
            Data = Variables.Graphs[GraphName]["Data"]
            ImageUI.Switch(Text=GraphName,
                           X1=5,
                           Y1=Variables.GraphUIPositionY1 + 10 + 30 * i,
                           X2=Variables.GraphUIPositionX1 - 5,
                           Y2=Variables.GraphUIPositionY1 + 35 + 30 * i,
                           ID=f"GraphSwitch{GraphName}",
                           State=ShowState,
                           OnChange=lambda State: {
                               Settings.Set("Graphs", Variables.LogPath + ":" + GraphName, State),
                               Variables.Graphs.update({GraphName: {"FileName": FileName, "Show": State, "Data": Data}})
                           })

    else:

        ImageUI.Label(Text="TrainBoard",
                      X1=0,
                      Y1=Bottom / 2 - 30,
                      X2=Right,
                      Y2=Bottom / 2 - 70,
                      Align="Center",
                      ID="LogPathLabel",
                      FontSize=25,
                      FontType="Candarab")

        ImageUI.Input(X1=Right / 2 - 250,
                      Y1=Bottom / 2 - 20,
                      X2=Right / 2 + 250,
                      Y2=Bottom / 2 + 20,
                      Placeholder="Enter the absolute path to the log folder",
                      TextAlign="Center",
                      ID="LogPathInput",
                      RoundCorners=10,
                      OnChange=LogReader.SetLogPath)

        for i in range(min(len(Variables.LogPathHistory), 3)):
            ImageUI.Button(Text=Variables.LogPathHistory[i],
                           X1=Right / 2 - 225,
                           Y1=Bottom / 2 + 30 + 35 * i,
                           X2=Right / 2 + 190,
                           Y2=Bottom / 2 + 60 + 35 * i,
                           ID=f"LogPathHistoryButton{i}Select",
                           FontSize=12,
                           RoundCorners=10,
                           OnPress=lambda i=i: LogReader.SetLogPath(Variables.LogPathHistory[i]))

            ImageUI.Button(Text="X",
                           X1=Right / 2 + 195,
                           Y1=Bottom / 2 + 30 + 35 * i,
                           X2=Right / 2 + 225,
                           Y2=Bottom / 2 + 60 + 35 * i,
                           ID=f"LogPathHistoryButton{i}Remove",
                           FontSize=12,
                           RoundCorners=10,
                           OnPress=lambda i=i: {Variables.LogPathHistory.remove(Variables.LogPathHistory[i]), Settings.Set("Log", "PathHistory", Variables.LogPathHistory)})

    WindowHandle = SimpleWindow.GetHandle(Name=Variables.WindowName)
    Frame = ImageUI.Update(WindowHWND=WindowHandle, Frame=Variables.Background)

    SimpleWindow.Show(Name=Variables.WindowName, Frame=Frame)
    if SimpleWindow.GetOpen(Name=Variables.WindowName) != True:
        Console.RestoreConsole()
        Variables.Break = True

    Time = time.time()
    if Time - Variables.LastMouseInput < 3 or Time - Variables.LastWindowResize < 3 or Time - Variables.LastWindowMove < 3:
        Variables.DynamicFPS = 60
    elif Variables.LogPath == "" or Time - Variables.LastMouseMove < 1:
        Variables.DynamicFPS = 30
    else:
        Variables.DynamicFPS = 10

    TimeToSleep = 1/Variables.DynamicFPS - (time.perf_counter() - Start)
    if TimeToSleep > 0:
        time.sleep(TimeToSleep)

Console.CloseConsole()