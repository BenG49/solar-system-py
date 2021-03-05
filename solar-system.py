import math
import random
from typing import List, Union
import pygame
from pygame_widgets import Slider

pygame.init()

# CONSTANTS
G = 0.01
width  = 700
height = 700
sliderPos = (10, 10)
sliderSize = (100, 10)
screen = pygame.display.set_mode((width, height))


def add(a:tuple, b:Union[float, tuple]):
    if type(b) is tuple:
        return a[0]+b[0], a[1]+b[1]
    else:
        return a[0]+b, a[1]+b

def sub(a:tuple, b:Union[float, tuple]):
    if type(b) is tuple:
        return a[0]-b[0], a[1]-b[1]
    else:
        return a[0]-b, a[1]-b

def mul(a:tuple, b:Union[float, tuple]):
    if type(b) is tuple:
        return a[0]*b[0], a[1]*b[1]
    else:
        return a[0]*b, a[1]*b

def div(a:tuple, b:Union[float, tuple]):
    if type(b) is tuple:
        return a[0]/b[0], a[1]/b[1]
    else:
        return a[0]/b, a[1]/b

def distance(a:tuple, b:tuple):
    return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

def normalize(i:tuple):
    magnitude = math.sqrt(i[0]**2+i[1]**2)
    if magnitude > 0:
        return div(i, (magnitude, magnitude))
    else:
        return i

class Planet:
    def __init__(self, pos:tuple, mass:float, radius:float, color=None, vy:tuple=None):
        self.pos = pos
        self.mass = mass
        self.radius = radius
        self.color = "white" if color is None else color
        self.vy = (0, 0) if vy is None else vy

        self.displayMenu = False
        # mass, radius
        self.sliders = [None, None]
    
    # static list of all planets
    planets = []
    
    def update(self, otherplanets:tuple):
        for p in otherplanets:
            if p is not self:
                distSqr = pow(distance(self.pos, p.pos), 2)
                forceDir = normalize(sub(p.pos, self.pos))
                force = mul(forceDir, G * self.mass * p.mass / distSqr)
                accel = div(force, self.mass)

                self.vy = add(self.vy, accel)
        
        self.pos = add(self.pos, self.vy)

        if self.displayMenu:
            self.mass = max(self.sliders[0].getValue(), 1)
            self.radius = max(self.sliders[1].getValue(), 1)
    
    def setSliders(self, sliderCount:int):
        self.sliders[0] = self.makeSlider(sliderCount, 0, 100, self.mass, (100,100,100))
        sliderCount+=1
        self.sliders[1] = self.makeSlider(sliderCount, 0, 75, self.radius, (50,50,50))
    
    def makeSlider(self, sliderCount:int, min:int, max:int, initial:int, color):
        return Slider(
            screen, sliderPos[0], sliderPos[1]*(sliderCount+1)+sliderSize[1]*sliderCount, sliderSize[0], sliderSize[1],
            min = min, max = max, initial = initial, colour = self.color, handleColour = color)
    
    def mouseSelected(self, mousePos:tuple, screenPos:tuple):
        return (distance(self.pos, sub(mousePos, screenPos)) < self.radius)
    
    @staticmethod
    def getFuture(iterations:int, updateInterval:int, planet):
        output = []
        tempPlanets = [p.copy() for p in Planet.planets]
        tempPlanets.append(planet)
        for i in range(iterations):
            for p in tempPlanets:
                p.update(tempPlanets)
            if i % updateInterval == 0:
                output.append(tempPlanets[len(tempPlanets)-1].pos)
        
        return output

    @staticmethod
    def mouseSelectedAll(mousePos:tuple, screenPos:tuple):
        for p in Planet.planets:
            if p.mouseSelected(mousePos, screenPos):
                return p

        return None
    
    # random preset planet to place
    @staticmethod
    def getRandomPreset():
        presets = (Planet((0,0), 10, 50, "yellow"),
                   Planet((0,0), 0.1, 10, "gray"),
                   Planet((0,0), 1, 15, "blue"))

        return presets[random.randint(0,len(presets)-1)]
    
    def copy(self):
        return Planet((self.pos[0], self.pos[1]), self.mass, self.radius, self.color, (self.vy[0], self.vy[1]))

