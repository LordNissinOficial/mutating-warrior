import pygame as pg
from time import time
from config import *
import math
from random import randint

pg.mixer.init()

class Gun:
	def __init__(self, bulletDamage, bulletVel, bulletAngleOffsets, cooldown=0.1, bulletColor=None, isPlayer=True):
		self.bulletDamage = bulletDamage
		self.bulletVel = bulletVel
		self.bulletAngleOffsets = bulletAngleOffsets
		self.cooldown = cooldown
		self.cooldownTime = time()
		self.bullets = []
		self.bulletFiredSound = pg.mixer.Sound("sounds/bullet_fired.wav")
		self.bulletHitSound = pg.mixer.Sound("sounds/bullet_hit.wav")
		self.isPlayer = isPlayer
		self.bulletColor = bulletColor
			
	def __getstate__(self):
		state = self.__dict__.copy()
		state["bulletFiredSound"] = None
		state["bulletHitSound"] = None
		#print(state)
		return state
	
	def __setstate__(self, state):
		state["bulletFiredSound"] = pg.mixer.Sound("sounds/bullet_fired.wav")
		state["bulletHitSound"] = pg.mixer.Sound("sounds/bullet_hit.wav")
		self.__dict__.update(state)

	def update(self, game, pos):
		if game.pausing:
			self.cooldownTime = time()
			return 
			
		if self.isPlayer:
			#self.cooldownTime = time()
			if game.gunJoystick.pressed["bool"]:
				angle = game.gunJoystick.getAngle()
				self.shotBullet(pos, angle)

		for bullet in self.bullets:
			if not bullet.update():
				self.bullets.remove(bullet)
				continue
			if not self.isPlayer and bullet.collide(game.player):
				game.player.life -= bullet.damage
				if bullet in self.bullets:
					self.bullets.remove(bullet)
				self.bulletHitSound.play(0)
			elif self.isPlayer:
				for enemy in game.enemyManager.enemies:
					if bullet.collide(enemy):
						enemy.mutation.life -= self.bulletDamage
						if bullet in self.bullets:
							self.bullets.remove(bullet)
						self.bulletHitSound.play(0)
						
	def shotBullet(self, pos, angle):
		if time()-self.cooldownTime<self.cooldown: return
		self.cooldownTime = time()	
		for bulletAngleOffset in self.bulletAngleOffsets:			
			self.bullets.append(Bullet(self.bulletDamage, pos, angle+bulletAngleOffset, self.bulletVel, self.bulletColor))
		self.bulletFiredSound.play(0)
		
	def show(self, screen, camera):
		for bullet in self.bullets:
			bullet.show(screen, camera)
			
class Bullet:
	def __init__(self, damage, pos, angle, vel, color):
		self.damage = damage
		self.pos = pg.math.Vector2(pos.x, pos.y)
		self.color = color
		self.angle = angle
		self.vel = vel
		self.timeAlive = 0
		self.timeAliveTimer = time()
		self.lifetime = randint(2, 6)
		self.IMG = pg.image.load("sprites/bullet.png").convert_alpha()
		self.IMG.fill(self.color, special_flags=pg.BLEND_ADD)
		self.mask = pg.mask.from_surface(self.IMG)
		self.Rect = pg.Rect((self.pos.x, self.pos.y, self.IMG.get_width(), self.IMG.get_height()))
	
	def __getstate__(self):
		state = self.__dict__.copy()
		state["IMG"] = None
		state["mask"] = None
		#print(state)
		return state
	
	def __setstate__(self, state):
		state["IMG"] = pg.image.load("sprites/bullet.png").convert_alpha()
		state["IMG"].fill(state["color"], special_flags=pg.BLEND_ADD)
		state["mask"] = pg.mask.from_surface(state["IMG"])
		self.__dict__.update(state)
	
	def update(self):
		if time()-self.timeAliveTimer>=1:
			self.timeAlive += 1
			self.timeAliveTimer = time()
			if self.timeAlive>=self.lifetime:
				return False
		self.pos.x += math.cos(math.radians(self.angle))*-self.vel
		self.pos.y += math.sin(math.radians(self.angle))*self.vel
		self.Rect = pg.Rect((self.pos.x, self.pos.y, self.IMG.get_width(), self.IMG.get_height()))
		return True
		
	def collide(self, entitie):
		
		entitieRect = pg.Rect((entitie.pos.x, entitie.pos.y, entitie.mutation.IMG.get_width(), entitie.mutation.IMG.get_height()))
		offset_x = self.Rect.x - entitieRect.x
		offset_y = self.Rect.y - entitieRect.y
		return entitie.mutation.mask.overlap(self.mask, (offset_x, offset_y))
	
	def show(self, screen, camera):
		pos = self.pos-camera.pos
		if pos.x>SIZE[0] or pos.y>SIZE[1] or pos.y+self.IMG.get_height()<0 or pos.x+self.IMG.get_width()<0: return 
		
		screen.blit(self.IMG, pos)