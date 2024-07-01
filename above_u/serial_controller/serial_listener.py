import base64
import cv2
import serial


class SerialListener:
    def __init__(self, port, baud_rate, drone_controller, video_processor):
        """
        Initialize the SerialListener with the given parameters.

        Args:
            port (str): The serial port to listen to (e.g., '/dev/ttyUSB0').
            baud_rate (int): The baud rate for the serial communication.
            drone_controller (DroneController): An instance of the DroneController class.
            video_processor (VideoProcessor): An instance of the VideoProcessor class.
        """
        self.serial_port = None
        self.drone_controller = drone_controller
        self.video_processor = video_processor

        try:
            self.serial_port = serial.Serial(port, baud_rate)
        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")

    def listen(self):
        """
        Continuously listen for incoming serial commands and handle them.
        """
        if self.serial_port is None:
            print("Serial port not initialized correctly.")
            return

        print("Listening to serial port...\n")
        while True:
            if self.serial_port.in_waiting > 0:
                # Read and handle the incoming command
                try:
                    command = self.serial_port.readline().strip().decode('utf-8')
                    self.handle_command(command)
                except UnicodeDecodeError as e:
                    print(f"Error decoding command: {e}")
                except serial.SerialException as e:
                    print(f"Error opening serial port {e}")

    def handle_command(self, command):
        """
        Handle the incoming command and perform the corresponding action.

        Args:
            command (str): The command received via the serial port.
        """
        print("Serial port command: ", command)
        
        if command == "<COMMAND>TAKEOFF": #'takeoff':
            print("Taking off...")
            self.drone_controller.takeoff()
            
        elif command == '<COMMAND>LAND': #'land':
            print("Landing...")
            self.drone_controller.land()

        elif command == '<COMMAND>START_TRACK': #'start_track':
            print("Starting tracking...")
            self.video_processor.start_tracking()

        elif command == '<COMMAND>STOP_TRACK': #'stop_track':
            print("Stopping tracking...")
            self.video_processor.stop_tracking()

        elif command == '<COMMAND>CALIBRATE': #'calibrate':
            print("Calibrating colors...")
            self.video_processor.calibrate_colors()

        elif command == '<IMAGE>REQUEST_IMAGE':
            print("Send image...")
            self.send_image()

    def send_image(self):
        frame = self.video_processor.get_current_frame()
        if frame is not None:
            # Encode the image as jpg
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                # Convert buffer to base64 string
                data = base64.b64encode(buffer).decode('utf-8')
                # Format as a string with "<IMAGE>..."
                formatted_data = "<IMAGE>" + data
                # Send the image as bytes
                self.serial_port.write(formatted_data.encode('utf-8'))
            else:
                print("Failed to encode frame to JPEG.")
        else:
            print("No frame available to send.")
