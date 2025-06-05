from ultralytics import RTDETR


class RTDETRDetector:
    def __init__(self, model_path, confidence_threshold=0.5):
        print(f"Model path is: {model_path}")
        self.model = RTDETR(model_path)
        self.class_names = self.model.names
        self.confidence_threshold = confidence_threshold

    def detect(self, img_path):
        results = self.model.predict(img_path, conf=self.confidence_threshold)
        detections = []

        for result in results:
            if result.boxes is not None:
                filtered_dets = result.boxes.data.cpu().numpy()

                frame_detections = [
                    {
                        "bbox": [d[0], d[1], d[2], d[3]],  # Bounding box [x1, y1, x2, y2]
                        "confidence": d[4],               # Confidence score
                        "class_id": int(d[5]),            # Class ID
                        "class_name": self.class_names[int(d[5])]  # Class name
                    }
                    for d in filtered_dets if d[4] > self.confidence_threshold
                ]

                detections.append({
                    'detections': frame_detections
                })

        return detections


def main():
    model_path = "C:\\Users\\Krishna\\Downloads\\LPD_ServiceGRPC\\server\\checkpoints\\yolo\\lp-rtdetr-l.pt"
    image_path = "C:\\Users\\Krishna\\Downloads\\LPD_ServiceGRPC\\server\\received_image.jpg"

    detector = RTDETRDetector(model_path)
    detections = detector.detect(image_path)

    print("Detections:", detections)


if __name__ == "__main__":
    main()
