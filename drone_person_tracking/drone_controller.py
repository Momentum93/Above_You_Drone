import tellopy
from pynput import keyboard


class DroneController:
    def __init__(self):
        self.drone = tellopy.Tello()
        self.running = True

    def connect(self):
        self.drone.connect()

    def takeoff(self):
        self.drone.takeoff()

    def land(self):
        self.drone.land()

    def quit(self):
        self.drone.quit()

    def on_key_press(self, key):
        try:
            if key.char == 'l':
                self.land()
            elif key.char == 'q':
                self.running = False
                return False
        except AttributeError:
            if key == keyboard.Key.tab:
                self.takeoff()

    def start_listening(self):
        with keyboard.Listener(on_press=self.on_key_press) as listener:
            listener.join()
