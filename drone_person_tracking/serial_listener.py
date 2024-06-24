class SerialListener:
    def __init__(self, port, baud_rate, drone_controller, video_processor):
        self.serial_port = port
        self.baud_rate = baud_rate
        self.drone_controller = drone_controller
        self.video_processor = video_processor

    def listen(self):
        while True:
            if self.serial_port.in_waiting > 0:
                command = self.serial_port.readline().decode('utf-8').strip()
                self.handle_command(command)

    def handle_command(self, command):
        if command == 'takeoff':
            self.drone_controller.takeoff()
        elif command == 'land':
            self.drone_controller.land()
        elif command == 'start_track':
            self.video_processor.start_tracking()
        elif command == 'stop_track':
            self.video_processor.stop_tracking()
        elif command == 'calibrate':
            self.video_processor.calibrate()
            