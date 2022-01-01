import pygame as pg
from game import SceneManager
import time
pg.init()
pg.font.init()

screen = pg.display.set_mode((1920, 1080))
screenSize = screen.get_size()
fps = 30
clock = pg.time.Clock()
sceneManager = SceneManager()
sceneManager.setUp()

font = pg.font.SysFont("Calibri", 16)
while sceneManager.running:
	sceneManager.update()
	sceneManager.show(screen)
	screen.blit(font.render(str(int(clock.get_fps())), 0, (0, 0, 0)), (20, 1000))
	pg.display.update()
	clock.tick(fps)