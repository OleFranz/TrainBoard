from CrashReport import CrashReport
import traceback
import Variables
import numpy
import math
import cv2

LastContent = None
Frame = None

def ConvertToImageCoordinate(X, Y, Round=True):
    X = (X + Variables.GraphPosition[0] * 1 / Variables.GraphZoom) * Variables.GraphZoom
    Y = (Y + Variables.GraphPosition[1] * 1 / Variables.GraphZoom) * Variables.GraphZoom
    if Round == True:
        X = round(X)
        Y = round(Y)
    return X, Y

def Update():
    try:
        global LastContent
        global Frame

        Content = (len(Variables.GraphContent),
                   Variables.GraphPosition,
                   Variables.GraphZoom)

        if LastContent != Content:
            GraphWidth = Variables.GraphUIPositionX2 - Variables.GraphUIPositionX1
            GraphHeight = Variables.GraphUIPositionY2 - Variables.GraphUIPositionY1
            if Variables.Graph.shape != (GraphHeight, GraphWidth, 3):
                Variables.Graph = numpy.zeros((GraphHeight, GraphWidth, 3), numpy.uint8)
                Variables.Graph[:] = (28, 28, 28)
            Frame = Variables.Graph.copy()

            for GraphName, GraphDat in Variables.GraphContent:
                ...

            cv2.circle(Frame, ConvertToImageCoordinate(0, 0), 5, (0, 255, 0), -1)
            cv2.circle(Frame, ConvertToImageCoordinate(100, 0), 5, (0, 255, 0), -1)
            cv2.circle(Frame, ConvertToImageCoordinate(100, 100), 5, (0, 255, 0), -1)
            cv2.circle(Frame, ConvertToImageCoordinate(0, 100), 5, (0, 255, 0), -1)

            LastContent = Content
    except:
        CrashReport("Graph - Error in function Update.", str(traceback.format_exc()))