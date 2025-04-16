from crashreport import crash_report
import SimpleWindow
import threading
import traceback
import variables
import ImageUI
import ctypes
import pynput
import mouse
import numpy
import time
import cv2


last_content = None
frame = None

background = numpy.zeros((variables.window_height, variables.window_width, 3), numpy.uint8)
background[:] = (25, 25, 25)

graph_zoom = 1
graph_position = 0, 0

graph_colors = [
    (203, 181, 18),
    (146, 37, 229),
    (0, 171, 249),
    (230, 52, 147),
    (66, 179, 124),
    (10, 113, 232),
    (163, 152, 142)
]


def start_mouse_tracking():
    try:
        def thread():
            global graph_zoom
            global graph_position
            try:
                move_start = 0, 0
                was_disabled = False
                last_scroll_wheel = 0
                last_mouse_position = 0, 0
                while variables.stop == False:
                    if SimpleWindow.GetForeground(variables.window_name) == False:
                        time.sleep(0.1)
                        was_disabled = True
                        continue

                    start = time.perf_counter()

                    graph_x = variables.window_x + variables.graph_ui_position_x1
                    graph_y = variables.window_y + variables.graph_ui_position_y1
                    graph_width = variables.graph_ui_position_x2 - variables.graph_ui_position_x1
                    graph_height = variables.graph_ui_position_y2 - variables.graph_ui_position_y1
                    mouse_x, mouse_y = mouse.get_position()

                    mouse_left_pressed = ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and graph_x <= mouse_x <= graph_x + graph_width and graph_y <= mouse_y <= graph_y + graph_height
                    mouse_right_pressed = ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and graph_x <= mouse_x <= graph_x + graph_width and graph_y <= mouse_y <= graph_y + graph_height

                    if ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 or ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0:
                        variables.last_mouse_input = time.time()

                    if was_disabled:
                        while True:
                            graph_x = variables.window_x + variables.graph_ui_position_x1
                            graph_y = variables.window_y + variables.graph_ui_position_y1
                            graph_width = variables.graph_ui_position_x2 - variables.graph_ui_position_x1
                            graph_height = variables.graph_ui_position_y2 - variables.graph_ui_position_y1
                            mouse_x, mouse_y = mouse.get_position()

                            mouse_left_pressed = ctypes.windll.user32.GetKeyState(0x01) & 0x8000 != 0 and graph_x <= mouse_x <= graph_x + graph_width and graph_y <= mouse_y <= graph_y + graph_height
                            mouse_right_pressed = ctypes.windll.user32.GetKeyState(0x02) & 0x8000 != 0 and graph_x <= mouse_x <= graph_x + graph_width and graph_y <= mouse_y <= graph_y + graph_height
                            if mouse_left_pressed == False and mouse_right_pressed == False:
                                was_disabled = False
                                break

                    if graph_x <= mouse_x <= graph_x + graph_width and graph_y <= mouse_y <= graph_y + graph_height and variables.tab == "Graphs":
                        with pynput.mouse.Events() as Events:
                            Event = Events.get()
                            if isinstance(Event, pynput.mouse.Events.Scroll):
                                if mouse_right_pressed == False:
                                    last_scroll_wheel = time.time()
                                    variables.last_mouse_input = time.time()
                                    canvas_x = (mouse_x - graph_x - graph_position[0]) / graph_zoom
                                    canvas_y = (mouse_y - graph_y - graph_position[1]) / graph_zoom
                                    if graph_zoom < 10000:
                                        graph_zoom = graph_zoom * 1.1 if Event.dy > 0 else graph_zoom / 1.1
                                    elif Event.dy < 0:
                                        graph_zoom /= 1.1
                                    graph_position = (mouse_x - graph_x - canvas_x * graph_zoom, mouse_y - graph_y - canvas_y * graph_zoom)

                        if mouse_right_pressed == False:
                            move_start = mouse_x - graph_position[0], mouse_y - graph_position[1]
                        else:
                            graph_position = (mouse_x - move_start[0]), (mouse_y - move_start[1])

                        if last_mouse_position != (mouse_x, mouse_y):
                            variables.last_mouse_move = time.time()
                            last_mouse_position = mouse_x, mouse_y

                    time_to_sleep = 1/(variables.dynamic_fps * 2) - (time.perf_counter() - start)
                    if time_to_sleep > 0 and time.time() - last_scroll_wheel > 3:
                        time.sleep(time_to_sleep)
            except:
                crash_report("Graph - Error in function thread", str(traceback.format_exc()))
        threading.Thread(target=thread, daemon=True).start()
    except:
        crash_report("Graph - Error in function start_mouse_tracking", str(traceback.format_exc()))


def convert_to_frame_coordinate(x, y):
    right = background.shape[1]
    bottom = background.shape[0]
    x = round(((x + 72 / right) * right * ((right - 89) / right) + graph_position[0] * 1 / graph_zoom) * graph_zoom)
    y = round(((y + 27 / bottom) * bottom * ((bottom - 49) / bottom) + graph_position[1] * 1 / graph_zoom) * graph_zoom)
    return x, y


def get_text_size(text:str, font_size:int=10):
    try:
        font_scale = 1
        text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
        _, height_current_text = text_size
        max_count_current_text = 3
        while height_current_text > font_size:
            font_scale *= font_size / text_size[1]
            text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
            max_count_current_text -= 1
            if max_count_current_text <= 0:
                break
        thickness = round(font_scale * 2)
        if thickness <= 0:
            thickness = 1
        return text, font_scale, thickness, text_size[0], text_size[1]
    except:
        print("Graph - Error in function get_text_size", str(traceback.format_exc()))
        return "", 1, 1, 100, 100

