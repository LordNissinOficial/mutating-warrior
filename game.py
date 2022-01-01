import pygame as pg
import pickle
from random import randint
from config import *
from player import Player
from joystick import Joystick
from camera import Camera
from time import time
from mutation import MutationManager
from enemy import EnemyManager
from transition import Fade
from enum import Enum
import sys

pg.init()
pg.font.init()

class SceneManager:
	def __init__(self):
		self.state = STATES.INTRO
		self.fade = Fade()
		self.deltatime = 0
		self.oldScene = None
		self.scene = None
		self.running = True
		self.events = []
		
	def setScene(self, state):
		self.state  = state
		self.setUp()

	def setUp(self):
		if self.scene:
			self.scene.exit()
		self.oldScene = self.scene
		self.scene = STATES.states.value[self.state.value]()
		
		if self.oldScene:
			self.fade.fadeOut()

	def update(self):
		if not self.running: return
		self.events = pg.event.get()
		if self.fade.fading:
			if self.fade.fadeout:
				self.fade.update()
				if self.fade.fadein:
					self.scene.show()					
				return
			else:
				self.fade.update()
		self.scene.update(self)

	def show(self, screen):
		if not self.running: return
		if self.fade.fading:			
			if self.fade.fadeout:
				displayCopy = self.oldScene.surface.copy()
			else:
				displayCopy = self.scene.surface.copy()

			self.fade.show(displayCopy)
			screen.blit(pg.transform.scale(displayCopy, screen.get_size()), (0, 0))
			return
		self.scene.show()
		screen.blit(pg.transform.scale(self.scene.surface, screen.get_size()), (0, 0))
		
