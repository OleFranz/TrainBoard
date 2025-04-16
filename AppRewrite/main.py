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
        graph.update()
    #    Image.Update()
    #    Model.Update()

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
                       ID="GraphsTab",
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
                       ID="ImagesTab",
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
                       ID="ModelsTab",
                       RoundCorners=10,
                       Color=(30, 125, 255) if variables.tab == "Models" else ImageUI.Colors.ButtonColor,
                       HoverColor=(35, 130, 255) if variables.tab == "Models" else ImageUI.Colors.ButtonHoverColor,
                       TextColor=(0, 0, 0) if variables.tab == "Models" else (255, 255, 255),
                       OnPress=lambda: {settings.set("ui", "tab", "Models"), setattr(variables, "tab", "Models")})

    #    if variables.tab == "Graphs":
    #        for i, GraphName in enumerate(Variables.Graphs):
    #            FileName = Variables.Graphs[GraphName]["FileName"]
    #            ShowState = Variables.Graphs[GraphName]["Show"]
    #            Data = Variables.Graphs[GraphName]["Data"]
    #            ImageUI.Switch(Text=GraphName,
    #                        X1=5,
    #                        Y1=variables.graph_ui_position_y1 + 10 + 30 * i,
    #                        X2=variables.graph_ui_position_x1 - 26,
    #                        Y2=variables.graph_ui_position_y1 + 35 + 30 * i,
    #                        ID=f"GraphSwitch{GraphName}",
    #                        State=ShowState,
    #                        OnChange=lambda State, GraphName=GraphName: {
    #                            settings.set("Graphs", Variables.LogPath + ":Show:" + GraphName, State),
    #                            getattr(Variables, "Graphs").__setitem__(GraphName, {"FileName": FileName, "Show": State, "Data": Data})
    #                        })
#
    #            ColorImage = numpy.zeros((15, 15, 3), numpy.uint8)
    #            ColorsFound = [Graph[1] for Graph in Variables.GraphContent if Graph[0] == GraphName]
    #            ColorImage[:] = ColorsFound[0] if len(ColorsFound) > 0 else (28, 28, 28)
    #            ImageUI.Image(Image=ColorImage,
    #                          X1=variables.graph_ui_position_x1 - 21,
    #                          Y1=variables.graph_ui_position_y1 + 15 + 30 * i,
    #                          X2=variables.graph_ui_position_x1 - 6,
    #                          Y2=variables.graph_ui_position_y1 + 30 + 30 * i,
    #                          ID=f"GraphColor{GraphName}",
    #                          RoundCorners=12)
#
    #        ImageUI.Button(Text="Center the graph",
    #                       X1=5,
    #                       Y1=variables.graph_ui_position_y2 - 85,
    #                       X2=variables.graph_ui_position_x1 - 5,
    #                       Y2=variables.graph_ui_position_y2 - 45,
    #                       ID="CenterGraphButton",
    #                       RoundCorners=10,
    #                       OnPress=lambda: {
    #                           setattr(Variables, "GraphPosition", (0, 0)),
    #                           setattr(Variables, "GraphZoom", 1)
    #                       })
#
    #    elif variables.tab == "Images":
    #        for i, ImageName in enumerate(Variables.Images):
    #            if Variables.SelectedImage == ImageName:
    #                FileName = Variables.Images[ImageName]["FileName"]
    #                SwapRGBBGR = Variables.Images[ImageName]["SwapRGBBGR"]
    #                Data = Variables.Images[ImageName]["Data"]
#
    #                if Variables.SelectedImageEpoch not in (D[1] for D in Data):
    #                    Variables.SelectedImageEpoch = max(D[1] for D in Data)
    #                    ImageUI.SetInput(f"ImageInput{ImageName}", str(Variables.SelectedImageEpoch))
#
    #                ImageUI.Switch(Text="RGB instead of BGR",
    #                            X1=5,
    #                            Y1=variables.graph_ui_position_y1 + 10,
    #                            X2=variables.graph_ui_position_x1 - 6,
    #                            Y2=variables.graph_ui_position_y1 + 35,
    #                            ID=f"ImageSwitch{ImageName}",
    #                            State=SwapRGBBGR,
    #                            OnChange=lambda State, ImageName=ImageName: {
    #                                settings.set("Images", Variables.LogPath + ":SwapRGBBGR:" + ImageName, State),
    #                                getattr(Variables, "Images").__setitem__(ImageName, {"FileName": FileName, "SwapRGBBGR": State, "Data": Data})
    #                            })
