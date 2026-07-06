import math

class FeatureVector:
	def __init__(self):
		self.nodesX_world = list()
		self.nodesY_world = list()
		self.nodesZ_world = list()
		self.nodesX_world_norm = list()
		self.nodesY_world_norm = list()
		self.nodesZ_world_norm = list()
		self.rotationAngle = None

		#self.epsilonMahalanobis2D = 6
		self.epsilonMahalanobis3D = 9 #9 - best for models v.3
		#self.epsilonMahalanobis3D = 8.6  # 8.6 - best for massey digits