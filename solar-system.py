import math
import random
from typing import List
import pygame
from pygame_widgets import Slider

G = 0.01

width  = 700
height = 700

run = True

pygame.init()
screen = pygame.display.set_mode((width, height))

sliderPos = (10, 10)
sliderSize = (100, 10)

def add(a:list, b):
    if type(a) is tuple:
        if type(b) is tuple:
            return a[0]+b[0], a[1]+b[1]
        else:
            return a[0]+b, a[1]+b
    else:
        print("Incorrect types given")

def sub(a:list, b):
    if type(a) is tuple:
        if type(b) is tuple:
            return a[0]-b[0], a[1]-b[1]
        else:
            return a[0]-b, a[1]-b
    else:
        print("Incorrect types given")

def mul(a:list, b):
    if type(a) is tuple:
        if type(b) is tuple:
            return a[0]*b[0], a[1]*b[1]
        else:
            return a[0]*b, a[1]*b
    else:
        print("Incorrect types given")

def div(a:list, b):
    if type(a) is tuple:
        if type(b) is tuple:
            return a[0]/b[0], a[1]/b[1]
        else:
            return a[0]/b, a[1]/b
    else:
        print("Incorrect types given")

def distance(a:list, b:list):
    return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

def normalize(i:list):
    magnitude = math.sqrt(i[0]**2+i[1]**2)
    if magnitude > 0:
        return div(i, (magnitude, magnitude))
    else:
        return i

class Planet:
    def __init__(self, pos:list, mass, radius, color=None, vy:list=None):
        self.pos = pos
        self.mass = mass
        self.radius = radius
        self.color = "white" if color is None else color
        self.vy = (0, 0) if vy is None else vy

        self.displayMenu = False
        self.massSlider = None
    
    planets = []
    
    def update(self, otherplanets:list):
        for p in otherplanets:
            if p is not self:
                distSqr = pow(distance(self.pos, p.pos), 2)
                forceDir = normalize(sub(p.pos, self.pos))
                force = mul(forceDir, G * self.mass * p.mass / distSqr)
                accel = div(force, self.mass)

                self.vy = add(self.vy, accel)
        
        self.pos = add(self.pos, self.vy)

        if self.displayMenu:
            self.mass = max(self.massSlider.getValue(), 1)
    
    def mouseSelected(self, mousePos:list, screenPos:list):
        return (distance(self.pos, sub(mousePos, screenPos)) < self.radius)
    
    def setMassSlider(self, sliderCount):
        self.massSlider = Slider(
            screen,
            sliderPos[0],
            sliderPos[1]*sliderCount+sliderSize[1]*(sliderCount-1),
            sliderSize[0],
            sliderSize[1],
            min = 0, max = 100, colour = (255,255,255), handleColour = (100,100,100), initial = self.mass
        )
    
    @staticmethod
    def fullPresets():
        return (
            Planet((0,0), 10, 50, "yellow"),
            Planet((0,0), 0.1, 10, "gray"),
            Planet((0,0), 1, 15, "blue")
        )
    
    @staticmethod
    def getRandomPreset():
        index = random.randint(0,len(Planet.fullPresets())-1)
        return Planet.fullPresets()[index]
    
    @staticmethod
    def mouseSelectedAll(mousePos:list, screenPos:list):
        for p in Planet.planets:
            if p.mouseSelected(mousePos, screenPos):
                return p

        return None

class Input:
    def __init__(self, paused=None):
        self.screenPos = (0, 0)
        self.rightClickPos = None
        self.clickScreenPos = (0, 0)

        self.planetPos = None
        self.preset = None

        self.paused = False if paused is None else paused
    
    sliderCount = 0
    
    def mouseOnSlider(self, mousePos:list):
        max = sliderPos[1]*self.sliderCount+sliderSize[1]*self.sliderCount
        x = mousePos[0]
        y = mousePos[1]
        return x > 0 and x < sliderSize[0] and y > 0 and y < max
    
    def checkInput(self):
        global run

        events = pygame.event.get()
        mousePos = pygame.mouse.get_pos()
        buttons = pygame.mouse.get_pressed(num_buttons = 3)

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[2]:
                    self.rightClickPos = mousePos
                    self.clickScreenPos = self.screenPos
                if buttons[0]:
                    # check if mouse is selecting planet
                    selectedPlanet = Planet.mouseSelectedAll(mousePos, self.screenPos)
                    if selectedPlanet is not None:
                        planetSelected = True
                        p.displayMenu = not p.displayMenu
                        self.sliderCount += 1 if p.displayMenu else -1
                        p.setMassSlider(self.sliderCount)

                    elif not self.mouseOnSlider(mousePos):
                        self.planetPos = sub(mousePos, self.screenPos)
                        self.preset = Planet.getRandomPreset()

            if event.type == pygame.MOUSEBUTTONUP:
                self.rightClickPos = None if self.rightClickPos != None else self.rightClickPos
                if self.planetPos != None:
                    Planet.planets.append(Planet(self.planetPos, self.preset.mass, self.preset.radius,
                        self.preset.color, div(sub(self.planetPos, sub(mousePos, self.screenPos)), 1000)))
                    self.planetPos = None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

        if self.rightClickPos != None:
            self.screenPos = sub(add(self.clickScreenPos, mousePos), self.rightClickPos)

def drawCanvas(planets:List[Planet], input):
    for p in planets:
        pygame.draw.circle(screen, p.color, add(input.screenPos, p.pos), p.radius)
        if p.displayMenu:
            p.massSlider.draw()
            p.massSlider.listen(pygame.event.get())
    
    if input.planetPos != None:
        pygame.draw.circle(screen, input.preset.color, add(input.screenPos, input.planetPos), input.preset.radius)

    # draw over last frame
    background = pygame.Surface(screen.get_size())
    background.set_alpha(5)
    background.fill("black")
    screen.blit(background, (0,0))

    # update display
    pygame.display.update()


input = Input()
Planet.planets.append(Planet((350, 350), 0.1, 10, "gray", (0.04, -0.04)))
Planet.planets.append(Planet((250, 250), 50, 30, "deepskyblue"))

try:
    while run:
        input.checkInput()
        drawCanvas(Planet.planets, input)

        if not input.paused:
            for p in Planet.planets:
                p.update(Planet.planets)

except KeyboardInterrupt:
    pass