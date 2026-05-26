import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime

import serial
import time
import winsound

arduino = serial.Serial('COM5', 9600)  # change COM port
time.sleep(2)

last_capture_time = 0

known_encodings = []
known_names = []

dataset_path = "dataset"

# Load all faces from dataset
for person in os.listdir(dataset_path):
    person_folder = os.path.join(dataset_path, person)

    for image in os.listdir(person_folder):
        img_path = os.path.join(person_folder, image)
        img = face_recognition.load_image_file(img_path)
        
        encodings = face_recognition.face_encodings(img)
        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(person)

print("Dataset Loaded Successfully")

video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    faces = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, faces)

    for (top, right, bottom, left), encoding in zip(faces, encodings):

        matches = face_recognition.compare_faces(
            known_encodings, encoding, tolerance=0.6)

        face_distances = face_recognition.face_distance(known_encodings, encoding)

        if len(face_distances) > 0:
            best_match = np.argmin(face_distances)

            name = "Unknown"

            if face_distances[best_match] < 0.6:
                name = known_names[best_match]
                arduino.write(b'1')
        if name == "Unknown":
            current_time = time.time()

            if current_time - last_capture_time > 5:   # 5 sec delay
                    now = datetime.now().strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(f"intruders/{now}.jpg", frame)
                    print("⚠️ Unknown person detected!")
                    winsound.Beep(1000, 500) #for sound
                    last_capture_time = current_time
                    now = datetime.now().strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(f"intruders/{now}.jpg", frame)

        cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
        cv2.putText(frame, name, (left, top-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    cv2.imshow("Smart Face Unlock System", frame)

    if cv2.waitKey(1) == 27:
        break

video.release()
cv2.destroyAllWindows()