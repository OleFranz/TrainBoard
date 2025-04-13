from CrashReport import CrashReport
import traceback
import Variables
import ImageUI


def Update():
    try:

        if Variables.Tab != "Models":
            return

        for i, ModelName in enumerate(Variables.Models):
            ModelData = Variables.Models[ModelName]["Data"][0]
            TotalParameters = ModelData["TotalParameters"]
            TrainableParameters = ModelData["TrainableParameters"]
            NonTrainableParameters = ModelData["NonTrainableParameters"]
            ModelSize = ModelData["ModelSize"]

            ImageUI.Label(Text=f"{ModelName}\n> Total Parameters: {TotalParameters:,}\n> Trainable Parameters: {TrainableParameters:,}\n> Non-Trainable Parameters: {NonTrainableParameters:,}\n> Model Size: {f'{round(ModelSize, 2):,}'}MB".replace(",", "#").replace(".", ",").replace("#", "."),
                          X1=Variables.GraphUIPositionX1 + 10,
                          Y1=Variables.GraphUIPositionY1 + 10 + 100 * i,
                          X2=Variables.GraphUIPositionX2 - 10,
                          Y2=Variables.GraphUIPositionY1 + 10 + 100 * (i + 1),
                          ID=f"ModelLabel{ModelName}",
                          Align="Left",
                          FontSize=15)

    except:
        CrashReport("Model - Error in function Update.", str(traceback.format_exc()))