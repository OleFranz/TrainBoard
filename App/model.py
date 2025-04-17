from crashreport import crash_report
import traceback
import variables
import ImageUI


models = {}


def update():
    try:

        if variables.tab != "Models":
            return

        for i, model_name in enumerate(models):
            total_parameters = models[model_name]["total_parameters"]
            trainable_parameters = models[model_name]["trainable_parameters"]
            non_trainable_parameters = models[model_name]["non_trainable_parameters"]
            model_size = models[model_name]["model_size"]

            ImageUI.Label(Text=f"{model_name}\n> Total Parameters: {total_parameters:,}\n> Trainable Parameters: {trainable_parameters:,}\n> Non-Trainable Parameters: {non_trainable_parameters:,}\n> Model Size: {f'{round(model_size, 2):,}'}MB".replace(",", "#").replace(".", ",").replace("#", "."),
                          X1=variables.graph_ui_position_x1,
                          Y1=variables.graph_ui_position_y1 + 100 * i,
                          X2=variables.graph_ui_position_x2 - 10,
                          Y2=variables.graph_ui_position_y1 + 100 * (i + 1),
                          ID=f"model_label_{model_name}",
                          Align="Left",
                          FontSize=15)

    except:
        crash_report("Model - Error in function update", str(traceback.format_exc()))