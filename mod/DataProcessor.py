from mod import FeatureVector as fv
import math

class DataProcessor:

	def __init__(self, referenceNodeIndex, rotationNodeIndices, normalizationNodeIndices):
		self.referenceNodeIndex = referenceNodeIndex
		self.rotationNodeIndices = rotationNodeIndices
		self.normalizationNodeIndices = normalizationNodeIndices

	def calculateFeatureVector(self, rawData):
		featureVector = fv.FeatureVector()
		if rawData.hasData == True:
			for nodeIndex in range (rawData.nodesCount):
				featureVector.nodesX_world.append(rawData.nodesX_world[nodeIndex] - rawData.nodesX_world[self.referenceNodeIndex])
				featureVector.nodesY_world.append(-(rawData.nodesY_world[nodeIndex] - rawData.nodesY_world[self.referenceNodeIndex]))
				featureVector.nodesZ_world.append(rawData.nodesZ_world[nodeIndex] - rawData.nodesZ_world[self.referenceNodeIndex])

			currentOrientation = math.atan2(featureVector.nodesY_world[self.rotationNodeIndices[1]] -
											featureVector.nodesY_world[self.rotationNodeIndices[0]],
											featureVector.nodesX_world[self.rotationNodeIndices[1]] -
											featureVector.nodesX_world[self.rotationNodeIndices[0]])
			desiredOrientation = math.pi/2
			rotationAngle = desiredOrientation - currentOrientation
			featureVector.rotationAngle = rotationAngle
			for nodeIndex in range (rawData.nodesCount):
				x = featureVector.nodesX_world[nodeIndex] * math.cos(rotationAngle) - featureVector.nodesY_world[nodeIndex] * math.sin(rotationAngle)
				y = featureVector.nodesX_world[nodeIndex] * math.sin(rotationAngle) + featureVector.nodesY_world[nodeIndex] * math.cos(rotationAngle)
				featureVector.nodesX_world[nodeIndex] = x
				featureVector.nodesY_world[nodeIndex] = y

			normalizationDistance_world = 0.0
			for nodeIndex in range(len(self.normalizationNodeIndices)-1):
				normalizationDistance_world += self.euclidesDistance3D(
				featureVector.nodesX_world[self.normalizationNodeIndices[nodeIndex]],
				featureVector.nodesY_world[self.normalizationNodeIndices[nodeIndex]],
				featureVector.nodesZ_world[self.normalizationNodeIndices[nodeIndex]],
				featureVector.nodesX_world[self.normalizationNodeIndices[nodeIndex+1]],
				featureVector.nodesY_world[self.normalizationNodeIndices[nodeIndex+1]],
				featureVector.nodesZ_world[self.normalizationNodeIndices[nodeIndex+1]])
			for nodeIndex in range (rawData.nodesCount):
				featureVector.nodesX_world[nodeIndex] = featureVector.nodesX_world[nodeIndex]/normalizationDistance_world
				featureVector.nodesY_world[nodeIndex] = featureVector.nodesY_world[nodeIndex]/normalizationDistance_world
				featureVector.nodesZ_world[nodeIndex] = featureVector.nodesZ_world[nodeIndex]/normalizationDistance_world
		return featureVector
	
	def euclidesDistance2D(self, x1, y1, x2, y2):
		distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
		return distance

	def euclidesDistance3D(self, x1, y1, z1, x2, y2, z2):
		distance = math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
		return distance