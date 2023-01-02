import socket
from _thread import *
from player import Player
import pickle

colors = [(255,128,0),(0,255,0),(0,255,255),(0,0,255),(255,0,255), (138,54,15), (69,139,0), (61,89,171), (153,50,204), (255,193,37)]
seeker = True

server = "192.168.0.53"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

players = []

seeker_pos = (0, 0)

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
    else:
        players[player].y += 100
        players[player].seeker = False

    players[player].color = colors[0]

    colors.pop(0)
    conn.send(pickle.dumps(players[player]))
    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
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

            conn.sendall(pickle.dumps((reply, seeker_pos)))
        except Exception as e:
            print(e)
            break

    print("Lost connection")
    conn.close()
    colors.append(players[player].color)
    if players[player].seeker:
        seeker = True
        seeker_pos = None
    players[player] = 0

currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    players.append(Player(2500,2500,(255,0,0)))

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1