class Game:
	def __init__(self):
		self.surface = pg.Surface(SIZE).convert()
		self.running = True
		self.fingers = {}
		self.clickSound = pg.mixer.Sound("sounds/hit.wav")
		self.pausing = False
		self.pausingText = "pausing."
		self.font = pg.font.Font("ThaleahFat.ttf", 20)
		self.outlinedCharacters = self.outlineCharacters()
		self.pausingBackgroundIMG = pg.transform.scale(pg.image.load("sprites/pause_background.png").convert_alpha(), (int(SIZE[0]/2*1), int(SIZE[1]/2*1)))
		self.pausingButtonIMG = pg.image.load("sprites/pause_button.png").convert_alpha()
		data = pickle.load(open("save.data", "rb"))
		self.restartButtonIMG = pg.image.load("sprites/restart_button.png").convert_alpha()
		self.homeButtonIMG = pg.image.load("sprites/home_button.png").convert_alpha()
		self.continueButtonIMG = pg.image.load("sprites/continue_button.png").convert_alpha()
		if data[0]:
			self.timeAlive = data[0]
			self.player = data[1]
			self.camera = data[2]
			self.enemyManager = data[3]
			self.highestTimeAlive = data[4]
			self.pausing = data[5]
		else:
			self.timeAlive = 0
			self.player = Player(randint(0, SIZE[0]), randint(0, SIZE[1]))
			self.camera = Camera(0, 0)			
			self.enemyManager = EnemyManager(self)
			self.highestTimeAlive = 0
		if self.player.life <= 0:
			self.restart()
		self.timeAliveTimer = time()			
		self.mutationManager = MutationManager()		
		self.lifeBarIMG = pg.transform.scale(pg.image.load("sprites/life_bar.png").convert(), (128, 32))
		self.lifeBarIMG.set_colorkey((118, 39, 255))
		self.mutationBarIMG = pg.transform.scale(pg.image.load("sprites/mutation_bar.png").convert(), (128, 16))
		self.mutationBarIMG.set_colorkey((118, 39, 255))
		self.moveJoystick = Joystick(50, SIZE[1]-50, 40)
		self.gunJoystick = Joystick(SIZE[0]-50, SIZE[1]-50, 40)
		self.floorIMG = pg.transform.scale(pg.image.load("sprites/floor.png").convert(), (32, 32))
		self.floorColor = [87, 29, 0]
		self.floorIMG.fill(self.floorColor, special_flags=pg.BLEND_ADD)		
		
	def restart(self):
		self.timeAlive = 0
		self.timeAliveTimer = time()
		self.player = Player(randint(0, SIZE[0]), randint(0, SIZE[1]))
		self.enemyManager.restart()
	
	def exit(self):
		pickle.dump([None, None, None, None, self.highestTimeAlive, None], open("save.data", "wb"))
		
	def save(self):
		pickle.dump([self.timeAlive, self.player, self.camera, self.enemyManager, self.highestTimeAlive, self.pausing], open("save.data", "wb"))
		
	def update(self, sceneManager):
		if self.pausing:
			self.timeAliveTimer = time()
			self.handleEvents(sceneManager)

		if self.timeAlive>self.highestTimeAlive:
			self.highestTimeAlive = self.timeAlive

		if self.player.mutationTime>=self.player.maxMutationTime:
			self.player.mutation = self.mutationManager.getRandomMutation()
			self.player.mutationTime = 0
		if time()-self.timeAliveTimer>=1:
			self.timeAliveTimer = time()
			self.timeAlive += 1
		self.player.update(self)
		self.moveJoystick.update(self)
		self.gunJoystick.update(self)
		self.camera.move((self.camera.pos.x-(self.player.pos.x-SIZE[0]/2))/8, (self.camera.pos.y-(self.player.pos.y-SIZE[1]/2))/8)
		self.enemyManager.update(self)
		if self.player.life <= 0:
			if not self.pausing:
				self.clickSound.play(0)
				self.pausingText = "you died."
				self.pausing = True
						
		self.handleEvents(sceneManager)
	
	def convertTimeAlive(self, timeInSeconds):
		minute = str(int(timeInSeconds/60))
		if len(minute)==1:
			minute = "0"+minute
		second = str(int(timeInSeconds-int(timeInSeconds/60)*60))
		if len(second)==1:
			second = "0"+second

		return f"{minute}.{second}"
		
	def show(self):
		self.showBackground()
		self.enemyManager.show(self.surface, self.camera)
		self.player.show(self.surface, self.camera)		
		self.moveJoystick.show(self.surface)
		self.gunJoystick.show(self.surface)
		self.showLifeBar()
		self.showMutationBar()
		self.showTimeAlive()
		if self.pausing:
			self.showPausing()
	
	def outlineCharacters(self):
		chars = "abcdefghijklmnopqrstuvwxyz0123456789:. "
		charsSurfaces = []
		for char in chars:
			charsSurfaces.append(self.outlineChar(char))
		return charsSurfaces
	
	def outlineText(self, text):
		if len(text)==0:
			return pg.Surface((0, 0))
		charsSurfaces = []
		charsCopy = "abcdefghijklmnopqrstuvwxyz0123456789:. "
		for char in text:
			charsSurfaces.append(self.outlinedCharacters[charsCopy.index(char)])
		width = 0
		for charSurface in charsSurfaces:
			width += charSurface.get_width()
		height = charSurface.get_height()
		surface = pg.Surface((width, height))
		surface.fill((23, 23, 23))
		x = 0
		for charSurface in charsSurfaces:
			surface.blit(charSurface, (x, 0))
			x += charSurface.get_width()
		surface.set_colorkey((23, 23, 23))
		return surface
		
	def outlineChar(self, text, spacing=2):
		textWidth, textHeight = self.font.size(text)
		surface  = pg.Surface((textWidth+2*len(text)+spacing*len(text), textHeight+2))
		surface.fill((243, 243, 0))
		currentX = 0
		for i in range(len(text)):
			char = text[i]
			textSurface = pg.Surface((textWidth+2, textHeight+2))
			charWidth, charHeight = self.font.size(char)
			textSurface.fill((243, 243, 0))
			textSurface.blit(self.font.render(char, 0, (254, 254, 254)).convert_alpha(), (1, 1))
			for y in range(textSurface.get_height()):
				for x in range(textSurface.get_width()):
					color = textSurface.get_at((x, y))
					if color==(254, 254, 254):
						continue
					for direction in [[0, 1], [1, 0], [-1, 0], [0, -1]]:
						if not (x+direction[0]>=0 and x+direction[0]<textSurface.get_width() and y+direction[1]>=0 and y+direction[1]<textSurface.get_height()):
							continue
					#	if i==0:
