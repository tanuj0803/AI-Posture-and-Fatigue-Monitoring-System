import cv2
import mediapipe as mp
import time
import threading
import os
import math

def speak_alert():
    os.system(
        'powershell -Command "Add-Type -AssemblyName System.Speech; '
        '(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'Please sit properly\')"'
    )

def calculate_angle(x1, y1, x2, y2):
    return abs(
        math.degrees(
            math.atan2(y2 - y1, x2 - x1)
        )
    )

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

last_alert_time = 0
alert_active = False

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = pose.process(rgb_frame)

    posture_text = "No Person"
    color = (255, 255, 255)

    if results.pose_landmarks:

        mp_draw.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        landmarks = results.pose_landmarks.landmark

        left_ear = landmarks[7]

        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]

        h, w, _ = frame.shape

        ear_x = int(left_ear.x * w)
        ear_y = int(left_ear.y * h)

        left_x = int(left_shoulder.x * w)
        left_y = int(left_shoulder.y * h)

        right_x = int(right_shoulder.x * w)
        right_y = int(right_shoulder.y * h)

        mid_shoulder_x = (left_x + right_x) // 2
        mid_shoulder_y = (left_y + right_y) // 2

        cv2.line(
            frame,
            (ear_x, ear_y),
            (mid_shoulder_x, mid_shoulder_y),
            (255, 0, 0),
            3
        )

        cv2.line(
            frame,
            (left_x, left_y),
            (right_x, right_y),
            (0, 255, 255),
            3
        )

        neck_angle = calculate_angle(
            ear_x,
            ear_y,
            mid_shoulder_x,
            mid_shoulder_y
        )

        shoulder_diff = abs(
            left_shoulder.y - right_shoulder.y
        )

        cv2.putText(
            frame,
            f"Neck Angle: {int(neck_angle)}",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Shoulder Diff: {round(shoulder_diff, 3)}",
            (30, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        if 80 <= neck_angle <= 125 and shoulder_diff < 0.05:

            posture_text = "Good Posture"
            color = (0, 255, 0)

            alert_active = False

        else:

            posture_text = "Bad Posture"
            color = (0, 0, 255)

            current_time = time.time()

            if current_time - last_alert_time >= 5 and not alert_active:

                alert_active = True

                def threaded_alert():

                    global alert_active

                    speak_alert()

                    alert_active = False

                threading.Thread(
                    target=threaded_alert
                ).start()

                last_alert_time = current_time

    cv2.putText(
        frame,
        posture_text,
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        3
    )

    cv2.imshow(
        "AI Neck Posture Detector",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()