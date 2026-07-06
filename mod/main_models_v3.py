import mediapipe as mp
import cv2
from mod import HandshapeRecognizer
import tempfile
import os

dataset = "models v3"
datasetPath = "Models"

# Tu można zdefiniować osoby i gesty
subjects = []  # pusta lista oznacza, że bierzemy pod uwagę wszystkie osoby
gestures = []  # pusta lista oznacza, że bierzemy pod uwagę wszystkie gesty
subjects = ['1', '2', '3', '4', '5', '6', '9', '10', '11', '12', '13', '14']  # bez osób 7 i 8

def runRealTime():
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0)

    handshapeRecognizer = HandshapeRecognizer.HandshapeRecognizer(dataset, datasetPath, subjects, gestures)  # all subjects
    handshapeRecognizer.train()

    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'predicted_label.txt')

    with open(file_path, 'w') as f:
        f.write("\n1")

    with mp_hands.Hands(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                continue

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True

            if results.multi_hand_landmarks:
                for num, hand in enumerate(results.multi_hand_landmarks):
                    mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS,
                                              mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                                              mp_drawing.DrawingSpec(color=(121, 44, 76), thickness=2, circle_radius=2))

            predictedLabel = handshapeRecognizer.run(results, isMediaPipeResult=True)
            if predictedLabel:
                with open(file_path, 'w') as f:
                    f.write(f"{predictedLabel}\n1")
                #print(f"Predicted label written to file: {predictedLabel}")

            cv2.imshow('Camera', frame)

            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    runRealTime()
