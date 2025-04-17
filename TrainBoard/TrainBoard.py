import pickle
import numpy
import torch
import time
import cv2
import os


class Create:
    def __init__(self, LogPath:str):
        """
        Create a new trainboard log

        Parameters
        ----------
        LogPath : str
            The path to the log
        """
        self._log_path = os.path.abspath(LogPath)
        self._graphs = {}
        self._images = {}
        self._models = {}
        os.makedirs(self._log_path, exist_ok=True)
        for file in os.listdir(self._log_path):
            if file.startswith("graph") or file.startswith("image") or file.startswith("model"):
                try: os.remove(os.path.join(self._log_path, file))
                except: pass


    def add_graph(self, name:str, value:float, epoch:int):
        """
        Add a graph to the trainboard log

        Parameters
        ----------
        name : str
            The name of the graph to add the value to
        value : float
            The new value to add (y-axis)
        epoch : int
            The epoch to add the value to (x-axis)

        Returns
        -------
        None
        """
        epoch_name = f"{name}#{epoch}"
        if epoch_name not in self._graphs:
            self._graphs[epoch_name] = os.path.join(self._log_path, f"graph{len(self._graphs)}.pkl")

        with open(self._graphs[epoch_name], "wb") as file:
            pickle.dump({"name": name,
                         "value": value,
                         "epoch": epoch,
                         "time": time.perf_counter()},
                        file)


    def add_image(self, name:str, image:numpy.ndarray | torch.Tensor, epoch:int):
        """
        Add an image to the trainboard log

        Parameters
        ----------
        name : str
            The name of the image to add
        image : numpy.ndarray | torch.Tensor
            The image to add, can be numpy.ndarray or torch.Tensor
        epoch : int
            The epoch to add the image to

        Returns
        -------
        None"""
        epoch_name = f"{name}#{epoch}"
        if epoch_name not in self._images:
            self._images[epoch_name] = os.path.join(self._log_path, f"image{len(self._images)}.pkl")

        if isinstance(image, numpy.ndarray) and image.dtype == numpy.uint8:
            if image.shape[2] == 1: image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        elif isinstance(image, numpy.ndarray) and image.dtype != numpy.uint8:
            image = numpy.clip(image, 0, 1)
            image = (image * 255).astype(numpy.uint8)
            if image.shape[2] == 1: image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        elif isinstance(image, torch.Tensor) and image.dtype == torch.float32:
            if len(image.shape) == 2: image = image.unsqueeze(0).cpu().detach().numpy().transpose(1, 2, 0)
            elif len(image.shape) == 3: image = image.cpu().detach().numpy().transpose(1, 2, 0)
            elif len(image.shape) == 4: image = image[0].cpu().detach().numpy().transpose(1, 2, 0)
            image = numpy.clip(image, 0, 1)
            image = (image * 255).astype(numpy.uint8)
            if image.shape[2] == 1: image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        elif isinstance(image, torch.Tensor) and image.dtype != torch.float32:
            image = image.to(torch.float32)
            if len(image.shape) == 2: image = image.unsqueeze(0).cpu().detach().numpy().transpose(1, 2, 0)
            elif len(image.shape) == 3: image = image.cpu().detach().numpy().transpose(1, 2, 0)
            elif len(image.shape) == 4: image = image[0].cpu().detach().numpy().transpose(1, 2, 0)
            image = numpy.clip(image, 0, 1)
            image = (image * 255).astype(numpy.uint8)
            if image.shape[2] == 1: image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        with open(self._images[epoch_name], "wb") as file:
            pickle.dump({"name": name,
                         "image": image,
                         "epoch": epoch,
                         "time": time.perf_counter()},
                        file)


    def add_model(self, name:str, model:torch.nn.Module):
        """
        Add a model to the trainboard log

        Parameters
        ----------
        name : str
            The name of the model
        model : torch.nn.Module
            The PyTorch model

        Returns
        -------
        dict
            A dictionary containing the total parameters, trainable parameters, non trainable parameters and model size in MB
        """
        if name not in self._models:
            self._models[name] = os.path.join(self._log_path, f"model{len(self._models)}.pkl")

        total_parameters = 0
        for parameter in model.parameters():
            parameter_count = 1
            for dim in parameter.size():
                parameter_count *= int(dim)
            total_parameters += parameter_count
        trainable_parameters = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
        non_trainable_parameters = total_parameters - trainable_parameters
        bytes_per_parameter = next(model.parameters()).element_size()
        model_size = (total_parameters * bytes_per_parameter) / (1024 ** 2)

        with open(self._models[name], "wb") as file:
            pickle.dump({"name": name,
                         "total_parameters": total_parameters,
                         "trainable_parameters": trainable_parameters,
                         "non_trainable_parameters": non_trainable_parameters,
                         "model_size": model_size,
                         "time": time.perf_counter()},
                        file)

        return {"total_parameters": total_parameters, "trainable_parameters": trainable_parameters, "non_trainable_parameters": non_trainable_parameters, "model_size": model_size}


    def clear_graph(self, name:str):
        """
        Clear the trainboard log of a graph

        Parameters
        ----------
        name : str
            The name of the graph

        Returns
        -------
        None
        """
        valid_name = False
        for file in os.listdir(self._log_path):
            if file.startswith("graph"):
                try:
                    with open(os.path.join(self._log_path, file), "rb") as f:
                        data = pickle.load(f)
                    if "name" in data and data["name"] == name:
                        valid_name = True
                        os.remove(os.path.join(self._log_path, file))
                except: pass
        if valid_name == False:
            raise ValueError(f"Graph with name {name} not found")


    def clear_image(self, name:str):
        """
        Clear the trainboard log of an image

        Parameters
        ----------
        name : str
            The name of the image

        Returns
        -------
        None
        """
        valid_name = False
        for file in os.listdir(self._log_path):
            if file.startswith("image"):
                try:
                    with open(os.path.join(self._log_path, file), "rb") as f:
                        data = pickle.load(f)
                    if "name" in data and data["name"] == name:
                        valid_name = True
                        os.remove(os.path.join(self._log_path, file))
                except: pass
        if valid_name == False:
            raise ValueError(f"Image with name {name} not found")


    def clear_model(self, name:str):
        """
        Clear the trainboard log of a model

        Parameters
        ----------
        name : str
            The name of the model

        Returns
        -------
        None
        """
        valid_name = False
        for file in os.listdir(self._log_path):
            if file.startswith("model"):
                try:
                    with open(os.path.join(self._log_path, file), "rb") as f:
                        data = pickle.load(f)
                    if "name" in data and data["name"] == name:
                        valid_name = True
                        os.remove(os.path.join(self._log_path, file))
                except: pass
        if valid_name == False:
            raise ValueError(f"Model with name {name} not found")


    def clear_all(self):
        """
        Clear the entire trainboard log

        Returns
        -------
        None
        """
        for file in os.listdir(self._log_path):
            if file.startswith("graph") or file.startswith("image") or file.startswith("model"):
                try: os.remove(os.path.join(self._log_path, file))
                except: pass