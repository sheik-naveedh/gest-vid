import cv2
import mediapipe as mp
import numpy as np
import os
import joblib
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from collections import deque

# Setup MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Directory to save the dataset
DATASET_DIR = "gesture_data"
os.makedirs(DATASET_DIR, exist_ok=True)

# Gesture names
gesture_names = ["increase", "decrease", "forward", "rewind", "play", "pause"]
gesture_index = 0

# Parameters for data collection
samples_per_gesture = 100
captured_samples = 0
data = []
labels = []

# Initialize model
model = make_pipeline(StandardScaler(), SVC(kernel='linear', probability=True))

# Function to extract landmarks
def extract_landmarks(results):
    if results.multi_hand_landmarks:
        landmarks = []
        for hand_landmarks in results.multi_hand_landmarks:
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
        return np.array(landmarks)
    return np.array([])

# Video Capture
cap = cv2.VideoCapture(0)

def collect_gesture_data():
    global gesture_index, captured_samples
    print(f"Start collecting data for: {gesture_names[gesture_index]}")
    captured_samples = 0
    while captured_samples < samples_per_gesture:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            landmarks = extract_landmarks(results)
            if landmarks.size > 0:
                data.append(landmarks)
                labels.append(gesture_names[gesture_index])
                captured_samples += 1
                cv2.putText(frame, f"Capturing {gesture_names[gesture_index]}: {captured_samples}/{samples_per_gesture}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("Gesture Collection", frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    
    # Move to the next gesture after collection
    gesture_index += 1
    if gesture_index < len(gesture_names):
        cv2.putText(frame, f"Data collection completed for {gesture_names[gesture_index - 1]}. Prepare for {gesture_names[gesture_index]}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.imshow("Gesture Collection", frame)
    cv2.waitKey(2000)  # Show a 2-second delay between gestures

while gesture_index < len(gesture_names):
    collect_gesture_data()

cap.release()
cv2.destroyAllWindows()

# Convert data to numpy arrays
data = np.array(data)
labels = np.array(labels)

# Training the model
model.fit(data, labels)

# Save the trained model
model_filename = "gesture_recognition_model.pkl"
joblib.dump(model, model_filename)

print(f"Model trained and saved as {model_filename}")

# Real-time Gesture Prediction
cap = cv2.VideoCapture(0)
gesture_history = deque(maxlen=5)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        landmarks = extract_landmarks(results)
        
        if landmarks.size > 0:
            prediction = model.predict([landmarks])[0]
            gesture_history.append(prediction)
            if len(gesture_history) == gesture_history.maxlen:
                predicted_gesture = max(set(gesture_history), key=gesture_history.count)
                cv2.putText(frame, f"Predicted Gesture: {predicted_gesture}", 
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("Gesture Prediction", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
