from .utils import get_detect_colors


def adjust_drone_height(drone, avg_shoulder_y):
    """
    Adjust the drone's height based on the average Y-position of the shoulders.

    Args:
        drone (object): The drone control object.
        avg_shoulder_y (float): The average Y-coordinate of the shoulders.
    """
    # Constants for drone height adjustments
    target_position_ratio = 1 / 3  # Ratio of the shoulder's target Y-position in the frame
    frame_height = 720  # 720p video
    target_y_position = frame_height * target_position_ratio  # Y-coordinate of the target position in the frame
    threshold_y = 40  # Threshold for Y-coordinate error

    # Proportional constant for height control
    p_y = 0.15  # Higher value -> faster drone movements

    # Calculate the error between the target Y-position and the Y-position of the shoulders
    height_error = target_y_position - avg_shoulder_y
    height_adjustment = int(p_y * height_error)
    # If height error exceeds THRESHOLD_Y, the drone adjusts its height
    if abs(height_error) > threshold_y:
        if height_adjustment > 0:
            drone.up(min(height_adjustment, 100))
        else:
            drone.down(min(-height_adjustment, 100))


def adjust_drone_forward_backward(drone, torso_size):
    """
    Adjust the drone's forward/backward position based on the torso size.

    Args:
        drone (object): The drone control object.
        torso_size (float): The detected size of the torso.
    """
    # Constants for torso size to estimate distance
    target_torso_size = 0.6  # Target size of the torso, used to estimate the drone's forward/backward position
    threshold_torso_size = 0.1  # Threshold for torso size error

    # Proportional constant for forward/backward control
    p_torso = 1.2  # Higher value -> faster drone movements

    # Calculate the error between the target torso size and the detected torso size
    torso_error = target_torso_size - torso_size
    torso_adjustment = int(p_torso * torso_error * 100)
    # If torso size error exceeds THRESHOLD_TORSO_SIZE, the drone adjusts its position
    if abs(torso_error) > threshold_torso_size:
        if torso_adjustment > 0:
            drone.forward(min(torso_adjustment, 100))
        else:
            drone.backward(min(-torso_adjustment, 100))


def adjust_drone_yaw(drone, avg_shoulder_x, torso_size):
    """
    Adjust the drone's yaw based on the average X-position of the shoulders.

    Args:
        drone (object): The drone control object.
        avg_shoulder_x (float): The average X-coordinate of the shoulders.
        torso_size (float): The detected size of the torso.
    """
    # Constants for drone yaw adjustments
    frame_width = 1280  # 720p video
    target_x_position = frame_width / 2  # X-coordinate of the target position in the frame
    threshold_x = 50  # Threshold for X-coordinate error

    # Proportional constant for yaw control
    p_x = 0.11  # Higher value -> faster drone movements

    horizontal_error = avg_shoulder_x - target_x_position
    horizontal_adjustment = int(p_x * horizontal_error * (1 + 0.5*torso_size))
    if abs(horizontal_error) > threshold_x:
        if horizontal_adjustment > 0:
            drone.clockwise(min(horizontal_adjustment, 100))
        else:
            drone.counter_clockwise(min(-horizontal_adjustment, 100))


def adjust_drone(drone, avg_shoulder_x, avg_shoulder_y, torso_size):
    """
    Adjust the drone's height, forward/backward position, and yaw.

    Args:
        drone (object): The drone control object.
        avg_shoulder_x (float): The average X-coordinate of the shoulders.
        avg_shoulder_y (float): The average Y-coordinate of the shoulders.
        torso_size (float): The detected size of the torso.
    """
    # Check if input values are valid
    if avg_shoulder_x and avg_shoulder_y and torso_size:
        # Adjust drone height
        adjust_drone_height(drone, avg_shoulder_y)

        # Adjust drone forward/backward position
        adjust_drone_forward_backward(drone, torso_size)

        # Adjust drone yaw
        adjust_drone_yaw(drone, avg_shoulder_x, torso_size)


def track_person(last_similarity, drone, avg_shoulder_x, avg_shoulder_y, torso_size):
    """
    Track a person and adjust the drone's position accordingly.

    Args:
        last_similarity (float): The similarity score of the detected person.
        drone (object): The drone control object.
        avg_shoulder_x (float): The average X-coordinate of the shoulders.
        avg_shoulder_y (float): The average Y-coordinate of the shoulders.
        torso_size (float): The detected size of the torso.
    """
    # Check if color detection to differentiate between persons should be on
    if get_detect_colors():
        # Check if drone should follow person in frame
        if last_similarity is not None and last_similarity > 0.4:
            adjust_drone(drone, avg_shoulder_x, avg_shoulder_y, torso_size)
        elif last_similarity is None:
            adjust_drone(drone, avg_shoulder_x, avg_shoulder_y, torso_size)
        else:
            print("Warning: Person not recognized because of low similarity score.")
    else:
        # Follow any person in frame
        adjust_drone(drone, avg_shoulder_x, avg_shoulder_y, torso_size)
