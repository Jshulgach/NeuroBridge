import os
import cv2
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

class DINODetection:
    """ Handles object tracking using Grounding DINO. """
    def __init__(self, dino_model_id="IDEA-Research/grounding-dino-tiny"):
        self.grounding_dino_id = dino_model_id

        # Set up device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        torch.autocast(device_type=self.device, dtype=torch.bfloat16).__enter__()
        if self.device == "cuda" and torch.cuda.get_device_properties(0).major >= 0:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
        torch.inference_mode()

        # Set up Grounding DINO model
        dino_path = os.path.join("models","grounding_dino")
        self.processor = AutoProcessor.from_pretrained(self.grounding_dino_id, cache_dir=dino_path)
        self.grounding_model = AutoModelForZeroShotObjectDetection.from_pretrained(self.grounding_dino_id,
                                                                                   cache_dir=dino_path).to(self.device)

    def detect_objects(self, frame, prompt="bottle"):
        """Detects objects in a given frame using Grounding DINO."""
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.grounding_model(**inputs)
        results = self.processor.post_process_grounded_object_detection(
            outputs, inputs.input_ids, box_threshold=0.4, text_threshold=0.4, target_sizes=[image.size[::-1]]
        )
        input_boxes = results[0]["boxes"].cpu().numpy()
        confidences = results[0]["scores"].cpu().numpy().to_list()
        class_names = results[0]["labels"]
        return input_boxes, confidences, class_names

    def annotate_frame(self, frame, boxes, confidences, class_names):
        """Annotates the frame with bounding boxes and object labels."""
        for box, confidence, class_name in zip(boxes, confidences, class_names):
            box = box.astype(int)
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
            cv2.putText(frame, f"{class_name} {confidence:.2f}", (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame

class AICamera:
    """ Manages camera streaming and object detection """

    def __init__(self, camera_id=0, detector_id="IDEA-Research/grounding-dino-tiny"):
        self.camera_id = camera_id
        self.cap = None
        self.running = False

        if detector_id == "IDEA-Research/grounding-dino-tiny":
            self.detector = DINODetection()
        else:
            raise ValueError("Invalid detector ID")

    def start(self):
        """ Starts the camera stream """
        self.cap = cv2.VideoCapture(self.camera_id)
        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                cv2.imshow("Camera Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.stop()

    def stop(self):
        """ Stops the camera stream """
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def detect_objects(self, prompt="bottle"):
        """ Runs object detection """
        print(f"Detecting objects: {prompt}")
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                boxes, confidences, class_names = self.detector.detect_objects(frame, prompt)
                print(f"Detected: {class_names}")

