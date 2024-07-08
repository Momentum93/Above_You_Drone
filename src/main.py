import threading

from drone_controller import DroneController
from serial_controller import SerialListener
from video_processing import VideoProcessor

# Serial port configuration
SERIAL_PORT = '/dev/cu.usbserial-10'
BAUD_RATE = 9600


class Main:
    def __init__(self):
        self.drone_controller = DroneController()
        self.video_processor = VideoProcessor(self.drone_controller)
        self.serial_listener = SerialListener(SERIAL_PORT, BAUD_RATE,
                                              self.drone_controller, self.video_processor)

    def start(self):
        # Connect to drone
        self.drone_controller.connect()

        # Drone control thread
        control_thread = threading.Thread(target=self.drone_controller.start_listening)
        control_thread.start()

        # Serial listener thread
        serial_thread = threading.Thread(target=self.serial_listener.listen)
        serial_thread.start()

        # Start video processing in the main thread to ensure cv2.imshow works
        self.video_processor.start_video_stream()

        control_thread.join()
        serial_thread.join()


if __name__ == "__main__":
    main_controller = Main()
    main_controller.start()
