import threading
from drone_controller import DroneController
from video_processor import VideoProcessor


class Main:
    def __init__(self):
        self.drone_controller = DroneController()
        self.video_processor = VideoProcessor(self.drone_controller)

    def start(self):
        # Connect to drone
        self.drone_controller.connect()

        # Drone control thread
        control_thread = threading.Thread(target=self.drone_controller.start_listening)
        control_thread.start()

        # Start video processing in the main thread to ensure cv2.imshow works
        self.video_processor.start_video_stream()

        control_thread.join()


if __name__ == "__main__":
    main_controller = Main()
    main_controller.start()
