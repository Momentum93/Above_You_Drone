import mediapipe as mp
import math
from utils import get_frame_height, get_frame_width

# Number of measurements that should be used to calculate average coordinates
FILTER_SIZE = 5

# Store recent measurements for the average filter
recent_shoulder_xs = []
recent_shoulder_ys = []
recent_torso_sizes = []

# Initialize MediaPipe Pose estimator
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def calculate_distance(coord1, coord2):
    # Calculate the distance between two coordinates
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

def calculate_torso_size(landmarks):
    # Calculate the size of the torso using shoulder and hip landmarks.
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

    shoulder_distance = calculate_distance((left_shoulder.x, left_shoulder.y), (right_shoulder.x, right_shoulder.y))
    hip_distance = calculate_distance((left_hip.x, left_hip.y), (right_hip.x, right_hip.y))
    torso_height = calculate_distance(((left_shoulder.x + right_shoulder.x) / 2, (left_shoulder.y + right_shoulder.y) / 2),
                                      ((left_hip.x + right_hip.x) / 2, (left_hip.y + right_hip.y) / 2))

    return shoulder_distance + hip_distance + torso_height

def append_recent_measurements(avg_shoulder_x, avg_shoulder_y, current_torso_size):
    # Append to recent measurements
    recent_shoulder_xs.append(avg_shoulder_x)
    recent_shoulder_ys.append(avg_shoulder_y)
    recent_torso_sizes.append(current_torso_size)

    # Maintain the size of the recent measurements list
    if len(recent_shoulder_ys) > FILTER_SIZE:
        recent_shoulder_ys.pop(0)
    if len(recent_torso_sizes) > FILTER_SIZE:
        recent_torso_sizes.pop(0)
    if len(recent_shoulder_xs) > FILTER_SIZE:
        recent_shoulder_xs.pop(0)

def calculate_avg_coordinates(pose_landmarks, current_torso_size):
    # Get shoulder x-coordinates
    left_shoulder_x = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].x * get_frame_width()
    right_shoulder_x = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER].x * get_frame_width()
    avg_shoulder_x = (left_shoulder_x + right_shoulder_x) / 2

    # Get shoulder y-coordinates
    left_shoulder_y = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].y * get_frame_height()
    right_shoulder_y = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER].y * get_frame_height()
    avg_shoulder_y = (left_shoulder_y + right_shoulder_y) / 2

    append_recent_measurements(avg_shoulder_x, avg_shoulder_y, current_torso_size)

    # Calculate moving average
    avg_shoulder_x = sum(recent_shoulder_xs) / len(recent_shoulder_xs)
    avg_shoulder_y = sum(recent_shoulder_ys) / len(recent_shoulder_ys)
    torso_size = sum(recent_torso_sizes) / len(recent_torso_sizes)

    return avg_shoulder_x, avg_shoulder_y, torso_size
