import math
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

class Input:
    def __init__(self):
        self.screenPos = (0, 0)
        self.mouseClickPos = None
        self.clickScreenPos = (0, 0)
    
    def checkInput(self):
        mousePos = pygame.mouse.get_pos()
        events = pygame.event.get()
        buttons = pygame.mouse.get_pressed(num_buttons = 3)

        for event in events:
            if buttons[2] and event.type == pygame.MOUSEBUTTONDOWN and self.mouseClickPos == None:
                self.mouseClickPos = mousePos
                self.clickScreenPos = self.screenPos

            if event.type == pygame.MOUSEBUTTONUP and self.mouseClickPos != None:
                self.mouseClickPos = None

        if self.mouseClickPos != None:
            self.screenPos = sub(add(self.clickScreenPos, mousePos), self.mouseClickPos)

def drawCanvas(planets:List[Planet], screenPos:list):
    # draw over last frame
    screen.fill("black")

    for p in planets:
        pygame.draw.circle(screen, p.color, add(screenPos, p.pos), p.radius)

    # update display
    pygame.display.update()


input = Input()
planets = [Planet((350, 350), 0.1, 10, "gray", (0.04, -0.04)),
           Planet((250, 250), 50, 30, "deepskyblue")]

try:
    while True:
        input.checkInput()
        drawCanvas(planets, input.screenPos)

        for p in planets:
            p.update(planets)

except KeyboardInterrupt:
    pass