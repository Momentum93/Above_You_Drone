# Above U Drone
**Master Praktikum: Usable Security**

![A flying drone.](https://images.unsplash.com/photo-1514598800938-f7125ea1aa1c?q=80&w=2831&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)

With Above U, a Tello drone can autonomously track a person using machine learning based pose estimation. Commands to control the drone can be sent via a USB serial connection, allowing remote control via a smartphone connected to a USB WiFi module.

## How the Tracking Works

Using MediaPipe Pose Detection, we can recognise a person in the frame of the drone's video feed. This works whether the person is facing the camera or not. Using the torso coordinates, we track the person's movement with the drone. To keep a constant distance. For performance reasons this is only done every 10th frame.
![MediaPipe Pose skeleton.](https://ai.google.dev/static/mediapipe/images/solutions/pose_landmarks_index.png?hl=de)
To distinguish between people, you can calibrate the tracking of just one person. This works by identifying histograms and dominant colors of the torso. These are subsequently compared every 30th frame for performance.
## References

- [TelloPy Tello drone controller](https://github.com/hanyazou/TelloPy)
- [MediaPipe Pose Detection](https://chuoling.github.io/mediapipe/solutions/pose.html)