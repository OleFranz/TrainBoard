import SimpleWindow
import settings
import ImageUI
import numpy
import data
import time


WindowName = "TrainBoard"
WindowX = settings.Get("Window", "X", 100)
WindowY = settings.Get("Window", "Y", 100)
WindowWidth = settings.Get("Window", "Width", 960)
WindowHeight = settings.Get("Window", "Height", 540)

Background = numpy.zeros((WindowHeight, WindowWidth, 3), dtype=numpy.uint8)
Background[:] = (28, 28, 28)


SimpleWindow.Initialize(Name=WindowName,
                        Size=(WindowWidth, WindowHeight),
                        Position=(WindowX, WindowY),
                        TitleBarColor=Background[0][0],
                        Resizable=True,
                        TopMost=False,
                        Foreground=True,
                        Minimized=False,
                        Undestroyable=False,
                        Icon="",
                        NoWarnings=False)


data.StartLogReader()


while True:
    Start = time.perf_counter()

    WindowSize = SimpleWindow.GetSize(Name=WindowName)
    WindowPosition = SimpleWindow.GetPosition(Name=WindowName)

    if WindowSize[0] != WindowWidth or WindowSize[1] != WindowHeight:
        WindowWidth = WindowSize[0]
        WindowHeight = WindowSize[1]
        Background = numpy.zeros((WindowHeight, WindowWidth, 3), dtype=numpy.uint8)
        Background[:] = (28, 28, 28)
        settings.Set("Window", "Width", WindowWidth)
        settings.Set("Window", "Height", WindowHeight)

    if WindowPosition[0] != WindowX or WindowPosition[1] != WindowY:
        WindowX = WindowPosition[0]
        WindowY = WindowPosition[1]
        settings.Set("Window", "X", WindowX)
        settings.Set("Window", "Y", WindowY)

    WindowHandle = SimpleWindow.GetHandle(Name=WindowName)
    Frame = ImageUI.Update(WindowHWND=WindowHandle, Frame=Background)

    SimpleWindow.Show(Name=WindowName, Frame=Frame)
    if SimpleWindow.GetOpen(Name=WindowName) != True:
        break

    TimeToSleep = 1/30 - (time.perf_counter() - Start)
    if TimeToSleep > 0:
        time.sleep(TimeToSleep)