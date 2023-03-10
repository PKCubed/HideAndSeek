"""
Things to add

x Serverside map loading

"""



import sys

import math
 
import pygame
from pygame.locals import *

from network import Network
from player import Player

import pygame.midi
import pygame.mixer as mixer
import time

import os

import threading
 
pygame.init()
mixer.init()

mixer.music.load("Breathing.mp3")

mixer.music.set_volume(0)

player_size = 50
player_acceleration = 0.5
player_topspeed = 6
player_friction = 0.2

comp_radius = 50

player_vision = 0.8
seeker_vision = 1.2

seeker_topspeed = 7
seeker_acceleration = 0.5

hitbox_size = player_size

my_x = 1000
my_y = 1000
my_speedx = 0
my_speedy = 0

my_x_old = my_x
my_y_old = my_y

fps = 60
fpsClock = pygame.time.Clock()
 
width, height = 800, 600
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

map_image = None
map_hbimage = None
 
seeker_pos = (0,0)

def draw_player(x, y, color):
    pygame.draw.rect(screen, color, pygame.Rect(x, y, player_size, player_size))
    if seeker:
        pygame.draw.rect(screen, (255,0,0), (x+player_size/4, y+player_size/4, player_size/2, player_size/2))

def draw_map(x, y):
    screen.blit(map_image, (-x, -y))

def draw_other_player(pl):
    if pl:
        pl_rect = pl.rect
        pygame.draw.rect(screen, pl.color, (pl_rect[0]-my_x-player_size/2, pl_rect[1]-my_y-player_size/2, player_size, player_size))
        if pl.seeker:
            pygame.draw.rect(screen, (255,0,0), (pl_rect[0]-my_x-player_size/2+player_size/4, pl_rect[1]-my_y-player_size/2+player_size/4, player_size/2, player_size/2))

def is_collision(colors):
    collision_colors = [(0,0,0,255)]

    color1 = colors[0]
    color2 = colors[1]
    color3 = colors[2]
    color4 = colors[3]
    if color1 in collision_colors or color2 in collision_colors or color3 in collision_colors or color4 in collision_colors:
        return True
    else:
        return False


difference_height = 0
difference_width = 0

# Game loop.

n = Network()
data = n.getP()

p = data

seeker = p.seeker

