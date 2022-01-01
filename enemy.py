import pygame as pg
import math
from config import *
from mutation import *
from time import time

class EnemyManager:
	def __init__(self, game):
		self.mutations = {"E": [Goblin, Snowman], "D": [Zombie, Mummy], "C": [Cat, Fishman], "B": [Monkeyman], "A": [Golem], "S": [Dragon, Alien]}
		self.ranks = ["E", "D", "C", "B", "A", "S"]
		self.minRank = "E"
		self.maxRank = "D"
		self.enemies = []
		self.spawnEnemyTimer = time()
		self.EnemySpawnTime  = 4
		
	def update(self, game):
		if game.pausing:
			self.spawnEnemyTimer = time()
			return 
		self.updateRanks(game.timeAlive)
		if self.EnemySpawnTime and time()-self.spawnEnemyTimer>self.EnemySpawnTime:
			self.spawnEnemy(game)
		for enemy in self.enemies:
			enemy.update(game)
			if not enemy.alive:
				self.enemies.remove(enemy)
	
	def spawnEnemy(self, game):
		
		for i in range(random.randint(1, 3)):
			rank = self.ranks[random.randint(self.ranks.index(self.minRank), self.ranks.index(self.maxRank))]
			self.enemies.append(Enemy(game, random.choice(self.mutations[rank])))
		self.spawnEnemyTimer = time()
		
	def updateEnemySpawnTime(self, game):
		if len(self.enemies)<10:
			self.EnemySpawnTime = 2
		elif len(self.enemies)<15:
			self.EnemySpawnTime = 6
		else:
			self.EnemySpawnTime = None
	
	def restart(self):
		self.enemies = []
		self.minRank = "E"
		self.maxRank = "D"
			
	def updateRanks(self, timeAlive):
		if timeAlive<2*60:
			self.minRank = "E"
			self.maxRank = "D"
		elif timeAlive<3*60:
			self.minRank = "D"
			self.maxRank = "A"
		elif timeAlive<4*60:
			self.minRank = "B"
			self.maxRank = "A"
		else:
			self.minRank = "B"
			self.maxRank = "S"
	
	def show(self, screen, camera):
		for enemy in self.enemies:
			enemy.show(screen, camera)
		
class Enemy():
	def __init__(self, game, mutation):
		self.alive = True
		self.mutation = mutation()
		self.mutation.gun.isPlayer = False
		self.mutation.gun.cooldown *= random.uniform(1, 1.1)
		self.hitSound = pg.mixer.Sound("sounds/bullet_hit.wav")
		self.walkSpeed = self.mutation.walkSpeed
		self.lowSpeed = random.uniform(0.5, 0.7)
		self.fullSpeed = random.uniform(0.9, 0.1)	
		self.walkingAngle = random.randint(-180, 180)
		self.walkSpeed *= 0.8
		self.pos = pg.math.Vector2(game.player.pos.x+random.randint(-SIZE[0], SIZE[0]), game.player.pos.y+random.randint(-SIZE[1], SIZE[1]))
		self.Rect = pg.Rect((self.pos.x, self.pos.y, self.mutation.IMG.get_width(), self.mutation.IMG.get_height()))
		while game.player.collide(self.Rect, self.mutation.mask):
			self.pos = pg.math.Vector2(game.player.pos.x+random.randint(-SIZE[0], SIZE[1]), game.player.pos.y+random.randint(-SIZE[1], SIZE[1]))
			self.Rect = pg.Rect((self.pos.x, self.pos.y, self.mutation.IMG.get_width(), self.mutation.IMG.get_height()))
		self.direction = 1
	
	def __getstate__(self):
		state = self.__dict__.copy()
		state["hitSound"] = None
		#print(state)
		return state
	
	def __setstate__(self, state):
		state["hitSound"] = pg.mixer.Sound("sounds/bullet_hit.wav")
		self.__dict__.update(state)
	
	def update(self, game):
		self.mutation.gun.update(game, pg.math.Vector2(self.pos.x+self.mutation.IMG.get_width()/2, self.pos.y+self.mutation.IMG.get_height()/2))
		angleToPlayer = getAngle(self.pos, game.player.pos)+random.randint(-10, 10)
		self.pos.x += math.cos(math.radians(angleToPlayer))*-self.walkSpeed
		self.pos.y += math.sin(math.radians(angleToPlayer))*self.walkSpeed
		
		self.pos.x += math.cos(self.walkingAngle)*(((angleToPlayer-self.walkingAngle)/(angleToPlayer-self.walkingAngle))*(self.walkSpeed*0.6))
		self.pos.y += math.sin(self.walkingAngle)*(((angleToPlayer-self.walkingAngle)/(angleToPlayer-self.walkingAngle))*(self.walkSpeed*0.6))
		distanceToPlayer = self.pos-game.player.pos
		self.direction = distanceToPlayer.x>0
		if not self.inScreen(game.camera):
			self.walkSpeed = self.mutation.walkSpeed*1.5
		if not (abs(distanceToPlayer.x)<SIZE[0]*0.32 and abs(distanceToPlayer.y)<SIZE[1]*0.32):
			self.walkSpeed = self.mutation.walkSpeed*self.fullSpeed
			
		else:
			self.walkSpeed = self.mutation.walkSpeed*self.lowSpeed
		self.Rect = pg.Rect((self.pos.x, self.pos.y, self.mutation.IMG.get_width(), self.mutation.IMG.get_height())) 	
		if self.inScreen(game.camera):
				self.mutation.gun.shotBullet(pg.math.Vector2(self.pos.x+self.mutation.IMG.get_width()/2, self.pos.y+self.mutation.IMG.get_height()/2), angleToPlayer)
		if game.player.collide(self.Rect, self.mutation.mask):
			self.alive = False
			game.player.life -= self.mutation.gun.bulletDamage*3
			self.hitSound.play(0)
		if self.mutation.life<=0:
			self.alive = False
	
	def inScreen(self, camera):
		pos = self.pos-camera.pos
		return pos.x<SIZE[0] and pos.x+self.mutation.IMG.get_width()>0 and pos.y<SIZE[1] and pos.y+self.mutation.IMG.get_height()>0
		
	def show(self, screen, camera):
		self.mutation.show(self, camera, screen)
		
def getAngle(pos1, pos2):
	rel_x, rel_y = pos1.x-pos2.x, pos1.y-pos2.y
	angleradian = math.atan2(rel_y, rel_x)	

	angle = ((180/math.pi)*-angleradian)
	return angle