import serial  # Import the pyserial library to handle serial communication


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
            self.serial_port = serial.Serial(port, baud_rate)  # Attempt to initialize the serial port
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
                command = self.serial_port.readline().decode('utf-8').strip()
                self.handle_command(command)

    def handle_command(self, command):
        """
        Handle the incoming command and perform the corresponding action.

        Args:
            command (str): The command received via the serial port.
        """
        print("Serial port command: ", command)
        
        if command == 'takeoff':
            print("Taking off...")
            self.drone_controller.takeoff()
        elif command == 'land':
            print("Landing...")
            self.drone_controller.land()

        elif command == 'start_track':
            print("Starting tracking...")
            self.video_processor.start_tracking()
        elif command == 'stop_track':
            print("Stopping tracking...")
            self.video_processor.stop_tracking()

        elif command == 'calibrate':
            print("Calibrating colors...")
            self.video_processor.calibrate_colors()