#							print((x+direction[0], y+direction[1]))
						if textSurface.get_at((x+direction[0], y+direction[1]))==(254, 254, 254):
							textSurface.set_at((x, y), (0, 0, 0))
							break
			surface.blit(textSurface, (currentX, 0))
			currentX += charWidth+spacing
		surface.set_colorkey((243, 243, 0))
		return surface
		
	def showPausing(self):
		backdrop = pg.Surface(SIZE)
		backdrop.set_alpha(150)
		self.surface.blit(backdrop, (0, 0))
		x = SIZE[0]/2-self.pausingBackgroundIMG.get_width()/2
		y = SIZE[1]/2-self.pausingBackgroundIMG.get_height()/2

		self.surface.blit(self.pausingBackgroundIMG, (x, y))
		pausingTextRender = self.outlineText(self.pausingText)
		self.surface.blit(pausingTextRender, (x+self.pausingBackgroundIMG.get_width()/2-pausingTextRender.get_width()/2, y+20))
		highscoreRender = self.outlineText(f"high:{self.convertTimeAlive(self.highestTimeAlive)}")
		self.surface.blit(highscoreRender, (x+self.pausingBackgroundIMG.get_width()/2-highscoreRender.get_width()/2, y+6))
		self.surface.blit(self.homeButtonIMG, (x+35, y+self.pausingBackgroundIMG.get_height()-40))
		self.surface.blit(self.continueButtonIMG, (x+77, y+self.pausingBackgroundIMG.get_height()-40))
		self.surface.blit(self.restartButtonIMG, (x+119, y+self.pausingBackgroundIMG.get_height()-40))
		
	def showTimeAlive(self):
		timeAliveRender = self.outlineText(self.convertTimeAlive(self.timeAlive))
		self.surface.blit(timeAliveRender, (SIZE[0]/2-timeAliveRender.get_width()/2, 2))
		
	def showMutationBar(self):
		mutationBar = pg.Surface(self.mutationBarIMG.get_size()).convert_alpha()
		mutationBar.fill((100, 100, 100))

		pg.draw.rect(mutationBar, (69, 225, 130), (2, 0, int((self.player.mutationTime)/self.player.maxMutationTime*(self.mutationBarIMG.get_width()-4)), self.mutationBarIMG.get_height()))
		mutationBar.blit(self.mutationBarIMG, (0, 0))
		mutationBar.set_alpha(200)
		mutationBar.set_colorkey((59, 0, 164))
		self.surface.blit(mutationBar, (2, 37))
	
	def showLifeBar(self):
		lifeBar = pg.Surface(self.lifeBarIMG.get_size()).convert_alpha()
		lifeBar.fill((100, 100, 100))
		pg.draw.rect(lifeBar, (181, 50, 32), (2, 0, int(self.player.life/self.player.maxLife*(self.lifeBarIMG.get_width()-4)), self.lifeBarIMG.get_height()))
		self.surface.blit(self.pausingButtonIMG, (SIZE[0]-40, 2))
		lifeBar.blit(self.lifeBarIMG, (0, 0))
		lifeBar.set_alpha(200)
		lifeBar.set_colorkey((59, 0, 164))
		self.surface.blit(lifeBar, (2, 4))
		
	def showBackground(self):		
		for y in range(int(self.surface.get_height()/self.floorIMG.get_height())+2):
			for x in range(int(self.surface.get_width()/self.floorIMG.get_width())+2):

				self.surface.blit(self.floorIMG, ((x-1)*self.floorIMG.get_width()-self.camera.pos.x%self.floorIMG.get_width(), (y-1)*self.floorIMG.get_height()-self.camera.pos.y%self.floorIMG.get_height()))

	def handleEvents(self, sceneManager):
		for event in sceneManager.events:
			if event.type==pg.QUIT:
				self.save()
				self.running = False
				pg.display.quit()
				pg.quit()
				sys.exit()
			if event.type==pg.FINGERDOWN:
				self.fingers[event.finger_id] = {"id": event.finger_id, "x": event.x*SIZE[0], "y": event.y*SIZE[1], "tipo": "pressed"}
			elif event.type==pg.FINGERMOTION: 
				self.fingers[event.finger_id] = {"id": event.finger_id, "x": event.x*SIZE[0], "y": event.y*SIZE[1], "tipo": "moving"}
			elif event.type==pg.FINGERUP: 
				self.fingers[event.finger_id] = {"id": event.finger_id, "x": event.x*SIZE[0], "y": event.y*SIZE[1], "tipo": "not pressed"}
				pausingButtonRect = pg.Rect((SIZE[0]-40, 2, 16, 16))
				if not self.pausing and pausingButtonRect.collidepoint([self.fingers[event.finger_id]["x"], self.fingers[event.finger_id]["y"]]):
					self.pausing = True
					self.clickSound.play(0)
					
				if self.pausing:
					x = SIZE[0]/2-self.pausingBackgroundIMG.get_width()/2
					y = SIZE[1]/2-self.pausingBackgroundIMG.get_height()/2
					homeButtonRect = pg.Rect((x+35, y+self.pausingBackgroundIMG.get_height()-40, 32, 32))
					continueButtonRect = pg.Rect((x+77, y+self.pausingBackgroundIMG.get_height()-40, 32, 32))
					restartButtonRect = pg.Rect((x+119, y+self.pausingBackgroundIMG.get_height()-40, 32, 32))
					if homeButtonRect.collidepoint([self.fingers[event.finger_id]["x"], self.fingers[event.finger_id]["y"]]):
						sceneManager.setScene(STATES.MAINMENU)						
						self.clickSound.play(0)
					elif continueButtonRect.collidepoint([self.fingers[event.finger_id]["x"], self.fingers[event.finger_id]["y"]]):
						if self.player.life>0:
							self.pausing = False
						self.clickSound.play(0)						
					elif restartButtonRect.collidepoint([self.fingers[event.finger_id]["x"], self.fingers[event.finger_id]["y"]]):
						self.pausing = False
						self.restart()
						self.clickSound.play(0)
					
