class RawData:
	def __init__(self, mediaPipeResults, world=False):
		self.nodesCount = 21
		#Lists are named "node{X,Y,Z}_world" but in fact they are not always world coordinates.
		#It depends on "world" parameter.
		self.nodesX_world = list()
		self.nodesY_world = list()
		self.nodesZ_world = list()
		if world:
			if mediaPipeResults.multi_hand_world_landmarks:
				self.hasData = True
				for nodeIndex in range (self.nodesCount):
					node = mediaPipeResults.multi_hand_world_landmarks[0].landmark[nodeIndex]
					self.nodesX_world.append(node.x)
					self.nodesY_world.append(node.y)
					self.nodesZ_world.append(node.z)
			else:
				self.hasData = False
		else:
			if mediaPipeResults.multi_hand_landmarks:
				self.hasData = True
				for nodeIndex in range (self.nodesCount):
					node = mediaPipeResults.multi_hand_landmarks[0].landmark[nodeIndex]
					self.nodesX_world.append(node.x)
					self.nodesY_world.append(node.y)
					self.nodesZ_world.append(node.z)
			else:
				self.hasData = False