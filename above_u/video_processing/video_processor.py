import av
import cv2
import mediapipe as mp
import numpy as np
import time
import warnings

from .pose_estimation import pose, calculate_torso_size, mp_drawing, calculate_avg_coordinates
from .person_color_detection import check_person_similarity, calibrate_colors
from .drone_tracking import track_person
from .utils import get_detect_colors


def create_image_from_frame(frame):
    """
    Convert a frame to a Color and RGB image.

    Args:
        frame (av.frame.Frame): The input frame.

    Returns:
        tuple: The BGR image and the RGB image.
    """
    image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)
    frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image, frame_rgb


class VideoProcessor:
    def __init__(self, drone_controller):
        """
        Initialize the VideoProcessor with a drone controller.

        Args:
            drone_controller (object): The drone controller object.
        """
        self.drone_controller = drone_controller

        self.current_frame = None
        self.last_30_frame_delays = []
        self.frame_count = 0

        self.pose_landmarks = None
        self.torso_size = None
        self.last_similarity = None

        self.tracking_active = False

    def start_tracking(self):
        self.tracking_active = True

    def stop_tracking(self):
        self.tracking_active = False

    def calculate_delay(self, start_time, end_time, image):
        """
        Calculate and display the average delay of the last 30 frames.

        Args:
            start_time (float): The start time of frame processing.
            end_time (float): The end time of frame processing.
            image (numpy.ndarray): The current frame image.
        """
        frame_delay = end_time - start_time
        self.last_30_frame_delays.append(frame_delay)

        # Only keep the last 30 delays
        if len(self.last_30_frame_delays) > 30:
            self.last_30_frame_delays.pop(0)

        # Calculate the average delay of the last 30 frames
        average_delay = sum(self.last_30_frame_delays) / len(self.last_30_frame_delays)

        # Draw the delay on screen
        cv2.putText(image, f'Avg Delay Last 30 Frames: {average_delay:.4f} s', (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

    def calibrate_colors(self, image):
        """
        Calibrate colors of the person in the frame.

        Args:
            image (numpy.ndarray): The RGB frame image.
        """
        if self.pose_landmarks:
            calibrate_colors(image, self.pose_landmarks)
        else:
            print("Color calibration didn't work. No pose landmarks detected")

    def process_pose_landmarks(self, pose_results):
        """
        Process the pose landmarks to calculate average shoulder position and torso size.

        Args:
            pose_results (mediapipe.python.solutions.pose.PoseLandmark): The pose landmarks results.

        Returns:
            tuple: The average shoulder X and Y coordinates.
        """
        self.pose_landmarks = pose_results.pose_landmarks.landmark
        avg_shoulder_x, avg_shoulder_y, self.torso_size = calculate_avg_coordinates(self.pose_landmarks,
                                                                                    calculate_torso_size(
                                                                                        self.pose_landmarks))
        return avg_shoulder_x, avg_shoulder_y

    def process_frame_tracking(self, frame_rgb, pose_results):
        """
        Process the frame for tracking purposes.

        Args:
            frame_rgb (numpy.ndarray): The RGB frame image.
            pose_results (mediapipe.python.solutions.pose.PoseLandmark): The pose landmarks results.
        """
        avg_shoulder_x, avg_shoulder_y = self.process_pose_landmarks(pose_results)

        # Perform person color similarity check every 30th frame
        if self.frame_count % 30 == 0 and get_detect_colors:
            self.last_similarity = check_person_similarity(frame_rgb, self.pose_landmarks)

        # Follow person in the frame if tracking is activated
        if self.tracking_active:
            track_person(self.last_similarity, self.drone_controller.drone, avg_shoulder_x, avg_shoulder_y,
                         self.torso_size)
        else:
            print("Tracking not active.")

    def process_frame(self, frame_rgb):
        """
        Process the frame for pose detection.

        Args:
            frame_rgb (numpy.ndarray): The RGB frame image.

        Returns:
            mediapipe.python.solutions.pose.PoseLandmark: The pose landmarks results.
        """
        pose_results = pose.process(frame_rgb)
        # Process the pose landmarks if a person is in frame
        if pose_results.pose_landmarks:
            self.process_frame_tracking(frame_rgb, pose_results)
        return pose_results

    def get_current_frame(self):
        """
        Get the current frame image.
        """
        return self.current_frame

    def start_video_stream(self):
        """
        Start the video stream and process each frame.
        """
        try:
            container = av.open(self.drone_controller.drone.get_video_stream())
        except av.error.InvalidDataError as e:
            print(f"Failed to open video stream: {e}")
            return
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return
        try:
            while self.drone_controller.running:
                for frame in container.decode(video=0):
                    # Get frame and convert to RGB
                    image, frame_rgb = create_image_from_frame(frame)

                    # Update the current frame
                    self.current_frame = image.copy()

                    # Count number of frames for skipping processing for some frames
                    self.frame_count += 1
                    # Save start time to calculate delay from processing
                    start_time = time.time()

                    # Process every 10th frame
                    if self.frame_count % 10 == 0:
                        # Process the frame for pose detection
                        pose_results = self.process_frame(frame_rgb)

                    # Draw data and skeleton in the frame
                    if self.pose_landmarks:
                        # Draw the torso size on the frame
                        cv2.putText(image, f'Torso Size: {self.torso_size:.2f}', (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

                        # Draw skeleton on the frame
                        mp_drawing.draw_landmarks(image, pose_results.pose_landmarks,
                                                  mp.solutions.pose.POSE_CONNECTIONS)

                        # Draw similar score
                        if self.last_similarity is not None:
                            cv2.putText(image, f'Similarity: {self.last_similarity:.2f}', (10, 70),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                    # Calculate delay from processing
                    self.calculate_delay(start_time, time.time(), image)

                    # Ensure cv2.imshow is called in a GUI-capable environment
                    try:
                        cv2.imshow('Output', image)
                    except cv2.error as e:
                        warnings.warn("cv2.imshow failed. Skipping frame display.", UserWarning)
                        print(f"cv2.error: {e}")

                    # Check for key press
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('c') and self.pose_landmarks and get_detect_colors:
                        # Calibrate torso colors of person in frame
                        calibrate_colors(image, self.pose_landmarks)
                    if key == ord('q'):
                        # Quit
                        self.drone_controller.running = False
                        break
        except KeyboardInterrupt:
            pass

        self.drone_controller.quit()
        cv2.destroyAllWindows()