class MainMenu:
	def __init__(self):
		self.surface = pg.Surface(SIZE).convert()
		
		self.mutationsIMG = pg.Surface(SIZE)
		self.mutationsIMG.fill((23, 24, 25))
		self.mutationsIMG.blit(pg.transform.scale(pg.image.load("sprites/main_menu.png"), SIZE), (0, 0))
		self.mutationsIMG.set_colorkey((23, 24, 25))
		self.backgroundIMG = pg.transform.scale(pg.image.load("sprites/floor.png").convert(), (32, 32))
		self.font = pg.font.Font("ThaleahFat.ttf", 20)
		self.outlinedCharacters = self.outlineCharacters()
		self.backgroundIMG.fill((21, 95, 218), special_flags=pg.BLEND_ADD)		
		self.backgroundPos = pg.math.Vector2(0, 0)
		self.backgroundSpeed = -0.5
		self.textOpacity = 255
		self.textOpacityVel = 16
		self.startRender = self.outlineText("click to start.")
		data = pickle.load(open("save.data", "rb"))
		if data[0]:
			self.highscoreRender = self.outlineText("high:"+self.convertTimeAlive(data[4]))
		else:
			self.highscoreRender = self.outlineText("high:00.00")
		self.clickSound = pg.mixer.Sound("sounds/hit.wav")
	
	def exit(self):
		pass

	def convertTimeAlive(self, timeAlive):
		minute = str(int(timeAlive/60))
		if len(minute)==1:
			minute = "0"+minute
		second = str(int(timeAlive-int(timeAlive/60)*60))
		if len(second)==1:
			second = "0"+second

		return f"{minute}.{second}"
		
	def update(self, sceneManager):
		self.backgroundPos.x += self.backgroundSpeed
		self.backgroundPos.y += self.backgroundSpeed
		self.textOpacity += self.textOpacityVel
		if self.textOpacity<=0 or self.textOpacity>=255:
			self.textOpacityVel *= -1
			self.textOpacity = min(max(self.textOpacity, 0), 255)
		
		self.handleEvents(sceneManager)
	
	def outlineCharacters(self):
		chars = "abcdefghijklmnopqrstuvwxyz0123456789:. "
		charsSurfaces = []
		for char in chars:
			charsSurfaces.append(self.outlineChar(char))
		return charsSurfaces
	
	def outlineText(self, text):
		charsSurfaces = []
		charsCopy = "abcdefghijklmnopqrstuvwxyz0123456789:. "
		for char in text:
			charsSurfaces.append(self.outlinedCharacters[charsCopy.index(char)])
		width = 0
		for charSurface in charsSurfaces:
			width += charSurface.get_width()
		height = charSurface.get_height()
		surface = pg.Surface((width, height))
		surface.fill((23, 23, 23))
		x = 0
		for charSurface in charsSurfaces:
			surface.blit(charSurface, (x, 0))
			x += charSurface.get_width()
		surface.set_colorkey((23, 23, 23))
		return surface
		
	def outlineChar(self, text, spacing=2):
		textWidth, textHeight = self.font.size(text)
		surface  = pg.Surface((textWidth+2*len(text)+spacing*len(text), textHeight+2))
		surface.fill((243, 243, 0))
		currentX = 0
		for i in range(len(text)):
			char = text[i]
			textSurface = pg.Surface((textWidth+2, textHeight+2))
			charWidth, charHeight = self.font.size(char)
			textSurface.fill((243, 243, 0))
			textSurface.blit(self.font.render(char, 0, (254, 254, 254)).convert_alpha(), (1, 1))
			for y in range(textSurface.get_height()):
				for x in range(textSurface.get_width()):
					color = textSurface.get_at((x, y))
					if color==(254, 254, 254):
						continue
					for direction in [[0, 1], [1, 0], [-1, 0], [0, -1]]:
						if not (x+direction[0]>=0 and x+direction[0]<textSurface.get_width() and y+direction[1]>=0 and y+direction[1]<textSurface.get_height()):
							continue
					#	if i==0:
