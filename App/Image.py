from CrashReport import CrashReport
import traceback
import Variables
import ImageUI
import numpy
import cv2


def Update():
    try:

        if Variables.Tab != "Images":
            return

        for i, ImageData in enumerate(Variables.ImageContent):
            ImageName = ImageData[0]
            if Variables.SelectedImage == ImageName:
                Index = next((Index for (Index, EpochData) in enumerate(ImageData[1]) if EpochData[1] == Variables.SelectedImageEpoch), None)
                if Index != None:
                    Image = ImageData[1][Index][0]
                    Epoch = ImageData[1][Index][1]
                    SwapRGBBGR = Variables.Images[ImageName]["SwapRGBBGR"]

                    if SwapRGBBGR:
                        Image = cv2.cvtColor(Image, cv2.COLOR_BGR2RGB)

                    Width = (Variables.GraphUIPositionX2 - Variables.GraphUIPositionX1)
                    Height = (Variables.GraphUIPositionY2 - Variables.GraphUIPositionY1)
                    WidthHeightRatio = Image.shape[1] / Image.shape[0] - Width / Height

                    if WidthHeightRatio > 0:
                        X1 = Variables.GraphUIPositionX1
                        Y1 = Variables.GraphUIPositionY1 + ((Height - (Width / (Image.shape[1] / Image.shape[0]))) / 2)
                        X2 = Variables.GraphUIPositionX2
                        Y2 = Variables.GraphUIPositionY2 - ((Height - (Width / (Image.shape[1] / Image.shape[0]))) / 2)
                    else:
                        X1 = Variables.GraphUIPositionX1 + Height * abs(WidthHeightRatio / 2)
                        Y1 = Variables.GraphUIPositionY1
                        X2 = Variables.GraphUIPositionX2 - Height * abs(WidthHeightRatio / 2)
                        Y2 = Variables.GraphUIPositionY2

                    ImageUI.Image(Image=Image,
                                  X1=X1,
                                  Y1=Y1,
                                  X2=X2,
                                  Y2=Y2,
                                  ID=f"Image{i}",
                                  RoundCorners=10)

    except:
        CrashReport("Image - Error in function Update.", str(traceback.format_exc()))