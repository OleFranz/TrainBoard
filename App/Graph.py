from CrashReport import CrashReport
import traceback
import Variables
import ImageUI
import numpy
import cv2

LastContent = None
Frame = None

def ConvertToImageCoordinate(X, Y, Round=True):
    Right = Variables.Graph.shape[1]
    Bottom = Variables.Graph.shape[0]
    X = ((X + 24 / Right) * Right * ((Right - 48) / Right) + Variables.GraphPosition[0] * 1 / Variables.GraphZoom) * Variables.GraphZoom
    Y = ((Y + 24 / Bottom) * Bottom * ((Bottom - 48) / Bottom) + Variables.GraphPosition[1] * 1 / Variables.GraphZoom) * Variables.GraphZoom
    if Round == True:
        X = round(X)
        Y = round(Y)
    return X, Y

def Update():
    try:
        global LastContent
        global Frame

        Content = (Variables.GraphContent,
                   Variables.GraphPosition,
                   Variables.GraphZoom,
                   Variables.WindowWidth,
                   Variables.WindowHeight,
                   [Graph["Show"] for Graph in Variables.Graphs.values()])

        if LastContent != Content:
            GraphWidth = Variables.GraphUIPositionX2 - Variables.GraphUIPositionX1
            GraphHeight = Variables.GraphUIPositionY2 - Variables.GraphUIPositionY1
            if Variables.Graph.shape != (GraphHeight, GraphWidth, 3):
                Variables.Graph = numpy.zeros((GraphHeight, GraphWidth, 3), numpy.uint8)
                Variables.Graph[:] = (25, 25, 25)
            Frame = Variables.Graph.copy()


            MinX = min([Graph[2][X][0] for Graph in Variables.GraphContent for X in range(len(Graph[2]))]) if len(Variables.GraphContent) > 0 else 0
            MaxX = max([Graph[2][X][0] for Graph in Variables.GraphContent for X in range(len(Graph[2]))]) if len(Variables.GraphContent) > 0 else 0
            MinY = min([Graph[2][X][1] for Graph in Variables.GraphContent for X in range(len(Graph[2]))]) if len(Variables.GraphContent) > 0 else 0
            MaxY = max([Graph[2][X][1] for Graph in Variables.GraphContent for X in range(len(Graph[2]))]) if len(Variables.GraphContent) > 0 else 0

            MinX = MinX - 1
            MaxX = MaxX + 1
            MinY = MinY - (MaxY - MinY) * 0.1
            MaxY = MaxY + (MaxY - MinY) * 0.1


            XAxisScale = 5
            YAxisScale = 5

            for i in range(XAxisScale + 1):
                FloatX = i / XAxisScale
                X, Y = ConvertToImageCoordinate(FloatX, 1)
                cv2.line(Frame, ConvertToImageCoordinate(FloatX, 0), ConvertToImageCoordinate(FloatX, 1), (180, 180, 180) if FloatX == 0 else (30, 30, 30), 1)
                cv2.line(Frame, (X, Y - 3), (X, Y + 3), (180, 180, 180), 1)

            for i in range(YAxisScale + 1):
                FloatY = 1 - i / YAxisScale
                X, Y = ConvertToImageCoordinate(0, FloatY)
                cv2.line(Frame, ConvertToImageCoordinate(0, FloatY), ConvertToImageCoordinate(1, FloatY), (180, 180, 180) if FloatY == 1 else (30, 30, 30), 1)
                cv2.line(Frame, (X - 3, Y), (X + 3, Y), (180, 180, 180), 1)


            for Graph in Variables.GraphContent:
                if Variables.Graphs[Graph[0]]["Show"]:
                    LastPoint = None
                    for X in range(len(Graph[2])):
                        X, Y = ConvertToImageCoordinate(Graph[2][X][0] / len(Graph[2]), 1 - Graph[2][X][1] / MaxY)
                        if len(Graph[2]) == 1:
                            cv2.circle(Frame, (X, Y), 1, Graph[1], 1, cv2.LINE_AA)
                        elif LastPoint != None:
                            cv2.line(Frame, LastPoint, (X, Y), Graph[1], 1, cv2.LINE_AA)
                        LastPoint = (X, Y)


            LastContent = Content
    except:
        CrashReport("Graph - Error in function Update.", str(traceback.format_exc()))