import math
import random
from typing import List
import pygame

G = 0.01

width  = 700
height = 700

pygame.init()
screen = pygame.display.set_mode((width, height))

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
    
    def update(self, otherplanets:list):
        for p in otherplanets:
            if p is not self:
                distSqr = pow(distance(self.pos, p.pos), 2)
                forceDir = normalize(sub(p.pos, self.pos))
                force = mul(forceDir, G * self.mass * p.mass / distSqr)
                accel = div(force, self.mass)

                self.vy = add(self.vy, accel)
        
        self.pos = add(self.pos, self.vy)
    
    @staticmethod
    def fullPresets():
        return (
            Planet((0,0), 5, 50, "yellow"),
            Planet((0,0), 0.1, 10, "gray")
        )
    
    @staticmethod
    def getPreset(index:int):
        return Planet.fullPresets()[index]

class Input:
    def __init__(self):
        self.screenPos = (0, 0)
        self.rightClickPos = None
        self.clickScreenPos = (0, 0)

        self.planetPos = None
        self.preset = None
    
    def checkInput(self):
        global planets

        mousePos = pygame.mouse.get_pos()
        events = pygame.event.get()
        buttons = pygame.mouse.get_pressed(num_buttons = 3)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[2]:
                    self.rightClickPos = mousePos
                    self.clickScreenPos = self.screenPos
                if buttons[0]:
                    self.planetPos = mousePos
                    self.preset = Planet.getPreset(random.randint(0,len(Planet.fullPresets())-1))

            if event.type == pygame.MOUSEBUTTONUP:
                self.rightClickPos = None if self.rightClickPos != None else self.rightClickPos
                if self.planetPos != None:
                    planets.append(Planet(
                        self.planetPos,
                        self.preset.mass,
                        self.preset.radius,
                        self.preset.color,
                        div(sub(self.planetPos, mousePos), 1000)
                    ))
                    self.planetPos = None

        if self.rightClickPos != None:
            self.screenPos = sub(add(self.clickScreenPos, mousePos), self.rightClickPos)

def drawCanvas(planets:List[Planet], input):
    for p in planets:
        pygame.draw.circle(screen, p.color, add(input.screenPos, p.pos), p.radius)
    
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
planets = [Planet((350, 350), 0.1, 10, "gray", (0.04, -0.04)),
           Planet((250, 250), 50, 30, "deepskyblue")]

try:
    while True:
        input.checkInput()
        drawCanvas(planets, input)

        for p in planets:
            p.update(planets)

except KeyboardInterrupt:
    pass