def update():
    try:
        global last_content
        global frame
        global background

        content = (graph_position,
                   graph_zoom,
                   [graph.values() for graph in variables.graphs.values()],
                   variables.window_width,
                   variables.window_height,
                   variables.tab)

        if last_content != content:
            graph_width = variables.graph_ui_position_x2 - variables.graph_ui_position_x1
            graph_height = variables.graph_ui_position_y2 - variables.graph_ui_position_y1
            if background.shape != (graph_height, graph_width, 3):
                background = numpy.zeros((graph_height, graph_width, 3), numpy.uint8)
                background[:] = (25, 25, 25)
            frame = background.copy()

            if variables.tab != "Graphs":
                last_content = content
                ImageUI.Image(Image=frame,
                              X1=variables.graph_ui_position_x1,
                              Y1=variables.graph_ui_position_y1,
                              X2=variables.graph_ui_position_x2,
                              Y2=variables.graph_ui_position_y2,
                              ID="GraphImage",
                              RoundCorners=20)
                return

            x_values = [key for graph in variables.graphs.values() for key in graph.keys()]
            y_values = [value for graph in variables.graphs.values() for value in graph.values()]

            MinX = min(x_values) if len(x_values) > 0 else 0
            MaxX = max(x_values) if len(x_values) > 0 else 0
            MinY = min(y_values) if len(y_values) > 0 else 0
            MaxY = max(y_values) if len(y_values) > 0 else 0

            MinY = MinY - (MaxY - MinY) * 0.1
            MaxY = MaxY + (MaxY - MinY) * 0.1

            MinY = 0 if MinY < 0 else MinY
            MaxX += 1 if MaxX == MinX else 0

            XAxisScale = max(1, min(5, MaxX - 1))
            XAxisMax = MinX + ((MaxX + XAxisScale - 2) // XAxisScale) * XAxisScale
            YAxisScale = max(5, round(graph_zoom * 5))

            for i in range(XAxisScale + 1):
                FloatX = i / XAxisScale
                X, Y = convert_to_frame_coordinate(FloatX, 1)
                if -10 <= X <= background.shape[1] + 9:
                    cv2.line(frame, convert_to_frame_coordinate(FloatX, 0), convert_to_frame_coordinate(FloatX, 1), (180, 180, 180) if FloatX == 0 else (50, 50, 50), 1)
                    cv2.line(frame, (X, Y - 3), (X, Y + 3), (180, 180, 180), 1)
                    Text, Fontscale, Thickness, Width, Height = get_text_size(f"{int(MinX + (XAxisMax - MinX) * FloatX):,}".replace(",", "."), 10)
                    Y = round(Y + Height * 1.5)
                    if Y >= background.shape[0] - 2:
                        Y = background.shape[0] - 2
                    cv2.putText(frame,
                                Text,
                                (round(X - Width / 2), Y),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                Fontscale,
                                (180, 180, 180),
                                Thickness,
                                cv2.LINE_AA)

            for i in range(YAxisScale + 1):
                FloatY = 1 - i / YAxisScale
                X, Y = convert_to_frame_coordinate(0, FloatY)
                if -10 <= Y <= background.shape[0] + 9:
                    cv2.line(frame, convert_to_frame_coordinate(0, FloatY), convert_to_frame_coordinate(1, FloatY), (180, 180, 180) if FloatY == 1 else (50, 50, 50), 1)
                    cv2.line(frame, (X - 3, Y), (X + 3, Y), (180, 180, 180), 1)
                    Text, Fontscale, Thickness, Width, Height = get_text_size(f"{round(MaxY - (MaxY - MinY) * FloatY, max(2, min(9, round(3 * (graph_zoom / 100) * 100)))):,}".replace(",", "#").replace(".", ",").replace("#", "."), 10)
                    X = round(X - Width * 1.1)
                    if X < 1:
                        X = 1
                    cv2.putText(frame,
                                Text,
                                (X, round(Y + Height / 2)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                Fontscale,
                                (180, 180, 180),
                                Thickness,
                                cv2.LINE_AA)

            for graph in variables.graphs.values():
                last_point = None
                for X in sorted(graph.keys(), key=lambda x: x):
                    X, Y = convert_to_frame_coordinate((X - MinX) / (XAxisMax - MinX) if XAxisMax - MinX != 0 else 0, (MaxY - graph[X]) / (MaxY - MinY) if MaxY - MinY != 0 else 0)
                    #if len(Graph[2]) == 1:
                    #    cv2.circle(frame, (X, Y), 1, Graph[1], 2, cv2.LINE_AA)
                    if last_point != None:
                        cv2.line(frame, last_point, (X, Y), (255, 255, 255), 1, cv2.LINE_AA)
                    last_point = (X, Y)


            ImageUI.Image(Image=frame,
                        X1=variables.graph_ui_position_x1,
                        Y1=variables.graph_ui_position_y1,
                        X2=variables.graph_ui_position_x2,
                        Y2=variables.graph_ui_position_y2,
                        ID="GraphImage",
                        RoundCorners=20)

            last_content = content

        else:

            ImageUI.Image(Image=frame,
                          X1=variables.graph_ui_position_x1,
                          Y1=variables.graph_ui_position_y1,
                          X2=variables.graph_ui_position_x2,
                          Y2=variables.graph_ui_position_y2,
                          ID="GraphImage",
                          RoundCorners=20)

    except:
        crash_report("Graph - Error in function update", str(traceback.format_exc()))