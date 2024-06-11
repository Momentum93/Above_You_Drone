import av
import cv2
import mediapipe as mp
import numpy as np
import time
from pose_estimation import pose, calculate_torso_size, mp_drawing, calculate_avg_coordinates
from person_color_detection import check_person_similarity, calibrate_colors
from drone_tracking_control import track_person
from utils import get_detect_colors

def create_image_from_frame(frame):
    # Get frame and convert to RGB
    image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)
    frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image, frame_rgb

# Initialize list to store delays of last 30 frames
last_30_frame_delays = []

# Calculate the average delay of the processing from the last 30 frames
def calculate_delay(start_time, end_time, image):
    global last_30_frame_delays

    frame_delay = end_time - start_time
    last_30_frame_delays.append(frame_delay)

    # Keep only the last 30 delays
    if len(last_30_frame_delays) > 30:
        last_30_frame_delays.pop(0)

    # Calculate the average delay of the last 30 frames
    average_delay = sum(last_30_frame_delays) / len(last_30_frame_delays)

    # Draw the delay on screen
    cv2.putText(image, f'Avg Delay Last 30 Frames: {average_delay:.4f} s', (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

def start_video_stream(drone, drone_controller):
    container = av.open(drone.get_video_stream())
    frame_count = 0

    # Store pose landmarks and torso size
    pose_landmarks = None
    torso_size = None

    # Initialize person similarity score to differentiate between persons
    last_similarity = None

    try:
        while drone_controller.running:
            for frame in container.decode(video=0):
                # Get frame and convert to RGB
                image, frame_rgb = create_image_from_frame(frame)

                # Count number of frames for skipping processing for some frames
                frame_count += 1
                # Save start time to calculate delay from processing
                start_time = time.time()

                # Process every 10th frame
                if frame_count % 10 == 0:
                    # Process the frame for pose detection
                    pose_results = pose.process(frame_rgb)

                    if pose_results.pose_landmarks:
                        pose_landmarks = pose_results.pose_landmarks.landmark

                        # Calculate average of shoulder position and torso size
                        avg_shoulder_x, avg_shoulder_y, torso_size = calculate_avg_coordinates(pose_landmarks, calculate_torso_size(pose_landmarks))

                        # Perform person color similarity check every 30th frame
                        if frame_count % 30 == 0 and get_detect_colors:
                            last_similarity = check_person_similarity(image, pose_landmarks)

                        # Follow person in the frame
                        track_person(last_similarity, drone, avg_shoulder_x, avg_shoulder_y, torso_size)

                # Draw data and skeleton in the frame
                if pose_landmarks:
                    # Draw the torso size on the frame
                    cv2.putText(image, f'Torso Size: {torso_size:.2f}', (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

                    # Draw skeleton on the frame
                    mp_drawing.draw_landmarks(image, pose_results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)

                    # Draw similar score
                    if last_similarity is not None:
                        cv2.putText(image, f'Similarity: {last_similarity:.2f}', (10, 70),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                # Calculate delay from processing
                calculate_delay(start_time, time.time(), image)

                # Display the frame
                cv2.imshow('Output', image)

                # Check for key press
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c') and pose_landmarks and get_detect_colors:
                    # Calibrate torso colors of person in frame
                    calibrate_colors(image, pose_landmarks)
                if key == ord('q'):
                    # Quit
                    drone_controller.running = False
                    break
    except KeyboardInterrupt:
        pass

    drone.quit()
    cv2.destroyAllWindows()
