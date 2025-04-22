import SimpleWindow
import settings
import numpy
import os

path = os.path.dirname(os.path.abspath(__file__))
if path[-1] != "/": path += "/"

log_path = settings.get("log", "path", "")
log_path_history = settings.get("log", "path_history", [])

stop = False
dynamic_fps = 10

last_mouse_move = 0
last_mouse_input = 0
last_window_move = 0
last_window_resize = 0

tab = settings.get("ui", "tab", "Graphs")

window: SimpleWindow.Window = None
window_name = "TrainBoard"
window_x = settings.get("ui", "x", 100)
window_y = settings.get("ui", "y", 100)
window_width = settings.get("ui", "width", 960)
window_height = settings.get("ui", "height", 540)

background = numpy.zeros((window_height, window_width, 3), dtype=numpy.uint8)
background[:] = (28, 28, 28)

status = None

graph_ui_position_x1 = 200
graph_ui_position_y1 = 50
graph_ui_position_x2 = window_width - 6
graph_ui_position_y2 = window_height - 6