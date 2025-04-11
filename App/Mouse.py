from CrashReport import CrashReport
import Variables
import Graph

import SimpleWindow
import threading
import traceback
import ctypes
import pynput
import mouse
import time


def Run():
    try:
        def RunThread():
            try:
                MoveStart = 0, 0
                WasDisabled = False
                LastScrollWheel = 0
                LastMousePosition = 0, 0
                while Variables.Break == False:
                    if SimpleWindow.GetForeground(Variables.WindowName) == False:
                        time.sleep(0.1)
                        WasDisabled = True
                        continue

                    Start = time.perf_counter()

                    WindowX = Variables.WindowX + Variables.GraphUIPositionX1
                    WindowY = Variables.WindowY + Variables.GraphUIPositionY1
                    WindowWidth = Variables.GraphUIPositionX2 - Variables.GraphUIPositionX1
                    WindowHeight = Variables.GraphUIPositionY2 - Variables.GraphUIPositionY1
                    MouseX, MouseY = mouse.get_position()

                    LeftClicked = ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight
                    RightClicked = ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight

                    if LeftClicked == True or RightClicked == True:
                        Variables.LastMouseInput = time.time()

                    if WasDisabled:
                        while True:
                            WindowX = Variables.WindowX + Variables.GraphUIPositionX1
                            WindowY = Variables.WindowY + Variables.GraphUIPositionY1
                            WindowWidth = Variables.GraphUIPositionX2 - Variables.GraphUIPositionX1
                            WindowHeight = Variables.GraphUIPositionY2 - Variables.GraphUIPositionY1
                            MouseX, MouseY = mouse.get_position()

                            LeftClicked = ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight
                            RightClicked = ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight
                            if LeftClicked == False and RightClicked == False:
                                WasDisabled = False
                                break

                    if WindowX <= MouseX <= WindowX + WindowWidth and WindowY <= MouseY <= WindowY + WindowHeight:
                        with pynput.mouse.Events() as Events:
                            Event = Events.get()
                            if isinstance(Event, pynput.mouse.Events.Scroll):
                                LastScrollWheel = time.time()
                                Variables.LastMouseInput = time.time()
                                CanvasX = (MouseX - WindowX - Variables.GraphPosition[0]) / Variables.GraphZoom
                                CanvasY = (MouseY - WindowY - Variables.GraphPosition[1]) / Variables.GraphZoom
                                if Variables.GraphZoom < 10000:
                                    Variables.GraphZoom = Variables.GraphZoom * 1.1 if Event.dy > 0 else Variables.GraphZoom / 1.1
                                elif Event.dy < 0:
                                    Variables.GraphZoom /= 1.1
                                Variables.GraphPosition = (MouseX - WindowX - CanvasX * Variables.GraphZoom, MouseY - WindowY - CanvasY * Variables.GraphZoom)

                        if RightClicked == False:
                            MoveStart = MouseX - Variables.GraphPosition[0], MouseY - Variables.GraphPosition[1]
                        else:
                            Variables.GraphPosition = (MouseX - MoveStart[0]), (MouseY - MoveStart[1])

                        if LastMousePosition != (MouseX, MouseY):
                            Variables.LastMouseMove = time.time()
                            LastMousePosition = MouseX, MouseY

                    TimeToSleep = 1/Variables.DynamicFPS - (time.perf_counter() - Start)
                    if TimeToSleep > 0 and time.time() - LastScrollWheel > 3:
                        time.sleep(TimeToSleep)
            except:
                CrashReport("Mouse - Error in function RunThread.", str(traceback.format_exc()))
        threading.Thread(target=RunThread, daemon=True).start()
    except:
        CrashReport("Mouse - Error in function Run.", str(traceback.format_exc()))