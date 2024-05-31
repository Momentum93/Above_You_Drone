import threading
import tellopy
from drone_controller import DroneController
from video_streaming import start_video_stream

def main():
    # Connect to the drone
    drone = tellopy.Tello()
    drone.connect()

    # Create and start the control thread
    drone_controller = DroneController(drone)
    control_thread = threading.Thread(target=drone_controller.listen)
    control_thread.start()

    # Start video streaming
    start_video_stream(drone, drone_controller)

    # Ensure proper shutdown
    control_thread.join()

if __name__ == "__main__":
    main()
