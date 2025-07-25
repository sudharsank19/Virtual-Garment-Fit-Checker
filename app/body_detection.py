import mediapipe as mp
import cv2
import numpy as np

mp_pose = mp.solutions.pose

def estimate_body_measurements(frame):
    with mp_pose.Pose(static_image_mode=False) as pose:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(frame_rgb)

        if not result.pose_landmarks:
            return None

        h, w, _ = frame.shape
        lm = result.pose_landmarks.landmark

        def get_pixel_distance(p1, p2):
            return np.linalg.norm([
                (lm[p1].x - lm[p2].x) * w,
                (lm[p1].y - lm[p2].y) * h
            ])

        return {
            "shoulder_width": round(get_pixel_distance(mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER), 2),
            "chest_circumference": round(get_pixel_distance(mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER) * 2.2, 2),
            "waist_circumference": round(get_pixel_distance(mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP) * 2.3, 2)
        }
