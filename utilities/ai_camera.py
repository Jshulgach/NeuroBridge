import cv2
from utilities.dino_stream import DINODetection

class AICamera:
    """ Manages camera streaming and object detection """

    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        self.running = False
        self.detector = DINODetection()

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
