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
    RetinaNet_ResNet50_FPN_V2_Weights,
    SSD300_VGG16_Weights,
    SSDLite320_MobileNet_V3_Large_Weights,
    FCOS_ResNet50_FPN_Weights,
)


class TorchVisionDetection:
    def __init__(self, model_name, checkpoint_path,  confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold
        self.checkpoint_path = checkpoint_path
        self.transform = transforms.Compose([
            transforms.ToTensor()
        ])
        self.model = self.load_model(model_name)
        self.model.eval()


    def load_model(self, model_name):
        checkpoint = torch.load(self.checkpoint_path, map_location=torch.device('cpu'))

        if model_name.startswith("fasterrcnn"):
            # Infer num_classes from checkpoint
            weight_shape = checkpoint['roi_heads.box_predictor.cls_score.weight'].shape[0]
            model = {
                "fasterrcnn_resnet50": models.detection.fasterrcnn_resnet50_fpn,
                "fasterrcnn_mobilenet_v3_large": models.detection.fasterrcnn_mobilenet_v3_large_fpn,
                "fasterrcnn_resnet50_v2": models.detection.fasterrcnn_resnet50_fpn_v2
            }[model_name](weights=None)

            in_features = model.roi_heads.box_predictor.cls_score.in_features
            model.roi_heads.box_predictor = FastRCNNPredictor(in_features, weight_shape)

        elif model_name.startswith("retinanet"):
            # RetinaNet uses 9 anchors per location, so:
            cls_weight_shape = checkpoint['head.classification_head.cls_logits.weight'].shape[0]
            num_classes = cls_weight_shape // 9
            model = {
                "retinanet_resnet50": models.detection.retinanet_resnet50_fpn,
                "retinanet_resnet50_v2": models.detection.retinanet_resnet50_fpn_v2
            }[model_name](weights=None, num_classes=num_classes)

        elif model_name == "ssd300_vgg16":
            # SSD: usually 21 or 91 classes including background
            model = models.detection.ssd300_vgg16(weights=None)
            # SSD head replacement is non-trivial and not shown here

        elif model_name == "ssdlite320_mobilenet_v3_large":
            model = models.detection.ssdlite320_mobilenet_v3_large(weights=None)

        elif model_name == "fcos_resnet50":
            cls_weight_shape = checkpoint['head.classification_head.cls_logits.weight'].shape[0]
            model = models.detection.fcos_resnet50_fpn(weights=None, num_classes=cls_weight_shape)

        else:
            raise ValueError(f"Model {model_name} not supported!")

        # Load checkpoint now (already loaded above)
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
    img_path = "C:\\Users\\12514\\Desktop\\DetectionDataPipelineGRPC\\server\\inbound\\received_image.jpg"
    modelname = "fcos_resnet50.pth"
    checkpoint = "C:\\Users\\12514\\Desktop\\DetectionDataPipelineGRPC\\server\\checkpoints\\torchvision\\fcos_resnet50.pth"
    detector = TorchVisionDetection(modelname[:-4], checkpoint_path=checkpoint, confidence_threshold=0.5)
    detections = detector.detect(img_path)
    print(len(detections))
    print(detections)




