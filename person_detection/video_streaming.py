import cv2
import mediapipe as mp
import numpy as np
import av
import time
from pose_estimation import pose, calculate_torso_size, mp_drawing

# Constants for drone adjustments
TARGET_POSITION_RATIO = 1 / 3  # Top third of the frame
FRAME_HEIGHT = 720  # Assuming a 720p video feed
TARGET_Y_POSITION = FRAME_HEIGHT * TARGET_POSITION_RATIO
THRESHOLD_Y = 40  # Larger allowable threshold to avoid constant adjustments

TARGET_TORSO_SIZE = 0.6
THRESHOLD_TORSO_SIZE = 0.1  # Larger threshold for torso size to avoid constant adjustments

FRAME_WIDTH = 1280  # Assuming a 720p video feed
TARGET_X_POSITION = FRAME_WIDTH / 2
THRESHOLD_X = 50  # Larger allowable threshold to avoid constant adjustments

FILTER_SIZE = 5

P_Y = 0.1  # Proportional constant for height control
P_TORSO = 0.5  # Proportional constant for forward/backward control
P_X = 0.1  # Proportional constant for horizontal control

def adjust_drone(drone, avg_shoulder_y, torso_size, avg_shoulder_x):
    # Adjust drone height using proportional control
    height_error = TARGET_Y_POSITION - avg_shoulder_y
    height_adjustment = int(P_Y * height_error)
    if abs(height_error) > THRESHOLD_Y:
        if height_adjustment > 0:
            drone.up(min(height_adjustment, 100))
        else:
            drone.down(min(-height_adjustment, 100))

    # Adjust drone forward/backward position using proportional control
    torso_error = TARGET_TORSO_SIZE - torso_size
    torso_adjustment = int(P_TORSO * torso_error * 100)
    if abs(torso_error) > THRESHOLD_TORSO_SIZE:
        if torso_adjustment > 0:
            drone.forward(min(torso_adjustment, 100))
        else:
            drone.backward(min(-torso_adjustment, 100))

    # Adjust drone horizontal position using proportional control
    horizontal_error = avg_shoulder_x - TARGET_X_POSITION
    horizontal_adjustment = int(P_X * horizontal_error)
    if abs(horizontal_error) > THRESHOLD_X:
        if horizontal_adjustment > 0:
            drone.clockwise(min(horizontal_adjustment, 100))
        else:
            drone.counter_clockwise(min(-horizontal_adjustment, 100))

def start_video_stream(drone, drone_controller):
    container = av.open(drone.get_video_stream())
    frame_count = 0

    # Variables to store pose landmarks and distance
    pose_landmarks = None
    torso_size = None
    processing_time = 0

    # Initialize lists to store recent measurements for the moving average filter
    recent_shoulder_ys = []
    recent_torso_sizes = []
    recent_shoulder_xs = []

    try:
        while drone_controller.running:
            for frame in container.decode(video=0):
                image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)

                # Convert to RGB
                frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Increment frame count
                frame_count += 1

                # Process every 8th frame
                if frame_count % 8 == 0:
                    # Start timing
                    processing_start_time = time.time()

                    # Process the frame for pose detection
                    pose_results = pose.process(frame_rgb)

                    if pose_results.pose_landmarks:
                        # Extract landmarks
                        pose_landmarks = pose_results.pose_landmarks.landmark

                        # Calculate torso size
                        current_torso_size = calculate_torso_size(pose_landmarks)

                        # Get shoulder y-coordinates
                        left_shoulder_y = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].y * FRAME_HEIGHT
                        right_shoulder_y = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER].y * FRAME_HEIGHT
                        avg_shoulder_y = (left_shoulder_y + right_shoulder_y) / 2

                        # Get shoulder x-coordinates
                        left_shoulder_x = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].x * FRAME_WIDTH
                        right_shoulder_x = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER].x * FRAME_WIDTH
                        avg_shoulder_x = (left_shoulder_x + right_shoulder_x) / 2

                        # Append to recent measurements
                        recent_shoulder_ys.append(avg_shoulder_y)
                        recent_torso_sizes.append(current_torso_size)
                        recent_shoulder_xs.append(avg_shoulder_x)

                        # Maintain the size of the recent measurements list
                        if len(recent_shoulder_ys) > FILTER_SIZE:
                            recent_shoulder_ys.pop(0)
                        if len(recent_torso_sizes) > FILTER_SIZE:
                            recent_torso_sizes.pop(0)
                        if len(recent_shoulder_xs) > FILTER_SIZE:
                            recent_shoulder_xs.pop(0)

                        # Calculate moving average
                        avg_shoulder_y = sum(recent_shoulder_ys) / len(recent_shoulder_ys)
                        torso_size = sum(recent_torso_sizes) / len(recent_torso_sizes)
                        avg_shoulder_x = sum(recent_shoulder_xs) / len(recent_shoulder_xs)

                        # Adjust drone based on current measurements
                        adjust_drone(drone, avg_shoulder_y, torso_size, avg_shoulder_x)

                # Draw the stored pose landmarks and torso size on the frame
                if pose_landmarks:
                    # Draw the torso size on the frame
                    cv2.putText(image, f'Torso Size: {torso_size:.2f}', (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

                    # Draw skeleton on the frame
                    mp_drawing.draw_landmarks(image, pose_results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)

                # Display the frame
                cv2.imshow('Output', image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    drone_controller.running = False
                    break
    except KeyboardInterrupt:
        pass

    # Ensure proper shutdown
    drone.quit()
    cv2.destroyAllWindows()
