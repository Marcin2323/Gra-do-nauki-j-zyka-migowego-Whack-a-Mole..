import pickle
import cv2
import mediapipe as mp

videoDevice = cv2.VideoCapture(0)
width = videoDevice.get(cv2.CAP_PROP_FRAME_WIDTH)
height = videoDevice.get(cv2.CAP_PROP_FRAME_HEIGHT)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
#mp_drawing_styles = mp.solutions.drawing_styles
#DETECTION - POCZATKOWA, TRACKING - SLEDZACA / max_num_hands=4 zwieksza liczbe rak

hands = mp_hands.Hands(model_complexity=1,min_detection_confidence=0.5, min_tracking_confidence=0.5)

print('Place your hand, show the desired gesture and press spacebar each time when ready to save.')
print('Press Esc to quit.')

letter = "marcin"
person = "14"
repetition = 1
while videoDevice.isOpened():
	frame = videoDevice.read()[1]
	image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	image.flags.writeable = False
	results = hands.process(image)
	image.flags.writeable = True

	if results.multi_hand_landmarks:
		for num, hand in enumerate(results.multi_hand_landmarks):
			mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS,
			mp_drawing.DrawingSpec(color=(121,22,76),thickness=2,circle_radius=4),
			mp_drawing.DrawingSpec(color=(121,44,76),thickness=2,circle_radius=2))

	cv2.imshow('Video Preview', frame)

	key = cv2.waitKey(1)
	if key == ord(" "):
		# w przypadku nagrań nowego zbioru (innego niż models v3) zmienić na True
		# models v3 był nagrywany na False, więc do dogrywania nowych osób używać False
		rawData = rd.RawData(results, world=False)	with open(letter+"_"+person+"_"+str(repetition), "wb") as outfile:
			pickle.dump(rawData, outfile)
		repetition += 1
	elif key == 27:
		break

videoDevice.release()
cv2.destroyAllWindows()