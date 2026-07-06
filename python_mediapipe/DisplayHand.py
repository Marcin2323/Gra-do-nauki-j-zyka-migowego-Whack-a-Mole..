import cv2
import numpy as np
import mediapipe as mp
import pickle
from mod import RawData as rd

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# create a black image
width = 640
height = 480
img = np.zeros((height, width, 3), dtype = np.uint8)
file = open("../mod/Models/C_13_1", "rb")

'''width = 223
height = 322
img = np.zeros((height, width, 3), dtype = np.uint8)
file = open("D:/Praca - uczelnia/projekty/2023/gesty statyczne mediapipe/python_mediapipe/Models (różne wersje)/Massey digits/0_4_5", "rb")'''

model: rd.RawData = pickle.load(file)

for i in range(len(model.nodesX_world)):
    cv2.circle(img, (round(model.nodesX_world[i]*width), round(model.nodesY_world[i]*height)), 2, (255,255,255), 2)

cv2.imshow('Camera', img)
cv2.waitKey(0)