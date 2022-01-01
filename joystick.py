import pygame as pg
from config import *
from math import (cos, sin, radians, pi, atan2)

class Joystick():
	def __init__(self, x, y, area):
		self.handleColor = (100, 176, 254)
		self.joystickColor = (100, 176, 254)
		self.outlineColor = (0, 0, 0)
		self.pos = pg.math.Vector2(x, y)
		self.handlePos =pg.math.Vector2(x, y)
		self.area = area
		self.pressed = {"bool": False, "id": None}

	def getValue(self):
		value = pg.math.Vector2(0, 0)
		value.x = (self.handlePos.x-self.pos.x)/self.area
		value.y = (self.handlePos.y-self.pos.y)/self.area
		return value
	
	def getAngle(self):
		return getAngle(self.pos, self.handlePos)
	
	def update(self, game):
		if game.pausing: return
		self.handleEvents(game)
		
	def handleEvents(self, game):
		for key in game.fingers:
			finger = game.fingers[key]
			if self.pressed["bool"]:
				if finger["id"]!=self.pressed["id"]: continue

			if finger["tipo"]=="not pressed":
				self.handlePos = self.pos
				self.pressed = {"bool": False, "id": None}
	
			if finger["x"]<self.pos.x+self.area and finger["x"]>self.pos.x-self.area and finger["y"]<self.pos.y+self.area and finger["y"]>self.pos.y-self.area:
				self.pressed = {"bool": True, "id": finger["id"]}
				self.handlePos = pg.math.Vector2(finger["x"], finger['y'])			
				
				if finger["tipo"] == "not pressed":
					self.handlePos = self.pos
					self.pressed = {"bool": False, "id": None}
					continue
				
			elif finger["id"]==self.pressed["id"]:
				angle = radians(-getAngle(pg.math.Vector2(finger['x'], finger['y']), self.pos))
				self.handlePos = pg.math.Vector2(self.pos.x+cos(angle)*self.area, self.pos.y+sin(angle)*self.area)
			if self.handlePos.x > self.pos.x+self.area: self.handlePos.x = self.pos.x+self.area
			if self.handlePos.y > self.pos.y+self.area: self.handlePos.y = self.pos.y+self.area
			if self.handlePos.x< self.pos.x-self.area: self.handlePos.x = self.pos.x-self.area
			if self.handlePos.y< self.pos.y-self.area: self.handlePos.y = self.pos.y-self.area
				
	def show(self, screen):
		pg.draw.circle(screen, self.outlineColor, (self.pos.x, self.pos.y), self.area+2, 8)
		pg.draw.circle(screen, self.joystickColor, (self.pos.x, self.pos.y), self.area, 4)
		pg.draw.circle(screen, self.outlineColor, (self.handlePos.x, self.handlePos.y), int(self.area/4)+2)
		pg.draw.circle(screen, self.handleColor, (self.handlePos.x, self.handlePos.y), int(self.area/4))

def getAngle(pos1, pos2):
	rel_x, rel_y = pos1.x-pos2.x, pos1.y-pos2.y
	angleradian = atan2(rel_y, rel_x)	

	angle = ((180/pi)*-angleradian)
	return angle