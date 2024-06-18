import cv2
import mediapipe as mp
import numpy as np
from sklearn.cluster import KMeans
from utils import get_frame_height, get_frame_width
import warnings

# Calibrated color histogram and dominant colors
calibrated_color_histogram = None
calibrated_dominant_colors = None


def calculate_torso_bounding_box(frame, x1, x2, x3, x4, y1, y2, y3, y4):
    # Calculate bounding box for the torso
    x_min = int(min(x1, x2, x3, x4) * get_frame_width())
    x_max = int(max(x1, x2, x3, x4) * get_frame_width())
    y_min = int(min(y1, y2, y3, y4) * get_frame_height())
    y_max = int(max(y1, y2, y3, y4) * get_frame_height())

    return frame[y_min:y_max, x_min:x_max]


def extract_torso_region(frame, pose_landmarks):
    # Get coordinates of shoulders and hips
    left_shoulder = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]
    right_hip = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

    # Check if x and y values are within the range of [0, 1]
    if not all(0 <= lm.x <= 1 and 0 <= lm.y <= 1 for lm in [left_shoulder, right_shoulder, left_hip, right_hip]):
        raise ValueError("Coordinates of landmarks are not within the range of 0 to 1")

    # Calculate bounding box for the torso
    bounding_box = calculate_torso_bounding_box(frame, left_shoulder.x, right_shoulder.x, left_hip.x, right_hip.x,
                                                left_shoulder.y, right_shoulder.y, left_hip.y, right_hip.y)

    # Return the cropped torso region
    return bounding_box


# Compute a normalized color histogram for the given image
def calculate_color_histogram(image):
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist.astype(np.float32)


# Identify the dominant colors in the image using K-means clustering
def find_dominant_colors(image, k=3):
    try:
        pixels = image.reshape(-1, 3)
        kmeans = KMeans(n_clusters=k).fit(pixels)
        colors = np.round(kmeans.cluster_centers_).astype(int)
        return colors
    except ValueError as e:
        warnings.warn(str(e))

    return None


# Compare two histograms and returns a similarity score
def calculate_histogram_similarity(hist1, hist2, method=cv2.HISTCMP_CORREL):
    return cv2.compareHist(hist1, hist2, method)


# Compare two color arrays and returns a similarity score
def calculate_color_similarity(calibrated_dominant_colors, current_colors):
    color_similarity = np.mean([np.linalg.norm(calibrated_dominant_colors[i] - current_colors[i]) for i in
                                range(len(calibrated_dominant_colors))])
    color_similarity = 1 - (color_similarity / 441.67)  # Normalize to [0, 1]
    return color_similarity


# Calibrates the colors for input frame
def calibrate_colors(frame, pose_landmarks):
    global calibrated_color_histogram, calibrated_dominant_colors

    try:
        torso_region = extract_torso_region(frame, pose_landmarks)
        calibrated_color_histogram = calculate_color_histogram(torso_region)
        calibrated_dominant_colors = find_dominant_colors(torso_region)
    except ValueError:
        warnings.warn("Calibration warning: Torso not fully in frame", category=UserWarning)


# Check the similarity of the current frame's person to the calibrated person
def check_person_similarity(frame, pose_landmarks, method=cv2.HISTCMP_CORREL):
    # Check similarity if torso colors are calibrated
    if calibrated_color_histogram is not None and calibrated_dominant_colors is not None:
        try:
            current_torso_region = extract_torso_region(frame, pose_landmarks)
        except ValueError:
            warnings.warn("Calibration warning: Torso not fully in frame", category=UserWarning)
            return None

        current_histogram = calculate_color_histogram(current_torso_region)
        current_colors = find_dominant_colors(current_torso_region)

        histogram_similarity = calculate_histogram_similarity(calibrated_color_histogram, current_histogram, method)
        if current_colors is not None:
            color_similarity = calculate_color_similarity(calibrated_dominant_colors, current_colors)

            return (histogram_similarity + color_similarity) / 2  # Average of both similarities
        else:
            return None
    # Return None if torso colors aren't calibrated
    else:
        return None
