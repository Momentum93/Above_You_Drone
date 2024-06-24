# Drone Person Tracking

This project uses MediaPipe Pose estimation to control a Tello drone. The drone's movements are adjusted based on the detected human pose, ensuring the person remains in the center of the frame, at a desired height, and a specific distance from the drone.

## Project Structure
### Main
- `main.py`: Contains main function to launch the program using multithreading.
- `serial_listener.py`: Listens for commands sent over a serial port and delegates them to the appropriate handler methods in DroneController and VideoProcessor.
### Drone Control
- `drone_controller.py`: Contains the DroneController class for handling keyboard controls.
- `drone_controller.py`: Handles the drone movement to track the person in the frame.
### Video Processing
- `video_streaming.py`: Shows the video stream and startes processing of frames.
- `pose_estimation.py`: Contains functions for pose estimation and torso size calculation.
- `person_color_detection.py`: Allows for tracking of a specific person by detecing the color of their torso after calibration.

## Usage

1. **Start the video stream:** Run the `main.py` script to start the video stream and control the drone based on pose estimation.
2. **Launch the drone:** Press Tab to let the drone take off.

### Keyboard Controls:

- **W**: Move forward
- **S**: Move backward
- **A**: Move left
- **D**: Move right
- **L**: Land
- **Tab**: Take off
- **Q**: Quit

## How It Works

- **Pose Estimation:** Uses MediaPipe to detect human poses in the video stream.
- **Drone Adjustments:**
  - **Height Control:** Keeps the shoulders in the top third of the frame.
  - **Forward/Backward Control:** Maintains a specific torso size in the frame.
  - **Yaw Control:** Keeps the person centered horizontally in the frame.
- **Person Color Detection:** Uses MediaPipe to detect torso and its colors.