if not os.path.exists("map.png") or not os.path.exists("map_hitbox.png"):

    n.need_map()


    print("waiting for map image")

    # Load map images from server
    with open("map.png", "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = n.get_map()
            try:
                if bytes_read.decode() == "mapdone":    
                    # nothing is received
                    # file transmitting is done
                    break
            except:
                pass
            # write to the file the bytes we just received
            f.write(bytes_read)

    print("map1 loaded")

    # Load map images from server
    with open("map_hitbox.png", "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = n.get_map()
            try:
                if bytes_read.decode() == "mapdone":    
                    # nothing is received
                    # file transmitting is done
                    break
            except:
                pass
            # write to the file the bytes we just received
            f.write(bytes_read)

    print("map2 loaded")


try:
    map_image = pygame.image.load("map.png").convert()
    map_hbimage = pygame.image.load("map_hitbox.png").convert()
except:
    print('IMAGE ERROR: PLEASE DELETE "map.png" AND "map_hitbox.png" AND RUN "main.py" AGAIN')

my_x = p.x
my_y = p.y

if seeker:
    print("You are CHASER!")
    player_vision = seeker_vision
    player_topspeed = seeker_topspeed
else:
    print("You are HIDER!")

blocker_surface = None

def render_vision():
    global blocker_surface
    # Vision "Vingette"
    blocker_surface = pygame.Surface((screen.get_width(), screen.get_height()))
    blocker_surface = blocker_surface.convert_alpha()
    blocker_surface.fill((0, 255, 0, 255))
    center_screen = (screen.get_width()/2, screen.get_height()/2)
    for ix in range(screen.get_width()):
        for iy in range(screen.get_height()):
            pixel_distance = math.sqrt(abs(center_screen[0] - ix)**2 + abs(center_screen[1] - iy)**2) / player_vision # Do the pythagorous lol ( d = sqrt(x^2 + y^2) )
            if pixel_distance > 255:
                pixel_distance = 255
            blocker_surface.set_at((ix, iy), (0,0,0,pixel_distance))

render_vision()

def draw_vision_blocker():
    screen.blit(blocker_surface, (0,0))

player_color = p.color

music_volume = 0
music_speed = 1

pygame.midi.init()
music_player = pygame.midi.Output(0)

running = True

def music_thread():
    global running
    print("Starting Music Thread")
    music_player.set_instrument(0)
    while running:
        music_player.note_on(64, music_volume)
        time.sleep(music_speed*1.5)
        music_player.note_off(64, music_volume)
        time.sleep(0.1)
        music_player.note_on(65, music_volume)
        time.sleep(0.1)
        music_player.note_off(65, music_volume)
        time.sleep(music_speed)
    del player
    pygame.midi.quit()
    print("Music player stopped")

if not seeker:
    MusicThread = threading.Thread(target=music_thread)
    MusicThread.start()
else:
    mixer.music.play(-1) # play breething on loop

hider_distance = None

last_message = 0

old_width = screen.get_width()
old_height = screen.get_height()

while running:
    players, seeker_pos, message = n.send(p)

    if message[0] != last_message:
        last_message = message[0]
        print(message[1])

    if not seeker_pos:
        seeker_pos = (-10000, -10000)

    screen.fill((0, 0, 0))
  
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            break
        elif event.type == VIDEORESIZE: # When window is resized
            render_vision()
            #Find resize amound and fix at bottom of game loop
            difference_width = screen.get_width() - old_width
            difference_height = screen.get_height() - old_height
            old_width = screen.get_width()
            old_height = screen.get_height()
            

  


    # Update
  
    keys=pygame.key.get_pressed()
    if keys[K_a]:
        my_speedx -= player_acceleration
    if keys[K_d]:
        my_speedx += player_acceleration
    if keys[K_w]:
        my_speedy -= player_acceleration
    if keys[K_s]:
        my_speedy += player_acceleration

    if my_speedx < -player_topspeed:
        my_speedx = -player_topspeed
    if my_speedx > player_topspeed:
        my_speedx = player_topspeed
    if my_speedy < -player_topspeed:
        my_speedy = -player_topspeed
    if my_speedy > player_topspeed:
        my_speedy = player_topspeed

    if my_speedx > 0:
        if my_speedx < player_friction:
            my_speedx = 0
    if my_speedx < 0:
        if my_speedx > -player_friction:
            my_speedx = 0
    if my_speedy > 0:
        if my_speedy < player_friction:
            my_speedy = 0
    if my_speedy < 0:
        if my_speedy > -player_friction:
            my_speedy = 0

    my_x += my_speedx
    my_y += my_speedy

    if my_speedx > 0:
        my_speedx -= player_friction
    if my_speedx < 0:
        my_speedx += player_friction
    if my_speedy > 0:
        my_speedy -= player_friction
    if my_speedy < 0:
        my_speedy += player_friction

    # Check for collisions

    hitbox_point1 = (int(screen.get_width()/2-player_size/2 + my_x), int(screen.get_height()/2-player_size/2 + my_y))
    hitbox_point2 = (int(screen.get_width()/2+player_size/2 + my_x), int(screen.get_height()/2-player_size/2 + my_y))
    hitbox_point3 = (int(screen.get_width()/2-player_size/2 + my_x), int(screen.get_height()/2+player_size/2 + my_y))
    hitbox_point4 = (int(screen.get_width()/2+player_size/2 + my_x), int(screen.get_height()/2+player_size/2 + my_y))

    color1 = map_hbimage.get_at((hitbox_point1))
    color2 = map_hbimage.get_at((hitbox_point2))
    color3 = map_hbimage.get_at((hitbox_point3))
    color4 = map_hbimage.get_at((hitbox_point4))

    
    if is_collision((color1, color2, color3, color4)):

        my_speedx = 0
        my_speedy = 0

        vectorx = (my_x - my_x_old)
        vectory = (my_y - my_y_old)

        threshhold = 1 # 0 -> 1
        incriment = 1/(player_acceleration*10)


        while is_collision((color1, color2, color3, color4)):

            threshhold -= incriment

            if threshhold < 0:
                break

            my_x = my_x_old + vectorx*threshhold
            my_y = my_y_old + vectory*threshhold


            hitbox_point1 = (int(screen.get_width()/2-player_size/2 + my_x), int(screen.get_height()/2-player_size/2 + my_y))
            hitbox_point2 = (int(screen.get_width()/2+player_size/2 + my_x), int(screen.get_height()/2-player_size/2 + my_y))
            hitbox_point3 = (int(screen.get_width()/2-player_size/2 + my_x), int(screen.get_height()/2+player_size/2 + my_y))
            hitbox_point4 = (int(screen.get_width()/2+player_size/2 + my_x), int(screen.get_height()/2+player_size/2 + my_y))

            color1 = map_hbimage.get_at((hitbox_point1))
            color2 = map_hbimage.get_at((hitbox_point2))
            color3 = map_hbimage.get_at((hitbox_point3))
            color4 = map_hbimage.get_at((hitbox_point4))

        my_x = int(my_x_old + vectorx*(threshhold))
        my_y = int(my_y_old + vectory*(threshhold))

    if not seeker:
        seeker_distance = math.sqrt(abs(seeker_pos[0]-screen.get_width()/2-my_x)**2+abs(seeker_pos[1]-screen.get_height()/2-my_y)**2) # Do the pythagorous again hehe

        if seeker_distance < player_size:
            print("GAME OVER")
            pygame.quit()
            running = False
            break
        
        
        dx = seeker_pos[0]-screen.get_width()/2 - my_x
        dy = seeker_pos[1]-screen.get_height()/2 - my_y
        rads = math.atan2(-dy,dx)

        compy = -(comp_radius * math.sin(rads))
        compx = comp_radius * math.cos(rads)

        seeker_direction = (compx+screen.get_width()/2, compy+screen.get_height()/2)
        


        if seeker_distance < 1000:
            music_volume = int((1-(seeker_distance/1000))*127)
        else:
            music_volume = 0
        if seeker_distance < 600:
            music_speed = (((seeker_distance/800))*0.5)
        else:
            music_speed = 1

    my_x_old = my_x
    my_y_old = my_y

    # Fix window resize problems
    if difference_height or difference_width:
        my_x -= difference_width/2
        my_y -= difference_height/2
        difference_width = 0
        difference_height = 0

    # Draw.

    draw_map(my_x, my_y)

    if players:
        min_pl_distance = None
        for pl in players:
            draw_other_player(pl)

            if seeker:
                if pl:
                    pl_distance = math.sqrt(abs(my_x-(pl.x-screen.get_width()/2))**2+abs(my_y-(pl.y-screen.get_height()/2))**2) # Pull yet another pythagorous hehe
                    if not min_pl_distance or pl_distance < min_pl_distance:
                        min_pl_distance = pl_distance

        hider_distance = min_pl_distance
        if hider_distance:
            if hider_distance < 1000:
                mixer.music.set_volume((1-(hider_distance/1000))*1)
            else:
                mixer.music.set_volume(0)
        else:
            mixer.music.set_volume(0)


    draw_player(screen.get_width()/2-player_size/2, screen.get_height()/2-player_size/2, player_color)

    draw_vision_blocker()

    if not seeker:
        pygame.draw.circle(screen, (255, 0, 0), seeker_direction, 5)

    p.move(my_x+screen.get_width()/2, my_y+screen.get_height()/2)
    pygame.display.flip()
    fpsClock.tick(fps)

running = False
pygame.quit()
sys.exit()
