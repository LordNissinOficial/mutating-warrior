from pygame import (Surface, transform, draw)
from config import *


class Fade:
	def __init__(self):
		self.fadeout = False
		self.fadein = False
		self.fading = False
		self.width = 32
		self.height = 16
		self.maxArea = self.height*1.1
		self.area = self.maxArea		
		self.fade = Surface((self.width, self.height)).convert()

			
	def fadeOut(self):
		self.fadeout = True
		self.area = self.maxArea
		self.fadein = False
		self.fading = True
	
	def update(self):
		
		if self.fadeout:			
			self.area -= 2
			
			if self.area<0:
				self.area = 0
				self.fadeout = False
				self.fadein = True
				
			return
		self.area += 2

		if self.area>self.maxArea:
			self.area = self.maxArea
			self.fadein = False
			self.fading = False

	def show(self, screen):
		#fade = Surface((1, 1)).convert()
		self.fade.fill(TRANSITIONCOLOR)
		draw.circle(self.fade, (24, 24, 24), (self.width/2, self.height/2), self.area)
		self.fade.set_colorkey((24, 24, 24))
		#self.fade.set_alpha(self.alpha)
		screen.blit(transform.scale(self.fade, screen.get_size()), (0, 0))