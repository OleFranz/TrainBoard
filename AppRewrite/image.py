from crashreport import crash_report
import traceback
import variables
import settings
import ImageUI
import cv2


images = {}
selected_image = ""
selected_image_epoch = -1


def update():
    try:
        global selected_image
        global selected_image_epoch

        if variables.tab != "Images":
            return

        if len(images) > 0:
            if selected_image == "":
                selected_image = settings.get("image", variables.log_path + ":selected:", "")
                if selected_image not in images.keys():
                    selected_image = list(images.keys())[0]
                    settings.set("image", variables.log_path + ":selected:", selected_image)
                selected_image_epoch = max(list(images[selected_image]["data"].keys()))

            ImageUI.Dropdown(Title=selected_image,
                             Items=list(images.keys()),
                             DefaultItem=selected_image,
                             X1=5,
                             Y1=variables.graph_ui_position_y1 + 123,
                             X2=variables.graph_ui_position_x1 - 6,
                             Y2=variables.graph_ui_position_y1 + 158,
                             ID=f"image_dropdown_{list(images.keys())}",
                             RoundCorners=10,
                             OnChange=lambda item: {
                                 setattr(__import__(__name__), "selected_image_epoch", max(list(images[item]["data"].keys())) if item != selected_image else selected_image_epoch),
                                 ImageUI.SetInput("image_input", str(selected_image_epoch)),
                                 settings.set("image", variables.log_path + ":selected:", item),
                                 setattr(__import__(__name__), "selected_image", item)
                             })

            ImageUI.Button(Text="Previous",
                           X1=5,
                           Y1=variables.graph_ui_position_y1 + 40,
                           X2=variables.graph_ui_position_x1 / 2 - 2.5,
                           Y2=variables.graph_ui_position_y1 + 75,
                           ID="image_previous",
                           RoundCorners=10,
                           OnPress=lambda selected_image=selected_image: {
                               setattr(__import__(__name__), "selected_image_epoch", max([v for v in list(images[selected_image]["data"].keys()) if v < selected_image_epoch], default=selected_image_epoch)),
                               ImageUI.SetInput("image_input", str(selected_image_epoch))
                           })

            ImageUI.Button(Text="Next",
                           X1=variables.graph_ui_position_x1 / 2 + 2.5,
                           Y1=variables.graph_ui_position_y1 + 40,
                           X2=variables.graph_ui_position_x1 - 6,
                           Y2=variables.graph_ui_position_y1 + 75,
                           ID="image_next",
                           RoundCorners=10,
                           OnPress=lambda selected_image=selected_image: {
                               setattr(__import__(__name__), "selected_image_epoch", min([v for v in list(images[selected_image]["data"].keys()) if v > selected_image_epoch], default=selected_image_epoch)),
                               ImageUI.SetInput("image_input", str(selected_image_epoch))
                           })

            ImageUI.Button(Text="Latest",
                           X1=variables.graph_ui_position_x1 / 2 + 2.5,
                           Y1=variables.graph_ui_position_y1 + 80,
                           X2=variables.graph_ui_position_x1 - 6,
                           Y2=variables.graph_ui_position_y1 + 115,
                           ID="image_latest",
                           RoundCorners=10,
                           OnPress=lambda selected_image=selected_image: {
                               setattr(__import__(__name__), "selected_image_epoch", max(list(images[selected_image]["data"].keys()))),
                               ImageUI.SetInput("image_input", str(selected_image_epoch))
                           })

            ImageUI.Input(X1=5,
                          Y1=variables.graph_ui_position_y1 + 80,
                          X2=variables.graph_ui_position_x1 / 2 - 2.5,
                          Y2=variables.graph_ui_position_y1 + 115,
                          ID="image_input",
                          DefaultInput=str(selected_image_epoch),
                          Placeholder="Epoch",
                          TextAlign="Center",
                          OnChange=lambda input, selected_image=selected_image: {
                              setattr(__import__(__name__), "selected_image_epoch", (int(input) if int(input) in list(images[selected_image]["data"].keys()) else selected_image_epoch) if input.isdigit() else selected_image_epoch),
                              ImageUI.SetInput("image_input", str(selected_image_epoch)),
                              None if input == str(selected_image_epoch) else ImageUI.Popup(Text="Invalid input",
                                                                                            StartX1=-100,
                                                                                            StartY1=variables.graph_ui_position_y1 + 120,
                                                                                            StartX2=0,
                                                                                            StartY2=variables.graph_ui_position_y1 + 150,
                                                                                            EndX1=5,
                                                                                            EndY1=variables.graph_ui_position_y1 + 120,
                                                                                            EndX2=variables.graph_ui_position_x1 - 6,
                                                                                            EndY2=variables.graph_ui_position_y1 + 150,
                                                                                            ID="InvalidInputPopup",
                                                                                            ShowDuration=3,
                                                                                            RoundCorners=10,
                                                                                            TextColor=(50, 50, 255))
                          })

        for i, image_name in enumerate(images):
            if image_name != selected_image: continue

            image = images[image_name]["data"][selected_image_epoch][0] # (image, timestamp) -> image
            swap_rgb_bgr = images[image_name]["swap_rgb_bgr"]

            ImageUI.Switch(Text="Swap RGB/BGR",
                           X1=5,
                           Y1=variables.graph_ui_position_y1 + 10,
                           X2=variables.graph_ui_position_x1 - 26,
                           Y2=variables.graph_ui_position_y1 + 35,
                           ID=f"image_switch_{image_name}",
                           State=swap_rgb_bgr,
                           OnChange=lambda state, image_name=image_name: {
                               settings.set("image", f"{variables.log_path}:{image_name}:swap_rgb_bgr", state),
                               getattr(__import__(__name__), "images").__setitem__(image_name, {"data": images[image_name]["data"], "swap_rgb_bgr": state})
                           })

            if swap_rgb_bgr:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            width = (variables.graph_ui_position_x2 - variables.graph_ui_position_x1)
            height = (variables.graph_ui_position_y2 - variables.graph_ui_position_y1)
            width_height_ratio = image.shape[1] / image.shape[0] - width / height

            if width_height_ratio > 0:
                X1 = variables.graph_ui_position_x1
                Y1 = variables.graph_ui_position_y1 + ((height - (width / (image.shape[1] / image.shape[0]))) / 2)
                X2 = variables.graph_ui_position_x2
                Y2 = variables.graph_ui_position_y2 - ((height - (width / (image.shape[1] / image.shape[0]))) / 2)
            else:
                X1 = variables.graph_ui_position_x1 + height * abs(width_height_ratio / 2)
                Y1 = variables.graph_ui_position_y1
                X2 = variables.graph_ui_position_x2 - height * abs(width_height_ratio / 2)
                Y2 = variables.graph_ui_position_y2

            ImageUI.Image(Image=image,
                            X1=X1,
                            Y1=Y1,
                            X2=X2,
                            Y2=Y2,
                            ID=f"image_{image_name}",
                            RoundCorners=10)

    except:
        crash_report("Image - Error in function update", str(traceback.format_exc()))