#
    #                ImageUI.Button(Text="Previous",
    #                               X1=5,
    #                               Y1=variables.graph_ui_position_y1 + 40,
    #                               X2=variables.graph_ui_position_x1 / 2 - 2.5,
    #                               Y2=variables.graph_ui_position_y1 + 75,
    #                               ID=f"ImagePrevious{ImageName}",
    #                               RoundCorners=10,
    #                               OnPress=lambda ImageName=ImageName: {
    #                                   setattr(Variables, "SelectedImageEpoch", next((D[1] for D in reversed(Data) if D[1] < Variables.SelectedImageEpoch), Variables.SelectedImageEpoch)),
    #                                   ImageUI.SetInput(f"ImageInput{ImageName}", str(Variables.SelectedImageEpoch))
    #                               })
#
    #                ImageUI.Button(Text="Next",
    #                               X1=variables.graph_ui_position_x1 / 2 + 2.5,
    #                               Y1=variables.graph_ui_position_y1 + 40,
    #                               X2=variables.graph_ui_position_x1 - 6,
    #                               Y2=variables.graph_ui_position_y1 + 75,
    #                               ID=f"ImageNext{ImageName}",
    #                               RoundCorners=10,
    #                               OnPress=lambda ImageName=ImageName: {
    #                                   setattr(Variables, "SelectedImageEpoch", next((D[1] for D in Data if D[1] > Variables.SelectedImageEpoch), Variables.SelectedImageEpoch)),
    #                                   ImageUI.SetInput(f"ImageInput{ImageName}", str(Variables.SelectedImageEpoch))
    #                               })
#
    #                ImageUI.Input(X1=5,
    #                              Y1=variables.graph_ui_position_y1 + 80,
    #                              X2=variables.graph_ui_position_x1 / 2 - 2.5,
    #                              Y2=variables.graph_ui_position_y1 + 115,
    #                              ID=f"ImageInput{ImageName}",
    #                              DefaultInput=str(Variables.SelectedImageEpoch),
    #                              Placeholder="Epoch",
    #                              TextAlign="Center",
    #                              OnChange=lambda Input, ImageName=ImageName: {
    #                                  setattr(Variables, "SelectedImageEpoch", (int(Input) if int(Input) in (D[1] for D in Data) else Variables.SelectedImageEpoch) if Input.isdigit() else Variables.SelectedImageEpoch),
    #                                  ImageUI.SetInput(f"ImageInput{ImageName}", str(Variables.SelectedImageEpoch)),
    #                                  None if Input == str(Variables.SelectedImageEpoch) else ImageUI.Popup(Text="Invalid input",
    #                                                                                                        StartX1=-100,
    #                                                                                                        StartY1=variables.graph_ui_position_y1 + 120,
    #                                                                                                        StartX2=0,
    #                                                                                                        StartY2=variables.graph_ui_position_y1 + 150,
    #                                                                                                        EndX1=5,
    #                                                                                                        EndY1=variables.graph_ui_position_y1 + 120,
    #                                                                                                        EndX2=variables.graph_ui_position_x1 - 6,
    #                                                                                                        EndY2=variables.graph_ui_position_y1 + 150,
    #                                                                                                        ID="InvalidInputPopup",
    #                                                                                                        ShowDuration=3,
    #                                                                                                        RoundCorners=10,
    #                                                                                                        TextColor=(50, 50, 255))
    #                              })
#
    #                ImageUI.Button(Text="Latest",
    #                               X1=variables.graph_ui_position_x1 / 2 + 2.5,
    #                               Y1=variables.graph_ui_position_y1 + 80,
    #                               X2=variables.graph_ui_position_x1 - 6,
    #                               Y2=variables.graph_ui_position_y1 + 115,
    #                               ID=f"ImageLatest{ImageName}",
    #                               RoundCorners=10,
    #                               OnPress=lambda ImageName=ImageName: {
    #                                   setattr(Variables, "SelectedImageEpoch", max(D[1] for D in Data)),
    #                                   ImageUI.SetInput(f"ImageInput{ImageName}", str(Variables.SelectedImageEpoch))
    #                               })
#
    #        if list(Variables.Images.keys()) != []:
    #            ImageUI.Dropdown(Title=Variables.SelectedImage,
    #                             Items=list(sorted(Variables.Images.keys(), key=lambda ImageName: Variables.Images[ImageName]["Data"][0][2])),
    #                             DefaultItem=Variables.SelectedImage,
    #                             X1=5,
    #                             Y1=variables.graph_ui_position_y1 + 123,
    #                             X2=variables.graph_ui_position_x1 - 6,
    #                             Y2=variables.graph_ui_position_y1 + 158,
    #                             ID=f"ImageDropdown{list(Variables.Images.keys())}",
    #                             RoundCorners=10,
    #                             OnChange=lambda Item: {
    #                                 setattr(Variables, "SelectedImageEpoch", max(D[1] for D in Variables.Images[Item]["Data"])) if Item != Variables.SelectedImage else None,
    #                                 ImageUI.SetInput(f"ImageInput{Item}", str(Variables.SelectedImageEpoch)),
    #                                 settings.set("Images", Variables.LogPath + ":Selected:", Item),
    #                                 setattr(Variables, "SelectedImage", Item)
    #                             })

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