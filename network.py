import socket
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "pkcubed.net"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except Exception as e:
            print(e)
            print("Unable to connect to server")

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            try:
                backdata, seeker_pos = pickle.loads(self.client.recv(2048))
                return backdata, seeker_pos
            except:
                print("No players connected")
                return [], (0,0)
        except socket.error as e:
            print(e)
