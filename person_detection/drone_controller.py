import tellopy
from pynput import keyboard

class DroneController:
    # Handles drone control commands via keyboard input.
    def __init__(self, drone):
        self.drone = drone
        self.running = True

    def on_press(self, key):
        # Handle key press events to control the drone.
        try:
            if key.char == 'w':
                self.drone.forward(10)
            elif key.char == 's':
                self.drone.backward(10)
            elif key.char == 'a':
                self.drone.left(10)
            elif key.char == 'd':
                self.drone.right(10)
            elif key.char == 'l':
                self.drone.land()
            elif key.char == 'q':
                self.running = False
                return False
        except AttributeError:
            if key == keyboard.Key.tab:
                self.drone.takeoff()

    def listen(self):
        # Start listening to keyboard events.
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()
