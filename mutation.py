import pygame as pg
from guns import Gun
import time, random

pg.mixer.init()

class MutationManager():
	def __init__(self):
		self.mutations = [Zombie, Mummy, Dragon, Cat, Goblin, Alien, Golem, Fishman, Monkeyman, Snowman]
		self.ranks = ["E", "D", "C", "B", "A", "S"]
		self.mutatingSound = pg.mixer.Sound("sounds/mutating.wav")
		
	def getRandomMutation(self):
		self.mutatingSound.play(0)
		return random.choice(self.mutations)()
	
	def update(self, game): pass
	
class Mutation():
	def __init__(self, name, walkSpeed, gun, life):
		self.life = life
		self.name = name
		self.IMG = pg.image.load("sprites/mutations/"+name+".png").convert_alpha()
		self.mask = pg.mask.from_surface(self.IMG)
		self.name = name		
		self.gun = gun 
		self.walkSpeed = walkSpeed
	
	def __getstate__(self):
		state = self.__dict__.copy()
		state["IMG"] = None
		state["mask"] = None
		#print(state)
		return state
	
	def __setstate__(self, state):
		state["IMG"] = pg.image.load("sprites/mutations/"+state["name"]+".png").convert_alpha()
		state["mask"] = pg.mask.from_surface(state["IMG"])
		self.__dict__.update(state)
		
	def update(self, game, player):
		self.gun.update(game, pg.math.Vector2(player.pos.x+self.IMG.get_width()/2, player.pos.y+self.IMG.get_height()/2))
		vel = game.moveJoystick.getValue()
		if vel.x>0.2:
			vel.x = max(vel.x, 0.4)
		elif vel.x<-0.2:
			vel.x = min(vel.x, -0.4)
		else:
			vel.x = 0
			
		if vel.y>0.2:
			vel.y = max(vel.y, 0.4)
		elif vel.y<-0.2:
			vel.y = min(vel.y, -0.4)
		else:
			vel.y = 0

		
		if game.gunJoystick.pressed["bool"]:
			valueX = game.gunJoystick.getValue().x
			if valueX>0:
				player.direction = 0
			elif valueX<0:
				player.direction = 1
		else:
			if vel.x>0:
				player.direction = 0
			elif vel.x<0:
				player.direction = 1
		player.pos.x += int(vel.x*self.walkSpeed)
		player.pos.y += int(vel.y*self.walkSpeed)
	
	def show(self, entitie, camera, screen):
		screen.blit(pg.transform.flip(self.IMG, entitie.direction, False), (entitie.pos.x-camera.pos.x, entitie.pos.y-camera.pos.y))
		self.gun.show(screen, camera)
		
class Zombie(Mutation):
	def __init__(self):
		Mutation.__init__(self, "zombie", 2.5, Gun(1, 4, [0], 0.4, (69, 225, 130)), 5)
		#bulletDamage, bulletVel, bulletAngleOffsets, cooldown=0.1, bulletColor=None
		
class Mummy(Mutation):
	def __init__(self):
		Mutation.__init__(self, "mummy", 3, Gun(2, 4, [0], 0.4, (108, 110, 0)), 10)
		
class Dragon(Mutation):
	def __init__(self):
		Mutation.__init__(self, "dragon", 3, Gun(3, 4, [-20, 10, 0, 20], 0.5, (108, 7, 0)), 20)
	
class Cat(Mutation):
	def __init__(self):
		Mutation.__init__(self, "cat", 2.5, Gun(2, 3, [0, 40], 0.5, (153, 79, 0)), 10)

class Goblin(Mutation):
	def __init__(self):
		Mutation.__init__(self, "goblin", 2.5, Gun(1, 3, [0], 0.3,  (69, 225, 130)), 5)

class Golem(Mutation):
	def __init__(self):
		Mutation.__init__(self, "golem", 2, Gun(10, 3.5, [0], 0.5,  (153, 79, 0)), 25)

class Fishman(Mutation):
	def __init__(self):
		Mutation.__init__(self, "fishman", 2.5, Gun(2, 3, [0, 10], 0.3,  (72, 206, 223)), 20)

class Monkeyman(Mutation):
	def __init__(self):
		Mutation.__init__(self, "monkeyman", 3, Gun(4, 4, [0, 10], 0.3,  (108, 7, 0)), 15)

class Snowman(Mutation):
	def __init__(self):
		Mutation.__init__(self, "snowman", 2.5, Gun(2, 3, [0], 0.3,  (174, 174, 174)), 5)

class Alien(Mutation):
	def __init__(self):
		Mutation.__init__(self, "alien", 3, Gun(4, 4, [-40, 0, 40], 0.5,  (199, 119, 254)), 20)