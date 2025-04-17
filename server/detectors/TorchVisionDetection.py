import torch
from torchvision import models, transforms
from PIL import Image
import cv2
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection import (
    FasterRCNN_ResNet50_FPN_Weights,
    FasterRCNN_MobileNet_V3_Large_FPN_Weights,
    FasterRCNN_ResNet50_FPN_V2_Weights,
    RetinaNet_ResNet50_FPN_Weights,
    SSD300_VGG16_Weights,
    SSDLite320_MobileNet_V3_Large_Weights,
    FCOS_ResNet50_FPN_Weights,
)


class TorchVisionDetection:
    def __init__(self, model_name, checkpoint_path, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold
        self.checkpoint_path = checkpoint_path
        self.transform = transforms.Compose([
            transforms.ToTensor()
        ])
        self.num_classes = 2  # Background + License Plate
        self.model = self.load_model(model_name)
        self.model.eval()

    def load_model(self, model_name):
        if model_name == "fasterrcnn":
            model = models.detection.fasterrcnn_resnet50_fpn(weights=None)
        elif model_name == "fasterrcnnmobilenet":
            model = models.detection.fasterrcnn_mobilenet_v3_large_fpn(weights=None)
        elif model_name == "fasterrcnnv2":
            model = models.detection.fasterrcnn_resnet50_fpn_v2(weights=None)
        elif model_name == "retinanet":
            model = models.detection.retinanet_resnet50_fpn(weights=None)
        elif model_name == "ssd":
            model = models.detection.ssd300_vgg16(weights=None)
        elif model_name == "ssdlite":
            model = models.detection.ssdlite320_mobilenet_v3_large(weights=None)
        elif model_name == "fcosresnet50":
            model = models.detection.fcos_resnet50_fpn(weights=None)
        else:
            raise ValueError(f"Model {model_name} not supported!")
 
        
        in_features = model.roi_heads.box_predictor.cls_score.in_features
        model.roi_heads.box_predictor = FastRCNNPredictor(in_features, self.num_classes)


        if self.checkpoint_path:
            checkpoint = torch.load(self.checkpoint_path, map_location=torch.device('cpu'))
            #model.load_state_dict(checkpoint, strict=False)
            model.load_state_dict(checkpoint)
            print(f"Fine-tuned weights loaded from {self.checkpoint_path}")

        return model

    def detect(self, img_path):
        # Convert frame to PIL image and apply transformation
        pil_image = Image.open(img_path).convert("RGB")
        input_tensor = self.transform(pil_image).unsqueeze(0)
        # Perform detection
        with torch.no_grad():
            outputs = self.model(input_tensor)[0]
        detections = []
  
        for box, score, label in zip(outputs['boxes'], outputs['scores'], outputs['labels']):
            if score > self.confidence_threshold:
                x1, y1, x2, y2 = box.numpy()
                detections.append([x1, y1, x2, y2, score.item(), int(label)])
                #detections.append([x1, y1, x2, y2, score.item()])
        return detections

if __name__ == "__main__":
    img_path = "testimage.jpg"
    detector = TorchVisionDetection("fasterrcnn", "best.pth", confidence_threshold=0.5)
    detections = detector.detect(img_path)
    print(len(detections))
    print(detections)


