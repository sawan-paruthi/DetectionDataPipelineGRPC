import cv2
import numpy as np
import tensorflow_hub as hub
import tensorflow as tf

class TensorFlowDetection:
    def __init__(self, model_name, confidence_threshold=0.5):
        # self.model = hub.load(model_name)
        self.model = self.load_model(model_name)
        self.confidence_threshold = confidence_threshold

    def load_model(self, model_name):
        if model_name=="efficientdetd0":
            return hub.load("https://tfhub.dev/tensorflow/efficientdet/d0/1")
        
        if model_name=="efficientdetd1":
            return hub.load("https://tfhub.dev/tensorflow/efficientdet/d1/1")
        
        if model_name=="efficientdetd2":
            return hub.load("https://tfhub.dev/tensorflow/efficientdet/d2/1")
        
        if model_name=="efficientdetd3":
            return hub.load("https://tfhub.dev/tensorflow/efficientdet/d3/1")
        
        if model_name=="efficientdetd4":
            return hub.load("https://tfhub.dev/tensorflow/efficientdet/d4/1")
        
        if model_name=="efficientdetd5":
            return hub.load("https://tfhub.dev/tensorflow/efficientdet/d5/1")
        
        if model_name=="faster-rcnn-restnet50":
            return hub.load("https://tfhub.dev/tensorflow/faster_rcnn/resnet50_v1_640x640/1")
        
        if model_name=="faster-rcnn-restnet-v2":
            return hub.load("https://tfhub.dev/tensorflow/faster_rcnn/inception_resnet_v2_640x640/1")
        
        if model_name=="faster-rcnn-restnet-101":
            return hub.load("https://tfhub.dev/tensorflow/faster_rcnn/resnet101_v1_640x640/1")
        
        if model_name=="retinanet":
            return hub.load("https://tfhub.dev/tensorflow/retinanet/resnet50_v1_fpn_640x640/1")
        
        if model_name=="ssdmobilenetv2":
            return hub.load("https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2")

    def preprocess_frame(self, frame):
        """Preprocess the input frame for the model."""
        # Convert the frame to a tensor of dtype uint8 and add a batch dimension
        input_tensor = tf.convert_to_tensor(frame, dtype=tf.uint8)[tf.newaxis, ...]
        return input_tensor

    def detect(self, video_path):
        """Run object detection on the video and return detections in the desired format."""
        cap = cv2.VideoCapture(video_path)
        frame_detections = []

        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to RGB (EfficientDet expects RGB format)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Preprocess the frame
            input_tensor = self.preprocess_frame(rgb_frame)

            # Run inference
            detections = self.model(input_tensor)

            # Extract results
            boxes = detections["detection_boxes"].numpy()[0]  # Normalized bounding boxes
            scores = detections["detection_scores"].numpy()[0]  # Confidence scores
            class_ids = detections["detection_classes"].numpy()[0]  # Class IDs

            # Filter and format detections for the current frame
            height, width, _ = frame.shape
            filtered_detections = [
                [
                    int(box[1] * width),  # x1
                    int(box[0] * height),  # y1
                    int(box[3] * width),  # x2
                    int(box[2] * height),  # y2
                    score  # confidence
                ]
                for box, score in zip(boxes, scores) if score > self.confidence_threshold
            ]

            frame_detections.append({
                'frame': frame_idx + 1,
                'detections': filtered_detections
            })

            frame_idx += 1

        cap.release()
        return frame_detections


# Example Usage
if __name__ == "__main__":
    model_name = "faster-rcnn-restnet50"
    video_path = "received_video.mp4"

    detector = TensorFlowDetection(model_name, confidence_threshold=0.5)
    detections = detector.detect(video_path)

    print(detections)

    # Print detections
    # for frame_info in detections:
    #     print(f"Frame {frame_info['frame']}:")
    #     for det in frame_info['detections']:
    #         print(f"  Bounding Box: {det[:4]}, Confidence: {det[4]:.2f}")
