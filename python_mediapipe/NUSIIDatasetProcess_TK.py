import os
import mediapipe as mp
import cv2
from mod import RawData as rd
import pickle
import numpy as np
import random

mp_hands = mp.solutions.hands
#hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
#best model complexity for Massey and NUS II = 0
hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0, min_tracking_confidence=0.5,static_image_mode=False,max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

datasetFolder = "D:\\Downloads\\NUS II\\dataset" #UWAGA: skopiować zbiór do Downloads, bo w ścieżce opencv nie może być polskich liter (i być może też spacji)
outputDataFolder = "D:/Praca - uczelnia/projekty/2023/gesty statyczne mediapipe/python_mediapipe/Models (różne wersje)/NUS II"

personsNumber = 40
signs = 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'

filePathsPerClassPerson = [[None] * personsNumber for _ in range(len(signs))]
previousSign = ""
#load file paths
for fileName in os.listdir(datasetFolder):
    sign = fileName[0]
    if previousSign != sign:
        repetitionCounter = 0

    parenthesisOpen = fileName.find("(")
    parenthesisClosed = fileName.find(")")
    person = int(fileName[parenthesisOpen+1:parenthesisClosed]) // 5

    if filePathsPerClassPerson[signs.index(sign)][int(person)] == None:
        filePathsPerClassPerson[signs.index(sign)][int(person)] = [datasetFolder + "\\" + fileName]
    else:
        filePathsPerClassPerson[signs.index(sign)][int(person)].append( datasetFolder + "\\" + fileName )

    previousSign = sign
    repetitionCounter += 1

random.seed(0)

notDetectedCounter = 0
imageCounter = 1
#load and process data
for class_i in range(len(filePathsPerClassPerson)):
    for person_i in range(len(filePathsPerClassPerson[class_i])):
        for rep_i in range(len(filePathsPerClassPerson[class_i][person_i])):
            for r in range(2):  # jako czwarty for - najlepsze wyniki dla NUS II
                image = cv2.imread(filePathsPerClassPerson[class_i][person_i][rep_i])
                results = hands.process(image)
                if r == 0: #rozruch
                    continue
                rawData = rd.RawData(results,world=True)
				
                counter = 0
                while (not rawData.hasData) and (counter < 100):
				
                    dx = random.randint(0, 10)
                    dy = random.randint(0, 10)
                    M = np.float32([[1, 0, dx], [0, 1, dy]])
                    shifted = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
                    results = hands.process(shifted)
                    rawData = rd.RawData(results,world=True)
                    counter = counter+1

                if not rawData.hasData:
                    print("nie ma: class_number: " + signs[class_i] + ", person number: " + str(person_i+1), ", repetition_number: " + str(rep_i+1))
                    notDetectedCounter += 1
                    continue

                if results.multi_hand_landmarks:
                    for num, hand in enumerate(results.multi_hand_landmarks):
                        mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS,
                                                  mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                                                  mp_drawing.DrawingSpec(color=(121, 44, 76), thickness=2, circle_radius=2))
                cv2.imwrite("G:\\Tom\\Research\\MediaPipeData\\NUSII\\Output\\" + str(imageCounter) + ".png", image)
                imageCounter += 1

                outFilePath = outputDataFolder + "/" + signs[class_i] + "_" + str(person_i+1) + "_" + str(rep_i+1)
                a = 1
                with open(outFilePath, "wb") as outfile:
                    pickle.dump(rawData, outfile)

print(notDetectedCounter)