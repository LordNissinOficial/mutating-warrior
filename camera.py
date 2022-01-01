from pygame import math


class Camera():
	def __init__(self, x, y):
		self.pos = math.Vector2(x, y)
	
	def move(self, x, y):
		self.pos.x -= x
		self.pos.y -= y