#							print((x+direction[0], y+direction[1]))
						if textSurface.get_at((x+direction[0], y+direction[1]))==(254, 254, 254):
							textSurface.set_at((x, y), (0, 0, 0))
							break
			surface.blit(textSurface, (currentX, 0))
			currentX += charWidth+spacing
		surface.set_colorkey((243, 243, 0))
		return surface
		
	def show(self):
		self.showBackground()
		startRender = self.startRender
		startRender.set_alpha(self.textOpacity)
		self.surface.blit(self.mutationsIMG, (0, 0))
		self.surface.blit(startRender, (SIZE[0]/2-startRender.get_width()/2, SIZE[1]-20))		
		self.surface.blit(self.highscoreRender, (4, 2))
		
	def showBackground(self):
		for y in range(int(self.surface.get_height()/self.backgroundIMG.get_height())+2):
			for x in range(int(self.surface.get_width()/self.backgroundIMG.get_width())+2):
				tileX = (x-1)*self.backgroundIMG.get_width()-self.backgroundPos.x%self.backgroundIMG.get_width()
				tileY = (y-1)*self.backgroundIMG.get_height()-self.backgroundPos.y%self.backgroundIMG.get_height()
				self.surface.blit(self.backgroundIMG, (tileX, tileY))
	
	def handleEvents(self, sceneManager):
		for event in sceneManager.events:
			if event.type==pg.QUIT:
				self.running = False
				pg.display.quit()
				pg.quit()
				sys.exit()
			elif event.type==pg.MOUSEBUTTONUP:
				sceneManager.setScene(STATES.GAME)
				self.clickSound.play(0)

