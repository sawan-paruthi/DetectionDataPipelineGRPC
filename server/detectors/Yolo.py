from ultralytics import YOLO

class Yolo:
    def __init__(self, model_path, confidence_threshold=0.5):
        print(f"model path is {model_path}")
        self.model = YOLO(model_path)
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
                        "class_name": self.class_names[int(d[5])]  #class name
                    }
                    for d in filtered_dets if d[4] > self.confidence_threshold
                ]

                detections.append({
                    'detections': frame_detections
                })

        return detections

def main():
    model_path = "best.pt"  
    image_path = "test.jpg"     

    yolo_detector = Yolo(model_path)
    detections = yolo_detector.detect(image_path)

    print("Detections:", detections)

if __name__ == "__main__":
    main()
