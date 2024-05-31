# Drone Pose Estimation and Control

This project uses MediaPipe Pose estimation to control a Tello drone. The drone's movements are adjusted based on the detected human pose, ensuring the person remains in the center of the frame, at a desired height, and a specific distance from the drone.

## Project Structure

- `pose_estimation.py`: Contains functions for pose estimation and torso size calculation.
- `drone_controller.py`: Contains the `DroneController` class for handling keyboard controls.
- `video_streaming.py`: Main script that starts the video stream, processes the frames for pose detection, and adjusts the drone's position.

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

## File Descriptions

### pose_estimation.py
#### Functions:
- `calculate_torso_size(landmarks)`: Calculates the size of the torso based on pose landmarks.
- `mp_drawing` and `mp_pose`: MediaPipe drawing utilities and pose estimator initialization.

### drone_controller.py
#### Classes:
- `DroneController`: Handles keyboard input to control the drone.

### video_streaming.py
#### Functions:
- `adjust_drone(drone, avg_shoulder_y, torso_size, avg_shoulder_x)`: Adjusts the drone's position based on pose data.
- `start_video_stream(drone, drone_controller)`: Main function to start video streaming, process frames, and adjust the drone.

## How It Works

- **Pose Estimation:** Uses MediaPipe to detect human poses in the video stream.
- **Drone Adjustments:**
  - **Height Control:** Keeps the shoulders in the top third of the frame.
  - **Forward/Backward Control:** Maintains a specific torso size in the frame.
  - **Horizontal Control:** Keeps the person centered horizontally in the frame.
  - **Proportional Control:** Adjustments are made using proportional control constants to ensure smooth movements.
