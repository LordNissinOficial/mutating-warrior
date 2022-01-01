import pygame as pg
import time
from guns import Gun
from mutation import Zombie
pg.init()

class Player:
	def __init__(self, x, y, mutation=Zombie):
		self.pos = pg.math.Vector2(x, y)
		self.mutation = mutation()
		self.direction = 0
		self.vel = None
		self.maxLife = 100
		self.life = self.maxLife
		self.maxMutationTime = 10
		self.mutationTime = 0
		self.mutationTimeTimer = time.time()
		self.receiveLiveTimer = time.time()
		
	def collide(self, Rect, mask):
		rect = pg.Rect(self.pos.x, self.pos.y, self.mutation.IMG.get_width(), self.mutation.IMG.get_height())
		offset_x = rect.x - Rect.x
		offset_y = rect.y - Rect.y
		if mask.overlap(self.mutation.mask, (offset_x, offset_y)):
			return True
		return False
		
	def update(self, game):
		if game.pausing:
			self.mutationTimeTimer = time.time()
			self.receiveLiveTimer = time.time()
			return 
		if time.time()-self.mutationTimeTimer>=1:
			self.mutationTimeTimer = time.time()
			self.mutationTime += 1
		if time.time()-self.receiveLiveTimer>=3:
			self.receiveLiveTimer = time.time()
			self.life = min(self.maxLife, self.life+1)
		self.mutation.update(game, self)
		
	def show(self, screen, camera):
		self.mutation.show(self, camera, screen)