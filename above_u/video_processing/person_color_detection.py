import cv2
import mediapipe as mp
import numpy as np
from sklearn.cluster import KMeans

from .utils import get_frame_height, get_frame_width

# Calibrated color histogram and dominant colors
calibrated_color_histogram = None
calibrated_dominant_colors = None


def extract_torso_region(frame, pose_landmarks):
    """
    Extract the torso region from the frame using pose landmarks.

    Args:
        frame (numpy.ndarray): The current video frame.
        pose_landmarks (list): List of pose landmarks for the person in the frame.

    Returns:
        numpy.ndarray: Cropped frame containing the torso region.

    Raises:
        ValueError: If coordinates of landmarks are not within the range of 0 to 1.
    """
    # Get coordinates of shoulders and hips
    left_shoulder = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip = pose_landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]
    right_hip = pose_landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

    # Check if x and y values are within the range of [0, 1]
    if not all(0 <= lm.x <= 1 and 0 <= lm.y <= 1 for lm in [left_shoulder, right_shoulder, left_hip, right_hip]):
        raise ValueError("Coordinates of landmarks are not within the range of 0 to 1")

    # Calculate bounding box for the torso
    x_min = int(min(left_shoulder, right_shoulder, left_hip.x, right_hip.x) * get_frame_width())
    x_max = int(max(left_shoulder, right_shoulder, left_hip.x, right_hip.x) * get_frame_width())
    y_min = int(min(left_shoulder.y, right_shoulder.y, left_hip.y, right_hip.y) * get_frame_height())
    y_max = int(max(left_shoulder.y, right_shoulder.y, left_hip.y, right_hip.y) * get_frame_height())
    bounding_box = frame[y_min:y_max, x_min:x_max]

    return bounding_box


def calculate_color_histogram(image):
    """
    Compute a normalized color histogram for the given image.

    Args:
        image (numpy.ndarray): The input image.

    Returns:
        numpy.ndarray: The normalized color histogram.
    """
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist.astype(np.float32)


def find_dominant_colors(image, k=3):
    """
    Identify the dominant colors in the image using K-means clustering.

    Args:
        image (numpy.ndarray): The input image.
        k (int, optional): Number of clusters for K-means. Default is 3.

    Returns:
        numpy.ndarray or None: Array of dominant colors or None if an error occurs.
    """
    try:
        pixels = image.reshape(-1, 3)
        kmeans = KMeans(n_clusters=k).fit(pixels)
        colors = np.round(kmeans.cluster_centers_).astype(int)
        return colors
    except ValueError as e:
        print(f"Error occurred when finding dominant colors: {e}")

    return None


def calculate_histogram_similarity(hist1, hist2, method=cv2.HISTCMP_CORREL):
    """
    Compare two histograms and return a similarity score.

    Args:
        hist1 (numpy.ndarray): First histogram.
        hist2 (numpy.ndarray): Second histogram.
        method (int, optional): OpenCV histogram comparison method. Default is cv2.HISTCMP_CORREL.

    Returns:
        float: Similarity score between the two histograms.
    """
    return cv2.compareHist(hist1, hist2, method)


def calculate_color_similarity(calibrated_colors, current_colors):
    """
    Compare two color arrays and return a similarity score.

    Args:
        calibrated_colors (numpy.ndarray): Array of calibrated dominant colors.
        current_colors (numpy.ndarray): Array of current dominant colors.

    Returns:
        float: Similarity score between the two color arrays.
    """
    color_similarity = np.mean([np.linalg.norm(calibrated_colors[i] - current_colors[i]) for i in
                                range(len(calibrated_colors))])
    color_similarity = 1 - (color_similarity / 441.67)  # Normalize to [0, 1]
    return color_similarity


def calibrate_colors(frame, pose_landmarks):
    """
    Calibrate the colors for the input frame.

    Args:
        frame (numpy.ndarray): The current video frame.
        pose_landmarks (list): List of pose landmarks for the person in the frame.
    """
    global calibrated_color_histogram, calibrated_dominant_colors

    try:
        torso_region = extract_torso_region(frame, pose_landmarks)
        calibrated_color_histogram = calculate_color_histogram(torso_region)
        calibrated_dominant_colors = find_dominant_colors(torso_region)
    except ValueError:
        print(f"Calibration did not work: Torso not fully in frame")


def are_torso_colors_calibrated():
    """
    Check if torso colors are calibrated.

    Returns:
        bool: True if calibrated, False otherwise.
    """
    return calibrated_color_histogram is not None and calibrated_dominant_colors is not None


def check_person_similarity(frame, pose_landmarks, method=cv2.HISTCMP_CORREL):
    """
    Check the similarity of the current frame's person to the calibrated person.

    Args:
        frame (numpy.ndarray): The current video frame.
        pose_landmarks (list): List of pose landmarks for the person in the frame.
        method (int, optional): OpenCV histogram comparison method. Default is cv2.HISTCMP_CORREL.

    Returns:
        float or None: The average similarity score or None if similarity cannot be computed.
    """
    if are_torso_colors_calibrated():
        # Extract torso if torso is fully in frame
        try:
            current_torso_region = extract_torso_region(frame, pose_landmarks)
        except ValueError:
            print(f"Calibration did not work: Torso not fully in frame")
            return None

        current_histogram = calculate_color_histogram(current_torso_region)
        current_colors = find_dominant_colors(current_torso_region)

        if current_colors is not None:
            histogram_similarity = calculate_histogram_similarity(calibrated_color_histogram, current_histogram, method)
            color_similarity = calculate_color_similarity(calibrated_dominant_colors, current_colors)

            return (histogram_similarity + color_similarity) / 2  # Average of both similarities
        else:
            return None
    # Return None if torso colors aren't calibrated
    else:
        return None


def check_person_similarity(frame, pose_landmarks, method=cv2.HISTCMP_CORREL):
    """
    Check the similarity of the current frame's person to the calibrated person.

    Parameters:
    frame (np.ndarray): The current video frame.
    pose_landmarks (list): The pose landmarks of the person in the frame.
    method (int): The method for comparing histograms (default: cv2.HISTCMP_CORREL).

    Returns:
    float or None: The average similarity score or None if the comparison cannot be made.
    """
    if not are_torso_colors_calibrated():
        return None

    try:
        current_torso_region = extract_torso_region(frame, pose_landmarks)
    except ValueError:
        print(f"Calibration did not work: Torso not fully in frame")
        return None

    current_histogram = calculate_color_histogram(current_torso_region)
    current_colors = find_dominant_colors(current_torso_region)

    if current_colors is None:
        return None

    histogram_similarity = calculate_histogram_similarity(calibrated_color_histogram, current_histogram, method)
    color_similarity = calculate_color_similarity(calibrated_dominant_colors, current_colors)

    return (histogram_similarity + color_similarity) / 2
