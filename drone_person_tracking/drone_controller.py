from pynput import keyboard

class DroneController:
    # Handles drone control commands via keyboard input.
    def __init__(self, drone):
        self.drone = drone
        self.running = True

    def on_press(self, key):
        # Handle key press events to control the drone.

        try:
            # l for land
            if key.char == 'l':
                self.drone.land()
            elif key.char == 'q':
                self.running = False
                return False
        except AttributeError:
            # Tab for takeoff
            if key == keyboard.Key.tab:
                self.drone.takeoff()

    def listen(self):
        # Start listening to keyboard events.
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()
