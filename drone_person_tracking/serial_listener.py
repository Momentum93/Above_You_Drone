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
        self.serial_port = serial.Serial(port, baud_rate)  # Initialize the serial port
        self.drone_controller = drone_controller  # Store the drone controller instance
        self.video_processor = video_processor  # Store the video processor instance

    def listen(self):
        """
        Continuously listen for incoming serial commands and handle them.
        """
        print("Listening to serial port...")
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
        if command == 'takeoff':
            self.drone_controller.takeoff()
        elif command == 'land':
            self.drone_controller.land()
        elif command == 'start_track':
            self.video_processor.start_tracking()
        elif command == 'stop_track':
            self.video_processor.stop_tracking()
        elif command == 'calibrate':
            self.video_processor.calibrate_colors()