class Input:
    def __init__(self, paused=None):
        self.screenPos = (0, 0)
        self.rightClickPos = None
        self.clickScreenPos = (0, 0)

        self.planetPos = None
        self.preset = None

        self.paused = False if paused is None else paused
    
    # static count of sliders, used for slider position
    sliderCount = 0
    
    def mouseOnSlider(self, mousePos:list):
        padding = sliderPos[0]
        max = sliderPos[1]*self.sliderCount+sliderSize[1]*self.sliderCount
        x = mousePos[0]
        y = mousePos[1]
        return x > 0 and x < sliderSize[0]+padding and y > 0 and y < max+padding
    
    def checkInput(self):
        events = pygame.event.get()
        mousePos = pygame.mouse.get_pos()
        buttons = pygame.mouse.get_pressed(num_buttons = 3)

        test = Planet.mouseSelectedAll(mousePos, self.screenPos)

        for event in events:
            # window closing
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # move with right click
                if buttons[2]:
                    self.rightClickPos = mousePos
                    self.clickScreenPos = self.screenPos
                # create planet with left click
                if buttons[0]:
                    # check if mouse is selecting planet
                    selected = Planet.mouseSelectedAll(mousePos, self.screenPos)
                    if selected is not None:
                        selected.displayMenu = not selected.displayMenu
                        selected.setSliders(self.sliderCount)
                        self.sliderCount += len(selected.sliders) if selected.displayMenu else -len(selected.sliders)
                    # create planet
                    elif not self.mouseOnSlider(mousePos):
                        self.planetPos = sub(mousePos, self.screenPos)
                        self.preset = Planet.getRandomPreset()

            if event.type == pygame.MOUSEBUTTONUP:
                # reset right click pos
                self.rightClickPos = None if self.rightClickPos != None else self.rightClickPos

                # place planet
                if self.planetPos != None:
                    Planet.planets.append(Planet(self.planetPos, self.preset.mass, self.preset.radius,
                        self.preset.color, div(sub(self.planetPos, sub(mousePos, self.screenPos)), 1000)))
                    self.planetPos = None
            
            if event.type == pygame.KEYDOWN:
                # pause
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                # remove all sliders
                if event.key == pygame.K_ESCAPE:
                    self.sliderCount = 0
                    for p in Planet.planets:
                        p.displayMenu = False
                if event.key == pygame.K_f:
                    self.screenPos = (0, 0)

        # constantly update screen pos while clicked
        if self.rightClickPos != None:
            self.screenPos = sub(add(self.clickScreenPos, mousePos), self.rightClickPos)

def drawCanvas(planets:List[Planet], input:Input):
    for p in planets:
        pygame.draw.circle(screen, p.color, mul(add(input.screenPos, p.pos), input.zoom), p.radius)
        if p.displayMenu:
            for s in p.sliders:
                s.draw()
                s.listen(pygame.event.get())
    
    # currently placing a planet
    if input.planetPos != None:
        pygame.draw.circle(screen, input.preset.color, add(input.screenPos, input.planetPos), input.preset.radius)
        # draws path of planet, really resource intensive and doesnt work with transparency
        # for pos in Planet.getFuture(10000, 1000, Planet(input.planetPos, input.preset.mass, input.preset.radius, input.preset.color, div(sub(input.planetPos, sub(pygame.mouse.get_pos(), input.screenPos)), 1000))):\
        #     pygame.draw.circle(screen, (100,100,100), add(input.screenPos, pos), 5)

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
    while True:
        input.checkInput()
        drawCanvas(Planet.planets, input)

        if not input.paused:
            for p in Planet.planets:
                p.update(Planet.planets)

except KeyboardInterrupt:
    pass