class Intro:
	def __init__(self):
		self.surface = pg.Surface(SIZE)
		self.nextButtonIMG =pg.transform.scale(pg.image.load("sprites/next_button.png").convert_alpha(), (32, 32))
		self.font = pg.font.Font("ThaleahFat.ttf", 16)
		self.outlinedCharacters = self.outlineCharacters()
		self.frames = self.getIntroFrames()
		self.texts = [[self.outlineText("in one fateful day.")], [self.outlineText("our hero was at work.")], [self.outlineText("when suddenly"), self.outlineText("monsters invaded!")], [self.outlineText("and because of the broken reactor"), self.outlineText("our hero began to mutate!")], [self.outlineText("now he must defeat"), self.outlineText("all the monsters!")]]
		self.currentFrame = 0
		self.nextButtonOpacity = 255
		self.nextButtonOpacityChange = 255/15
		self.clickSound = pg.mixer.Sound("sounds/hit.wav")
		
	def getIntroFrames(self):
		frames = []
		for i in range(1, 6):
			frames.append(pg.transform.scale(pg.image.load(f"sprites/intro/frame_{i}.png"), SIZE).convert())
		return frames
	
		
	def outlineCharacters(self):
		chars = "abcdefghijklmnopqrstuvwxyz0123456789!:. "
		charsSurfaces = []
		for char in chars:
			charsSurfaces.append(self.outlineChar(char))
		return charsSurfaces
	
	def outlineText(self, text):
		charsSurfaces = []
		charsCopy = "abcdefghijklmnopqrstuvwxyz0123456789!:. "
		for char in text:
			charsSurfaces.append(self.outlinedCharacters[charsCopy.index(char)])
		width = 0
		for charSurface in charsSurfaces:
			width += charSurface.get_width()
		height = charSurface.get_height()
		surface = pg.Surface((width, height))
		surface.fill((23, 23, 23))
		x = 0
		for charSurface in charsSurfaces:
			surface.blit(charSurface, (x, 0))
			x += charSurface.get_width()
		surface.set_colorkey((23, 23, 23))
		return surface
		
	def outlineChar(self, text, spacing=2):
		textWidth, textHeight = self.font.size(text)
		surface  = pg.Surface((textWidth+2*len(text)+spacing*len(text), textHeight+2))
		surface.fill((243, 243, 0))
		currentX = 0
		for i in range(len(text)):
			char = text[i]
			textSurface = pg.Surface((textWidth+2, textHeight+2))
			charWidth, charHeight = self.font.size(char)
			textSurface.fill((243, 243, 0))
			textSurface.blit(self.font.render(char, 0, (254, 254, 254)).convert_alpha(), (1, 1))
			for y in range(textSurface.get_height()):
				for x in range(textSurface.get_width()):
					color = textSurface.get_at((x, y))
					if color==(254, 254, 254):
						continue
					for direction in [[0, 1], [1, 0], [-1, 0], [0, -1]]:
						if not (x+direction[0]>=0 and x+direction[0]<textSurface.get_width() and y+direction[1]>=0 and y+direction[1]<textSurface.get_height()):
							continue
					#	if i==0:
#							print((x+direction[0], y+direction[1]))
						if textSurface.get_at((x+direction[0], y+direction[1]))==(254, 254, 254):
							textSurface.set_at((x, y), (0, 0, 0))
							break
			surface.blit(textSurface, (currentX, 0))
			currentX += charWidth+spacing
		surface.set_colorkey((243, 243, 0))
		return surface
	
	def exit(self):
		pass
		
	def update(self, sceneManager):
		self.nextButtonOpacity -= self.nextButtonOpacityChange
		if self.nextButtonOpacity<0 or self.nextButtonOpacity>255:
			self.nextButtonOpacityChange *= -1
			self.nextButtonOpacity = min(255, max(0, self.nextButtonOpacity))
		self.handleEvents(sceneManager)
	
	def show(self):
		self.surface.blit(self.frames[self.currentFrame], (0, 0))
		for i in range(len(self.texts[self.currentFrame])):
			self.surface.blit(self.texts[self.currentFrame][i], (SIZE[0]/2-self.texts[self.currentFrame][i].get_width()/2, SIZE[1]-20*(2-i)))
		if self.currentFrame-1>=0:
			nextButtonIMG = pg.transform.flip(self.nextButtonIMG, 1, 0)
			nextButtonIMG.set_alpha(self.nextButtonOpacity)
			self.surface.blit(nextButtonIMG, (10, SIZE[1]/2-self.nextButtonIMG.get_height()/2))
		if self.currentFrame+1<len(self.frames):
			nextButtonIMG = self.nextButtonIMG.copy()
			nextButtonIMG.set_alpha(self.nextButtonOpacity)
			self.surface.blit(nextButtonIMG, (SIZE[0]-10-self.nextButtonIMG.get_width(), SIZE[1]/2-self.nextButtonIMG.get_height()/2))
		
	def handleEvents(self, sceneManager):
		for event in sceneManager.events:
			if event.type==pg.QUIT:
				self.running = False
				pg.display.quit()
				pg.quit()
				sys.exit()
			elif event.type==pg.FINGERUP:
				self.clickSound.play(0)
				x = event.x*SIZE[0]
				if x>SIZE[0]/2:
					self.currentFrame += 1
				else:
					self.currentFrame -= 1
				if self.currentFrame<0:
					self.currentFrame = 0
				if self.currentFrame >= len(self.frames):
					sceneManager.setScene(STATES.MAINMENU)
		
class STATES(Enum):
	GAME = 0
	MAINMENU = 1
	INTRO = 2
	states = [Game, MainMenu, Intro]