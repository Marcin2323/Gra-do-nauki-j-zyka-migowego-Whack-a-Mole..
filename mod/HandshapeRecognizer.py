import os
import pickle

import scipy as scipy

from mod import RawData as rd, DataProcessor as dt
import numpy as np

import sys
print(sys.version)
class HandshapeRecognizer:
	#kNN parameters
	k = 1
	useRepresentatives = False
	# metric: 0 - Euclidean, 1 - Euclidean squared, 2 city-block
	metric = 1
	#mahalanobis parameters
	allowableMismatches = 1 #Models v.3: 1, Massey: 0
	referenceNodeIndex = 0
	rotationNodeIndices = [0, 9]
	normalizationNodeIndices = [0, 9, 10] #without last two index finger joints
	#normalizationNodeIndices = [0, 9, 10, 11]  #without last index finger joint
	#normalizationNodeIndices = [0, 9, 10, 11, 12] #all finger joints

	#don't change this; these are initial values
	letterSpecificLimitations_models_v3 = False
	letterSpecificLimitations_massey_letters = False
	letterSpecificLimitations_massey_digits = False
	letterSpecificLimitations_nusII = False

	def __init__(self, dataset, modelFolder, subjects = None, gestures = None, check = False):
		match dataset:
			case "models v3":
				self.letterSpecificLimitations_models_v3 = True
			case "massey letters":
				self.letterSpecificLimitations_massey_letters = True
			case "massey digits":
				self.letterSpecificLimitations_massey_digits = True
			case "nus II":
				self.letterSpecificLimitations_nusII = True
			case _:
				raise Exception("HandshapeRecognizer: wrong dataset name: '"+dataset+"'")

		self.subjects = []
		self.classes = []
		self.subjectsUnique = []
		self.classesUnique = []
		if check: #only checking the number and list of subjects without loading files
			current_directory = os.path.dirname(os.path.abspath(__file__))

			# Ustaw ścieżkę względną do folderu 'Models'
			model_folder_path = os.path.join(current_directory, modelFolder)
			for path in os.listdir(model_folder_path):
				underscorePos = list(self.findAllSubstr(path, "_"))
				if len(underscorePos) < 2:
					raise Exception("Wrong file name: " + path)
				subject = path[underscorePos[0] + 1: underscorePos[1]]
				classLabel = path[:underscorePos[0]]
				self.subjects.append(subject)
				self.classes.append(path[:underscorePos[0]])
				if subjects and subject not in subjects: #load only subjects specified by subjects variable
					continue
				if gestures and classLabel not in gestures: #load only classes specified by gestures variable
					continue
				if subject not in self.subjectsUnique:
					self.subjectsUnique.append(subject)
				if classLabel not in self.classesUnique:
					self.classesUnique.append(classLabel)
			return
		self.templates = []

		current_directory = os.path.dirname(os.path.abspath(__file__))

		# Ustaw ścieżkę względną do folderu 'Models'
		model_folder_path = os.path.join(current_directory, modelFolder)
		for fileName in os.listdir(model_folder_path):
			with open(model_folder_path+"/"+fileName, "rb") as infile:
				underscorePos = list(self.findAllSubstr(fileName, "_"))
				if len(underscorePos) < 2:
					raise Exception("Wrong file name: " + fileName)
				subject = fileName[ underscorePos[0]+1 : underscorePos[1] ]
				classLabel = fileName[:underscorePos[0]]
				if subjects and subject not in subjects: #load only subjects specified by subjects variable
					continue
				if gestures and classLabel not in gestures: #load only classes specified by gestures variable
					continue
				self.subjects.append(subject)
				self.classes.append(classLabel)
				model = pickle.load(infile)
				self.templates.append(model)

		self.dataProcessor = dt.DataProcessor(self.referenceNodeIndex,self.rotationNodeIndices,self.normalizationNodeIndices)
		for index, rawData in enumerate(self.templates):
			featureVector = self.dataProcessor.calculateFeatureVector(rawData)
			self.templates[index] = featureVector
		#print(self.subjects)
		#print(self.classes)

	def createTemplatesDict(self):
		self.templatesDict = dict.fromkeys(self.classes) #key: class label, value: featureVector lists
		for index, vector in enumerate(self.templates):
			if not self.templatesDict[self.classes[index]]:
				self.templatesDict[self.classes[index]] = [vector]
			else:
				self.templatesDict[self.classes[index]].append(vector)

	def calculateCovMatricesAndClassRepresentatives(self):
		self.covMatrices = {} #key: class label, value: covariance matrices
		self.classRepresentatives = {} #key: class label, value: mean of that class features
		for label, vectors in self.templatesDict.items():
			classJoints = [[v.nodesX_world for v in vectors], [v.nodesY_world for v in vectors], [v.nodesZ_world for v in vectors]]
			classJoints = np.transpose(classJoints, (2, 1, 0))
			cov_mats = []
			reps = []
			for joints in classJoints:
				cov_mat = np.cov(joints,rowvar=False)
				if np.linalg.det(cov_mat):
					cov_mats.append( np.linalg.inv(cov_mat) ) #inverse covariance matrix
				else:
					cov_mats.append( np.linalg.pinv(cov_mat) ) #matrix is singular - use pseudo inverse instead
				reps.append(sum(joints)/len(joints))
			self.covMatrices[label] = cov_mats
			self.classRepresentatives[label] = reps

	def train(self):
		self.createTemplatesDict()
		self.calculateCovMatricesAndClassRepresentatives()

	def kNearestNeighbor(self, unknown, classes):
		#metric: 0 - Euclidean, 1 - Euclidean squared, 2 city-block
		distances = []
		for label in classes:
			if self.useRepresentatives:
				sum = 0
				for joint_i in range(len(self.classRepresentatives[label])):
					# 1. if initially recognized are O, S or S, T, then
					#   perform kNN only on small joint set
					templ_dict = self.classRepresentatives[label]
					if self.metric == 0 or self.metric == 1:
						sum += (unknown.nodesX_world[joint_i] - templ_dict[joint_i][0]) ** 2 + \
							(unknown.nodesY_world[joint_i] - templ_dict[joint_i][1]) ** 2 + \
							(unknown.nodesZ_world[joint_i] - templ_dict[joint_i][2]) ** 2
					else:
						sum += abs(unknown.nodesX_world[joint_i] - templ_dict[joint_i][0]) + \
							   abs(unknown.nodesY_world[joint_i] - templ_dict[joint_i][1]) + \
							   abs(unknown.nodesZ_world[joint_i] - templ_dict[joint_i][2])
					if self.metric == 1 or self.metric == 2:
						distances.append((label, sum))
					else:
						distances.append((label, sum ** 0.5))
			else: #don't use representatives
				sum = 0
				for template_i in range(len(self.templatesDict[label])):
					for joint_i in range(len(self.templatesDict[label][template_i].nodesX_world)):
						# 1. if initially recognized are O, S or S, T, then
						#  perform kNN only on small joint set

						if self.letterSpecificLimitations_models_v3:
							if (("O" in classes and "S" in classes) or ("S" in classes and "T" in classes)) \
								and (joint_i not in [3, 4, 8]):
								continue
						if self.letterSpecificLimitations_models_v3:
							if ("M" in classes and "E" in classes) \
								and (joint_i not in [20]):
								continue
						if self.letterSpecificLimitations_models_v3:
							if ("L" in classes and "C" in classes) \
								and (joint_i not in [8]):
								continue

						if self.letterSpecificLimitations_massey_digits:
							if ("4" in classes and "6" in classes) \
								and (joint_i not in [20]):
								continue
						if self.letterSpecificLimitations_massey_digits:
							if ("5" in classes and "6" in classes) \
								and (joint_i not in [4, 20]):
								continue
						if self.letterSpecificLimitations_massey_digits:
							if ("5" in classes and "8" in classes) \
								and (joint_i not in [4, 12]):
								continue
						if self.letterSpecificLimitations_massey_digits:
							if ("4" in classes and "9" in classes) \
								and (joint_i not in [8]):
								continue
						if self.letterSpecificLimitations_massey_digits:
							if ("2" in classes and "7" in classes) \
								and (joint_i not in [8, 12, 20]):
								continue

						templ_vect = self.templatesDict[label][template_i]
						if self.metric == 0 or self.metric == 1:
							sum += (unknown.nodesX_world[joint_i] - templ_vect.nodesX_world[joint_i]) ** 2 + \
								   (unknown.nodesY_world[joint_i] - templ_vect.nodesY_world[joint_i]) ** 2 + \
								   (unknown.nodesZ_world[joint_i] - templ_vect.nodesZ_world[joint_i]) ** 2
						else:
							sum += abs(unknown.nodesX_world[joint_i] - templ_vect.nodesX_world[joint_i]) + \
								   abs(unknown.nodesY_world[joint_i] - templ_vect.nodesY_world[joint_i]) + \
								   abs(unknown.nodesZ_world[joint_i] - templ_vect.nodesZ_world[joint_i])
					if self.metric == 1 or self.metric == 2:
						distances.append((label, sum))
					else:
						distances.append((label, sum ** 0.5))

		if self.k == 1 or self.useRepresentatives:
			return min(distances, key=lambda x: x[1])[0]
		elif self.k < 0:
			raise Exception("Wrong k value in kNN classifier.")
		#voting for the most common of all k classes
		distances.sort(key=lambda x: x[1])  # sort list by distances
		distances = distances[:self.k]
		classes = [d[0] for d in distances] #extract first column (class labels) from distances list
		return max(set(classes), key=classes.count)

	def run(self, unknown, isMediaPipeResult = False):
		if isMediaPipeResult:
			unknownRawData = rd.RawData(unknown)
			unknownFeatureVector = self.dataProcessor.calculateFeatureVector(unknownRawData)
		else:
			unknownFeatureVector = unknown
		#recognize potential classes by template matching using mahalanobis distance of each joint
		initiallyRecognized = []
		for label, representative in self.classRepresentatives.items():
			if abs(len(representative) != len(unknownFeatureVector.nodesX_world)):
				continue
			mismatchCounter = 0
			matches = True
			for t in range(len(representative)):
				unknownJoint = [unknownFeatureVector.nodesX_world[t],unknownFeatureVector.nodesY_world[t],unknownFeatureVector.nodesZ_world[t]]
				cov_mat = self.covMatrices[label][t]
				distance = scipy.spatial.distance.mahalanobis(unknownJoint, representative[t], cov_mat)
				if distance > unknownFeatureVector.epsilonMahalanobis3D:
					# the joint does not match
					mismatchCounter += 1
					if mismatchCounter > self.allowableMismatches:
						matches = False
						break
			if matches:
				initiallyRecognized.append(label)
		#if there are multiple potential classes, perform kNN classification using
		#class representatives (faster) or each class sample (more accurate);
		#use simple distances (Euclidean, Euclidean squared, city-block)
		if len(initiallyRecognized) < 1:
			return ""
		elif len(initiallyRecognized) == 1:
			return initiallyRecognized[0]
		else:
			return self.kNearestNeighbor(unknown=unknownFeatureVector, classes=initiallyRecognized)

	def findAllSubstr(self, a_str, sub):
		start = 0
		while True:
			start = a_str.find(sub, start)
			if start == -1: return
			yield start
			start += len(sub)  # use start += 1 to find overlapping matches