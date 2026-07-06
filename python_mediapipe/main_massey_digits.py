import mediapipe as mp
import cv2
from mod.HandshapeRecognizer import HandshapeRecognizer
from mod.Validator import Validator

dataset = "massey digits"
datasetPath = "Models (różne wersje)/Massey digits"

def runRealTime():
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    # mp_drawing_styles = mp.solutions.drawing_styles

    cap = cv2.VideoCapture(0)

    handshapeRecognizer = HandshapeRecognizer(dataset, datasetPath) #all subjects
    handshapeRecognizer.train()

    with mp_hands.Hands(model_complexity=1,min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            ret, frame = cap.read()

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            #jakby nie działało to te flagi do zmiany
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True

            if results.multi_hand_landmarks:
                for num, hand in enumerate(results.multi_hand_landmarks):
                    mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(121,22,76),thickness=2,circle_radius=4),
                    mp_drawing.DrawingSpec(color=(121,44,76),thickness=2,circle_radius=2))

            predictedLabel = handshapeRecognizer.run(results, isMediaPipeResult=True)
            print(predictedLabel)

            cv2.imshow('Camera', frame)

            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()
    cv2.destroyAllWindows()

def print2DListAligned(list, pad=3):
    for line in list:
        print(*[str(i).rjust(pad) for i in line], sep=" ")

def validate(type):
    validator = Validator(dataset,datasetPath)
    if type == "holdout":
        results = validator.holdoutValidation(["2"],["1"])
        print(results)
    elif type == "loso":
        results = validator.losoCrossValidation()
        print2DListAligned(results[2])
        print(round(results[0], 2), round(results[1], 2), results[3])

#____________________________________
#runRealTime()
#validate("holdout")
validate("loso")









