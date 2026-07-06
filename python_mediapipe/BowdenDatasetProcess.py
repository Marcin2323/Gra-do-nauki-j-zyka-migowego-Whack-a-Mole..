import os
import mediapipe as mp
import cv2
from mod import RawData as rd
import pickle

mp_hands = mp.solutions.hands
#hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
#best model complexity for Massey and NUS II = 0
hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0, min_tracking_confidence=0.5,static_image_mode=False,max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

datasetFolder = "D:\\Downloads\\Bowden\\dataset" #UWAGA: skopiować zbiór do Downloads, bo w ścieżce opencv nie może być polskich liter (i być może też spacji)
outputDataFolder = "D:/Praca - uczelnia/projekty/2023/gesty statyczne mediapipe/python_mediapipe/Models (różne wersje)/Bowden"

signs = 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y'
persons = 'A', 'B', 'C', 'D', 'E'
personsNumber = len(persons)

filePathsPerClassPerson = [[None] * personsNumber for _ in range(len(signs))] #[sign][person][repetition]
#load file paths
for p in persons:
    for s in signs:
        datasetSubFolder = datasetFolder + "\\" + p + "\\" + s
        for fileName in os.listdir(datasetSubFolder):
            if fileName[0] == "d": #omit depth files
                continue
            if filePathsPerClassPerson[signs.index(s)][persons.index(p)] == None:
                filePathsPerClassPerson[signs.index(s)][persons.index(p)] = [datasetSubFolder + "\\" + fileName]
            else:
                filePathsPerClassPerson[signs.index(s)][persons.index(p)].append( datasetSubFolder + "\\" + fileName )

notDetectedCounter = 0
imageCounter = 1
#load and process data
for class_i in range(len(filePathsPerClassPerson)):
    for r in range(2):
        for person_i in range(len(filePathsPerClassPerson[class_i])):
            for rep_i in range(len(filePathsPerClassPerson[class_i][person_i])):
                image = cv2.imread(filePathsPerClassPerson[class_i][person_i][rep_i])
                results = hands.process(image)
                if r == 0: #rozruch
                    continue
                rawData = rd.RawData(results,world=True)

                if not rawData.hasData:
                    print("nie ma: class_number: " + signs[class_i] + ", person number: " + str(person_i+1), ", repetition_number: " + str(rep_i+1))
                    notDetectedCounter += 1
                    continue

                if results.multi_hand_landmarks:
                    for num, hand in enumerate(results.multi_hand_landmarks):
                        mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS,
                                                  mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                                                  mp_drawing.DrawingSpec(color=(121, 44, 76), thickness=2, circle_radius=2))
                cv2.imwrite("D:\\Downloads\\Bowden\\output\\" + str(imageCounter) + ".png", image)
                imageCounter += 1

                outFilePath = outputDataFolder + "/" + signs[class_i] + "_" + str(person_i+1) + "_" + str(rep_i+1)
                a = 1
                with open(outFilePath, "wb") as outfile:
                    pickle.dump(rawData, outfile)

print(notDetectedCounter)
