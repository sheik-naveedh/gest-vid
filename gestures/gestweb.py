import asyncio
import websockets
import joblib
import cv2
import mediapipe as mp
import numpy as np
from sklearn.pipeline import make_pipeline
from collections import deque

# Load the pre-trained model
model = joblib.load("gesture_recognition_model.pkl")

# Setup MediaPipe and Hand Detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

def extract_landmarks(results):
    if results.multi_hand_landmarks:
        landmarks = []
        for hand_landmarks in results.multi_hand_landmarks:
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
        return np.array(landmarks)
    return np.array([])

# Function to normalize landmarks (scaling and centering)
def normalize_landmarks(landmarks):
    landmarks = np.array(landmarks).reshape(-1, 3)
    # Normalize landmarks by setting the origin to the wrist (landmark 0)
    wrist = landmarks[0]
    landmarks -= wrist
    max_val = np.max(np.abs(landmarks))
    landmarks /= max_val
    return landmarks.flatten()

# WebSocket server to send gesture predictions
async def gesture_server(websocket, path):
    cap = cv2.VideoCapture(0)
    gesture_history = deque(maxlen=5)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            landmarks = extract_landmarks(results)
            if landmarks.size > 0:
                normalized_landmarks = normalize_landmarks(landmarks)
                prediction = model.predict([normalized_landmarks])[0]
                gesture_history.append(prediction)
                
                # Use majority vote in history to improve accuracy
                if len(gesture_history) == gesture_history.maxlen:
                    predicted_gesture = max(set(gesture_history), key=gesture_history.count)
                    if gesture_history.count(predicted_gesture) >= 3:
                        await websocket.send(predicted_gesture)
                    
        await asyncio.sleep(0.1)

    cap.release()
    cv2.destroyAllWindows()

# Start the WebSocket server
start_server = websockets.serve(gesture_server, "localhost", 5678)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
