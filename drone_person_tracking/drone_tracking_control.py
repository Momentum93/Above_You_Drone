from utils import get_detect_colors

def adjust_drone_height(drone, avg_shoulder_y):
    # Constants for drone height adjustments
    TARGET_POSITION_RATIO = 1 / 3  # Ratio of the shoulder's target Y-position in the frame
    FRAME_HEIGHT = 720  # 720p video
    TARGET_Y_POSITION = FRAME_HEIGHT * TARGET_POSITION_RATIO  # Y-coordinate of the target position in the frame
    THRESHOLD_Y = 40  # Threshold for Y-coordinate error

    # Proportional constant for height control
    P_Y = 0.15  # Higher value -> faster drone movements

    # Calculate the error between the target Y-position and the Y-position of the shoulders
    height_error = TARGET_Y_POSITION - avg_shoulder_y
    height_adjustment = int(P_Y * height_error)
    # If height error exceeds THRESHOLD_Y, the drone adjusts its height
    if abs(height_error) > THRESHOLD_Y:
        if height_adjustment > 0:
            drone.up(min(height_adjustment, 100))
        else:
            drone.down(min(-height_adjustment, 100))

def adjust_drone_forward_backward(drone, torso_size):
    # Constants for torso size to estimate distance
    TARGET_TORSO_SIZE = 0.6  # Target size of the torso, used to estimate the drone's forward/backward position
    THRESHOLD_TORSO_SIZE = 0.1  # Threshold for torso size error

    # Proportional constant for forward/backward control
    P_TORSO = 0.5  # Higher value -> faster drone movements

    # Calculate the error between the target torso size and the detected torso size
    torso_error = TARGET_TORSO_SIZE - torso_size
    torso_adjustment = int(P_TORSO * torso_error * 100)
    # If torso size error exceeds THRESHOLD_TORSO_SIZE, the drone adjusts its position
    if abs(torso_error) > THRESHOLD_TORSO_SIZE:
        if torso_adjustment > 0:
            drone.forward(min(torso_adjustment, 100))
        else:
            drone.backward(min(-torso_adjustment, 100))

def adjust_drone_yaw(drone, avg_shoulder_x):
    # Constants for drone yaw adjustments
    FRAME_WIDTH = 1280  # 720p video
    TARGET_X_POSITION = FRAME_WIDTH / 2  # X-coordinate of the target position in the frame
    THRESHOLD_X = 50  # Threshold for X-coordinate error

    # Proportional constant for yaw control
    P_X = 0.1  # Higher value -> faster drone movements

    horizontal_error = avg_shoulder_x - TARGET_X_POSITION
    horizontal_adjustment = int(P_X * horizontal_error)
    if abs(horizontal_error) > THRESHOLD_X:
        if horizontal_adjustment > 0:
            drone.clockwise(min(horizontal_adjustment, 100))
        else:
            drone.counter_clockwise(min(-horizontal_adjustment, 100))

def adjust_drone(drone, avg_shoulder_x, avg_shoulder_y, torso_size):
    # Adjust drone height
    adjust_drone_height(drone, avg_shoulder_y)

    # Adjust drone forward/backward position
    adjust_drone_forward_backward(drone, torso_size)

    # Adjust drone yaw
    adjust_drone_yaw(drone, avg_shoulder_x)

def track_person(last_similarity, drone, avg_shoulder_x, avg_shoulder_y, torso_size):
    # Check if color detection to differentiate between persons should be on
    if get_detect_colors():
        # Check if drone should follow person in frame
        if last_similarity is not None and last_similarity > 0.5:
            adjust_drone(drone, avg_shoulder_x, avg_shoulder_y, torso_size)
        elif last_similarity is None:
            adjust_drone(drone, avg_shoulder_x, avg_shoulder_y, torso_size)
        else:
            print("Warning: Person not recognized.")
    else:
        # Follow any person in frame
        adjust_drone(drone, avg_shoulder_x, avg_shoulder_y, torso_size)
