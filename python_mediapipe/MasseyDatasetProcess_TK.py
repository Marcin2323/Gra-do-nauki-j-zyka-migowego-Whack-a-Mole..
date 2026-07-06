import os
import mediapipe as mp
import cv2
from mod import RawData as rd
import pickle
import numpy as np
import random

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0, min_tracking_confidence=0.5,static_image_mode=False,max_num_hands=1)
#best model complexity for Massey and NUS II = 0
#hands = mp_hands.Hands(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5,static_image_mode=True,max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils
loadDigits = True

datasetFolder = "D:\\Downloads\\Massey\\dataset" #UWAGA: skopiować zbiór do Downloads, bo w ścieżce opencv nie może być polskich liter (i być może też spacji)
if loadDigits:
    outputDataFolder = "D:/Praca - uczelnia/projekty/2023/gesty statyczne mediapipe/python_mediapipe/Models (różne wersje)/Massey digits"
else:
    outputDataFolder = "D:/Praca - uczelnia/projekty/2023/gesty statyczne mediapipe/python_mediapipe/Models (różne wersje)/Massey letters"

personsNumber = 5
if loadDigits:
    signs = '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
else:
    signs = 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'

filePathsPerClassPerson = [[None] * personsNumber for _ in range(len(signs))]
#load file paths
for fileName in os.listdir(datasetFolder):
    person = fileName[4]
    sign = fileName[6]

    #check whether the class represents a digit
    isDigit = False
    for i in range(10):
        if sign == str(i):
            isDigit = True
            break
    if isDigit and not loadDigits:
        continue
    elif not isDigit and loadDigits:
        continue

    if filePathsPerClassPerson[signs.index(sign)][int(person)-1] == None:
        filePathsPerClassPerson[signs.index(sign)][int(person)-1] = [datasetFolder + "\\" + fileName]
    else:
        filePathsPerClassPerson[signs.index(sign)][int(person)-1].append( datasetFolder + "\\" + fileName )

random.seed(0)

notDetectedCounter = 0
imageCounter = 1
#load and process data
for class_i in range(len(filePathsPerClassPerson)):
    for r in range(2):  #jako drugi for - najlepsze wyniki dla Massey digits i letters (jako pierwszy prawie tak samo dobrze)
        for person_i in range(len(filePathsPerClassPerson[class_i])):
            for rep_i in range(len(filePathsPerClassPerson[class_i][person_i])):
                image = cv2.imread(filePathsPerClassPerson[class_i][person_i][rep_i])
                results = hands.process(image)
                if r == 0: #rozruch
                    continue
                rawData = rd.RawData(results,world=True)

                counter = 0
                while (not rawData.hasData) and (counter < 5):
				
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
                if loadDigits:
                    cv2.imwrite("G:\\Tom\\Research\\MediaPipeData\\Massey\\Output\\Digits\\" + str(imageCounter) + ".png", image)
                else:
                    cv2.imwrite("G:\\Tom\\Research\\MediaPipeData\\Massey\\Output\\Letters\\" + str(imageCounter) + ".png", image)
                imageCounter += 1

                outFilePath = outputDataFolder + "/" + signs[class_i] + "_" + str(person_i+1) + "_" + str(rep_i+1)
                a = 1
                with open(outFilePath, "wb") as outfile:
                    pickle.dump(rawData, outfile)

print(notDetectedCounter)