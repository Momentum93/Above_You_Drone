import mediapipe as mp
import math

# Initialize MediaPipe Pose estimator
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def calculate_distance(coord1, coord2):
    # Calculate the Euclidean distance between two coordinates.
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
