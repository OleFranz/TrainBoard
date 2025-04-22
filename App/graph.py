from crashreport import crash_report
import threading
import traceback
import variables
import settings
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
graphs = {}

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
                    if variables.window.get_foreground() == False:
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

        if variables.tab == "Graphs":
            for i, graph_name in enumerate(graphs):
                show_state = graphs[graph_name]["show"]
                color = graphs[graph_name]["color"]
                ImageUI.Switch(Text=graph_name,
                            X1=5,
                            Y1=variables.graph_ui_position_y1 + 10 + 30 * i,
                            X2=variables.graph_ui_position_x1 - 26,
                            Y2=variables.graph_ui_position_y1 + 35 + 30 * i,
                            ID=f"graph_switch_{graph_name}",
                            State=show_state,
                            OnChange=lambda state, graph_name=graph_name, color=color: {
                                settings.set("graph", f"{variables.log_path}:{graph_name}:show", state),
                                getattr(__import__(__name__), "graphs").__setitem__(graph_name, {"data": graphs[graph_name]["data"], "color": color, "show": state})
                            })

                color_image = numpy.zeros((15, 15, 3), numpy.uint8)
                color_image[:] = color
                ImageUI.Image(Image=color_image,
                              X1=variables.graph_ui_position_x1 - 21,
                              Y1=variables.graph_ui_position_y1 + 15 + 30 * i,
                              X2=variables.graph_ui_position_x1 - 6,
                              Y2=variables.graph_ui_position_y1 + 30 + 30 * i,
                              ID=f"graph_color_{graph_name}",
                              RoundCorners=12)

            if graph_position != (0, 0) or graph_zoom != 1:
                ImageUI.Button(Text="Center the graph",
                               X1=5,
                               Y1=variables.graph_ui_position_y2 - 85,
                               X2=variables.graph_ui_position_x1 - 5,
                               Y2=variables.graph_ui_position_y2 - 45,
                               ID="CenterGraphButton",
                               RoundCorners=10,
                               OnPress=lambda: {
                                   setattr(__import__(__name__), "graph_position", (0, 0)),
                                   setattr(__import__(__name__), "graph_zoom", 1)
                               })

        content = (graph_position,
                   graph_zoom,
                   [len(graph["data"].keys()) for graph in graphs.values()],
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
                return

            # get all the x and y values of the shown graphs
            x_values = [epoch for name, data in graphs.items() if graphs[name]["show"] for epoch, (_, _) in data["data"].items()]
            y_values = [value for name, data in graphs.items() if graphs[name]["show"] for _, (value, _) in data["data"].items()]

            min_x = min(x_values) if len(x_values) > 0 else 0
            max_x = max(x_values) if len(x_values) > 0 else 0
            min_y = min(y_values) if len(y_values) > 0 else 0
            max_y = max(y_values) if len(y_values) > 0 else 0

            min_y = min_y - (max_y - min_y) * 0.1
            max_y = max_y + (max_y - min_y) * 0.1

            min_y = 0 if min_y < 0 else min_y

            x_axis_scale = (max(1, min(5, max_x - 1)) + 1 - min_x) if max_x != min_x else 1
            x_axis_max = min_x + ((max_x + x_axis_scale - 1 - min_x) // x_axis_scale) * x_axis_scale
            y_axis_scale = max(5, round(graph_zoom * 5))

            for i in range(x_axis_scale + 1):
                float_x = i / x_axis_scale
                x, y = convert_to_frame_coordinate(float_x, 1)
                if -10 <= x <= background.shape[1] + 9:
                    cv2.line(frame, convert_to_frame_coordinate(float_x, 0), convert_to_frame_coordinate(float_x, 1), (180, 180, 180) if float_x == 0 else (50, 50, 50), 1)
                    cv2.line(frame, (x, y - 3), (x, y + 3), (180, 180, 180), 1)
                    text, font_scale, thickness, width, height = get_text_size(f"{int(min_x + (x_axis_max - min_x) * float_x):,}".replace(",", "."), 10)
                    y = round(y + height * 1.5)
                    if y >= background.shape[0] - 2:
                        y = background.shape[0] - 2
                    cv2.putText(frame,
                                text,
                                (round(x - width / 2), y),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                font_scale,
                                (180, 180, 180),
                                thickness,
                                cv2.LINE_AA)

            for i in range(y_axis_scale + 1):
                float_y = 1 - i / y_axis_scale
                x, y = convert_to_frame_coordinate(0, float_y)
                if -10 <= y <= background.shape[0] + 9:
                    cv2.line(frame, convert_to_frame_coordinate(0, float_y), convert_to_frame_coordinate(1, float_y), (180, 180, 180) if float_y == 1 else (50, 50, 50), 1)
                    cv2.line(frame, (x - 3, y), (x + 3, y), (180, 180, 180), 1)
                    text, font_scale, thickness, width, height = get_text_size(f"{round(max_y - (max_y - min_y) * float_y, max(2, min(9, round(3 * (graph_zoom / 100) * 100)))):,}".replace(",", "#").replace(".", ",").replace("#", "."), 10)
                    x = round(x - width * 1.1)
                    if x < 1:
                        x = 1
                    cv2.putText(frame,
                                text,
                                (x, round(y + height / 2)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                font_scale,
                                (180, 180, 180),
                                thickness,
                                cv2.LINE_AA)

            for graph_name in graphs.keys():
                if graphs[graph_name]["show"] == False: continue
                graph = graphs[graph_name]["data"]
                last_point = None
                for x in list(graph.keys()):
                    y = graph[x][0] # (value, time) -> value
                    x, y = convert_to_frame_coordinate((x - min_x) / (x_axis_max - min_x) if x_axis_max - min_x != 0 else 0, (max_y - y) / (max_y - min_y) if max_y - min_y != 0 else 0)
                    if len(graph.keys()) == 1:
                        cv2.circle(frame, (x, y), 1, graphs[graph_name]["color"], 2, cv2.LINE_AA)
                    if last_point != None:
                        cv2.line(frame, last_point, (x, y), graphs[graph_name]["color"], 1, cv2.LINE_AA)
                    last_point = (x, y)

            last_content = content

        if variables.tab == "Graphs":
            ImageUI.Image(Image=frame,
                          X1=variables.graph_ui_position_x1,
                          Y1=variables.graph_ui_position_y1,
                          X2=variables.graph_ui_position_x2,
                          Y2=variables.graph_ui_position_y2,
                          ID="graph_image",
                          RoundCorners=20)

    except:
        crash_report("Graph - Error in function update", str(traceback.format_exc()))