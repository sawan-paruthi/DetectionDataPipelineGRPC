import os
import sys
import torch
from detectors.Yolo import Yolo
from detectors.TorchVisionDetection import TorchVisionDetection
from detectors.TensorFlowDetection import TensorFlowDetection


trackers_path = os.path.join(os.path.dirname(__file__), 'trackers')
sys.path.append(trackers_path)

class ObjectProcessor:
    def __init__(self, prefix):
        self.model = None  
        self.detector = None
        self.prefix = prefix

    def load_model(self, model):
        print(f"model name in object processor is {model}")
        self.detector = model


    def detect_objects(self, image_path):
        print(f"detector inside objectprocessor {self.detector}")
        
        # return detections
        if self.detector[:9]==f"{self.prefix}-rtdetr":
            print("inside if")
            model_path = os.path.join("checkpoints", "yolo", self.detector)
            Model = Yolo(model_path)
            detections = Model.detect(image_path)
            return detections
        
        if self.detector[:7]==f"{self.prefix}-yolo":
            print("inside if")
            model_path = os.path.join("checkpoints", "yolo", self.detector)
            Model = Yolo(model_path)
            detections = Model.detect(image_path)
            return detections
        
        if self.detector[:5] == f"{self.prefix}-tf":
            print("model Name")
            print(self.detector[2:])
            # checkpoint_path= model_path = os.path.join("checkpoints", "tensorflow", self.detector)
            detector = TensorFlowDetection(self.detector[2:], confidence_threshold=0.5)
            detections = detector.detect(image_path)
            return detections        


        if self.detector[:5] == f"{self.prefix}-tv":
            print("model Name")
            print(self.detector[2:])
            checkpoint_path = os.path.join("checkpoints", "torchvision", self.detector)
            detector = TorchVisionDetection(self.detector[:-4], checkpoint_path=checkpoint_path, confidence_threshold=0.5)
            detections = detector.detect(image_path)
            return detections

        raise ValueError("Model not available")

    def get_device(self):
    # Check for any GPU backend
        if torch.cuda.is_available():  # NVIDIA GPUs
            return "cuda"
        elif torch.backends.mps.is_available():  # Apple Silicon GPUs
            return "mps"
        elif hasattr(torch.version, "hip") and torch.version.hip:  # AMD GPUs with ROCm
            return "rocm"
        else:
            return "cpu" 