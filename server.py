import socket
from _thread import *
from player import Player
import pickle
import pygame
import pygame.image
import os
import time

os.environ["SDL_VIDEODRIVER"] = "dummy" #Fake Video mode to make pygame happy :)
pygame.init()
screen = pygame.display.set_mode((1,1))

colors = [(255,128,0),(0,255,0),(0,255,255),(0,0,255),(255,0,255), (138,54,15), (69,139,0), (61,89,171), (153,50,204), (255,193,37)]
seeker = True

server = "192.168.0.42"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

map_image = pygame.image.tostring(pygame.image.load("map_hitbox.png").convert(), "RGB")
map_hbimage = pygame.image.tostring(pygame.image.load("map_hitbox.png").convert(), "RGB")

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

players = []

seeker_pos = (0, 0)

message=[0, ""]


def send_maps():
    with open("map.png", "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(4096)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            conn.sendall(bytes_read)
    print("Map sent to client")
    time.sleep(1)
    conn.send("mapdone".encode()) # End transmission
    time.sleep(1)
    print("2243")
    with open("map_hitbox.png", "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(4096)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            conn.sendall(bytes_read)
    print("Map sent to client")
    time.sleep(1)
    conn.send("mapdone".encode()) # End transmission


	

def threaded_client(conn, player):
    global seeker
    global seeker_pos
    if seeker:
        players[player].seeker = True
        seeker = False
        print(players[player].y)
        players[player].y -= 310
        players[player].x -= 35
        print(players[player].y)

        message[1] = "Seeker joined the game"
        message[0] += 1
    else:
        players[player].y += 100
        players[player].seeker = False

        message[1] = "Hider joined the game"
        message[0] += 1

    players[player].color = colors[0]

    colors.pop(0)
    dat = pickle.dumps(players[player])
    print(len(dat))
    conn.send(dat)

    time.sleep(1)
    
    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048))

            if data == "getmap":
                print("Sending maps to client")
                time.sleep(1)
                send_maps()
                time.sleep(1)
            else:
	            #print(data)
	            #print(players)
                players[player] = data

                if players[player].seeker:
                    seeker_pos = (players[player].x, players[player].y)
	
                if not data:
                    print("Disconnected")
                    break
                else:
                    reply = players[:player]+players[player+1:]
	
	                #print("Received: ", data)
                    #print("Sending : ", reply)
	
                conn.sendall(pickle.dumps((reply, seeker_pos, message)))
        except Exception as e:
            print(e)
            break

    print("Lost connection")
    conn.close()
    colors.append(players[player].color)
    if players[player].seeker:
        seeker = True
        seeker_pos = None

        message[1] = "Seeker left the game"
        message[0] += 1
    else:
        message[1] = "Hider left the game"
        message[0] += 1
    players[player] = 0

currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    players.append(Player(2500,2500,(255,0,0)))

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1