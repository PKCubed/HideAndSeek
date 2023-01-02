import pygame

class Player():
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = color
        self.rect = (x,y,self.width,self.height)
        self.vel = 3
        self.seeker = False

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)

    def move(self, x, y):
        self.x = x
        self.y = y

        self.update()

    def update(self):
        self.rect = (self.x, self.y, self.width, self.height)