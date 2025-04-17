import SimpleWindow
import logreader
import variables
import settings
import console
import ImageUI
import image
import graph
import model
import numpy
import time
import os

SimpleWindow.Initialize(Name=variables.window_name,
                        Size=(variables.window_width, variables.window_height),
                        Position=(variables.window_x, variables.window_y),
                        TitleBarColor=variables.background[0][0],
                        Resizable=True,
                        TopMost=False,
                        Foreground=True,
                        Minimized=False,
                        Undestroyable=False,
                        Icon=f"{variables.path}Icon.ico",
                        NoWarnings=False)

console.hide_console()
logreader.start_log_reader()
graph.start_mouse_tracking()

ImageUI.Colors.SwitchEnabledColor = (30, 125, 255)
ImageUI.Colors.SwitchEnabledHoverColor = (30, 125, 255)

while variables.stop == False:
    Start = time.perf_counter()

    window_size = SimpleWindow.GetSize(Name=variables.window_name)
    window_position = SimpleWindow.GetPosition(Name=variables.window_name)

    if window_size[0] != variables.window_width or window_size[1] != variables.window_height:
        variables.last_window_resize = time.time()
        variables.window_width = window_size[0]
        variables.window_height = window_size[1]
        variables.graph_ui_position_x2 = window_size[0] - 6
        variables.graph_ui_position_y2 = window_size[1] - 6
        variables.background = numpy.zeros((variables.window_height, variables.window_width, 3), dtype=numpy.uint8)
        variables.background[:] = (28, 28, 28)
        settings.set("ui", "width", variables.window_width)
        settings.set("ui", "height", variables.window_height)

    if window_position[0] != variables.window_x or window_position[1] != variables.window_y:
        variables.last_window_move = time.time()
        variables.window_x = window_position[0]
        variables.window_y = window_position[1]
        settings.set("ui", "x", variables.window_x)
        settings.set("ui", "y", variables.window_y)


    Left = 0
    Right = variables.background.shape[1] - 1
    Top = 0
    Bottom = variables.background.shape[0] - 1

    if variables.log_path != "":
        logreader.sync_data()

        graph.update()
        image.update()
        model.update()

        ImageUI.Label(Text="TrainBoard",
                      X1=0,
                      Y1=0,
                      X2=variables.graph_ui_position_x1,
                      Y2=variables.graph_ui_position_y1,
                      Align="Center",
                      ID="title_label",
                      FontSize=25,
                      FontType="Candarab")

        ImageUI.Button(Text="Graphs",
                       X1=variables.graph_ui_position_x1,
                       Y1=5,
                       X2=variables.graph_ui_position_x1 + (variables.graph_ui_position_x2 - variables.graph_ui_position_x1) / 3 - 2.5,
                       Y2=variables.graph_ui_position_y1 - 5,
                       ID="graphs_tab",
                       RoundCorners=10,
                       Color=(30, 125, 255) if variables.tab == "Graphs" else ImageUI.Colors.ButtonColor,
                       HoverColor=(35, 130, 255) if variables.tab == "Graphs" else ImageUI.Colors.ButtonHoverColor,
                       TextColor=(0, 0, 0) if variables.tab == "Graphs" else (255, 255, 255),
                       OnPress=lambda: {settings.set("ui", "tab", "Graphs"), setattr(variables, "tab", "Graphs")})

        ImageUI.Button(Text="Images",
                       X1=variables.graph_ui_position_x1 + (variables.graph_ui_position_x2 - variables.graph_ui_position_x1) / 3 + 2.5,
                       Y1=5,
                       X2=variables.graph_ui_position_x1 + (variables.graph_ui_position_x2 - variables.graph_ui_position_x1) / 1.5 - 2.5,
                       Y2=variables.graph_ui_position_y1 - 5,
                       ID="images_tab",
                       RoundCorners=10,
                       Color=(30, 125, 255) if variables.tab == "Images" else ImageUI.Colors.ButtonColor,
                       HoverColor=(35, 130, 255) if variables.tab == "Images" else ImageUI.Colors.ButtonHoverColor,
                       TextColor=(0, 0, 0) if variables.tab == "Images" else (255, 255, 255),
                       OnPress=lambda: {settings.set("ui", "tab", "Images"), setattr(variables, "tab", "Images")})

        ImageUI.Button(Text="Models",
                       X1=variables.graph_ui_position_x1 + (variables.graph_ui_position_x2 - variables.graph_ui_position_x1) / 1.5 + 2.5,
                       Y1=5,
                       X2=variables.graph_ui_position_x2,
                       Y2=variables.graph_ui_position_y1 - 5,
                       ID="models_tab",
                       RoundCorners=10,
                       Color=(30, 125, 255) if variables.tab == "Models" else ImageUI.Colors.ButtonColor,
                       HoverColor=(35, 130, 255) if variables.tab == "Models" else ImageUI.Colors.ButtonHoverColor,
                       TextColor=(0, 0, 0) if variables.tab == "Models" else (255, 255, 255),
                       OnPress=lambda: {settings.set("ui", "tab", "Models"), setattr(variables, "tab", "Models")})

        ImageUI.Button(Text="Change the log path",
                       X1=5,
                       Y1=variables.graph_ui_position_y2 - 40,
                       X2=variables.graph_ui_position_x1 - 5,
                       Y2=variables.graph_ui_position_y2,
                       ID="log_path_change_button",
                       RoundCorners=10,
                       OnPress=logreader.clear_log_path)

    else:

        ImageUI.Label(Text="TrainBoard",
                      X1=0,
                      Y1=Bottom / 2 - 30,
                      X2=Right,
                      Y2=Bottom / 2 - 70,
                      Align="Center",
                      ID="title_label",
                      FontSize=25,
                      FontType="Candarab")

        ImageUI.Input(X1=Right / 2 - 250,
                      Y1=Bottom / 2 - 20,
                      X2=Right / 2 + 250,
                      Y2=Bottom / 2 + 20,
                      Placeholder="Enter the absolute path to the log folder",
                      TextAlign="Center",
                      ID="log_path_input",
                      RoundCorners=10,
                      OnChange=logreader.set_log_path)

        for i in range(min(len(variables.log_path_history), 3)):
            ImageUI.Button(Text=variables.log_path_history[i],
                           X1=Right / 2 - 225,
                           Y1=Bottom / 2 + 30 + 35 * i,
                           X2=Right / 2 + 190,
                           Y2=Bottom / 2 + 60 + 35 * i,
                           ID=f"log_path_history_button_{i}_select",
                           FontSize=12,
                           RoundCorners=10,
                           OnPress=lambda i=i: {os.makedirs(variables.log_path_history[i], exist_ok=True), logreader.set_log_path(variables.log_path_history[i])})

            ImageUI.Button(Text="X",
                           X1=Right / 2 + 195,
                           Y1=Bottom / 2 + 30 + 35 * i,
                           X2=Right / 2 + 225,
                           Y2=Bottom / 2 + 60 + 35 * i,
                           ID=f"log_path_history_button_{i}_remove",
                           FontSize=12,
                           RoundCorners=10,
                           OnPress=lambda i=i: {variables.log_path_history.remove(variables.log_path_history[i]), settings.set("log", "path_history", variables.log_path_history)})

    window_handle = SimpleWindow.GetHandle(Name=variables.window_name)
    frame = ImageUI.Update(WindowHWND=window_handle, Frame=variables.background)

    SimpleWindow.Show(Name=variables.window_name, Frame=frame)
    if SimpleWindow.GetOpen(Name=variables.window_name) != True:
        console.restore_console()
        variables.stop = True

    current_time = time.time()
    if current_time - variables.last_mouse_input < 3 or current_time - variables.last_window_resize < 3 or current_time - variables.last_window_move < 3:
        variables.dynamic_fps = 60
    elif variables.log_path == "" or current_time - variables.last_mouse_move < 1:
        variables.dynamic_fps = 30
    else:
        variables.dynamic_fps = 10

    TimeToSleep = 1/variables.dynamic_fps - (time.perf_counter() - Start)
    if TimeToSleep > 0:
        time.sleep(TimeToSleep)

console.restore_console()
console.close_console()