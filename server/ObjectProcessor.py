import os
import sys
import torch
from detectors.Yolo import Yolo
from detectors.TorchVisionDetection import TorchVisionDetection
from detectors.TensorFlowDetection import TensorFlowDetection
import logging

trackers_path = os.path.join(os.path.dirname(__file__), 'trackers')
sys.path.append(trackers_path)

class ObjectProcessor:
    def __init__(self, prefix):
        self.model = None  
        self.detector = None
        self.prefix = prefix

    def load_model(self, model):
        # print(f"model name in object processor is {model}")
        self.detector = model


    def detect_objects(self, image_path):
        # print(f"detector inside objectprocessor {self.detector}")
        
        # return detections
        if self.detector[:9]==f"{self.prefix}-rtdetr":
            # print("inside if")
            logging.info(f"ObjectProcessor: Model Loaded: {self.detector}")
            abs_path = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(abs_path, "checkpoints", "yolo", self.detector)
            Model = Yolo(model_path)
            detections = Model.detect(image_path)
            return detections
        
        elif self.detector[:7]==f"{self.prefix}-yolo":
            # print("inside if")
            logging.info(f"ObjectProcessor: Model Loaded: {self.detector}")
            abs_path = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(abs_path, "checkpoints", "yolo", self.detector)
            Model = Yolo(model_path)
            detections = Model.detect(image_path)
            return detections
        
        elif self.detector[:5] == f"{self.prefix}-tf":
            logging.info(f"ObjectProcessor: Model Loaded: {self.detector}")
            abs_path = os.path.dirname(os.path.abspath(__file__))
            checkpoint_path= model_path = os.path.join(abs_path, "checkpoints", "tensorflow", self.detector)
            detector = TensorFlowDetection(self.detector[2:], confidence_threshold=0.5)
            detections = detector.detect(image_path)
            return detections        


        elif self.detector[:5] == f"{self.prefix}-tv":
            logging.info(f"ObjectProcessor: Model Loaded: {self.detector}")
            abs_path = os.path.dirname(os.path.abspath(__file__))
            checkpoint_path = os.path.join(abs_path, "checkpoints", "torchvision", self.detector)
            detector = TorchVisionDetection(self.detector[:-4], checkpoint_path=checkpoint_path, confidence_threshold=0.5)
            detections = detector.detect(image_path)
            return detections

        else:
            logging.error("ObjectProcessor: Model not available")
            raise ValueError(f"Model not available : {self.detector}")

