import socket
import threading
import json
from collections import defaultdict

class ServerA:
    # static params
    clientsList = {}
    lastRecieveMessage = ""
    nameIdList = []
    id = ""
    idConnect0 = ""
    idConnect1 = ""
    connectionList = defaultdict(list)
    count = 0
    sender = ""

    # Constructor
    def __init__(self):
        self.serverSocket = None
        self.createServer()

    # Server Initialization
    def createServer(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        localIp = '127.0.0.1'
        localPort = 9990
        # socket options
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind to host and port
        self.serverSocket.bind((localIp, localPort))
        # connection msgs
        print('Server started at ', str(localIp), 'at port ', str(localPort))
        print('Waiting for connections ...')
        # listen up to n clients simultaneously
        n = 10
        self.serverSocket.listen(n)
        # Manage each client on a new thread
        self.clientThread()


    # Initiating each client thread socket
    def clientThread(self):
        while True:
            sock, (ip, port) = self.serverSocket.accept()
            t = threading.Thread(target=self.manageClient, args=(sock,))
            t.start()


    # msg broadcast to all clients
    def broadcastToAllClients(self, sendersSocket, idRoom):
        try:
            for key in self.connectionList.keys():
                if idRoom == key:
                    #print(self.connectionList[idRoom])
                    for socket in self.connectionList[idRoom]:
                        if socket is not sendersSocket:
                            socket.sendall(self.lastRecieveMessage.encode('utf-8'))
        except ConnectionError:
            print("An error occurred")

    # To manage every client socket generated
    def manageClient(self, socket):
        try:
            while True:
                msgBuffer = socket.recv(1024)
                print("allEncode:", msgBuffer)
                message = msgBuffer.decode('utf-8')
                print("allDecode:", message)

                if ":" in message:
                    self.sender = message.split(":")[0]

                if "joined" in message:
                    self.nameIdList.append(message[6:])
                    self.id = message[6:]
                    self.addClientToList(socket, self.id)
                    self.sendClientList(socket)
                if "connect" in message:
                    self.idConnect0 = message.split("to")[1]
                    self.idConnect1 = message[7:].split("to")[0]
                    self.sender = self.idConnect1
                    if not self.connectionList:
                        self.connectionList[self.count].append(self.clientsList[self.idConnect0])
                        self.connectionList[self.count].append(self.clientsList[self.idConnect1])
                        self.count = self.count + 1
                    else:
                        for key in self.connectionList.keys():
                            if self.clientsList[self.idConnect0] not in self.connectionList[key]:
                                #print("if 1.1", self.clientsList[self.idConnect0], self.connectionList[key])
                                if self.clientsList[self.idConnect1] not in self.connectionList[key]:
                                    self.connectionList[self.count].append(self.clientsList[self.idConnect0])
                                    self.connectionList[self.count].append(self.clientsList[self.idConnect1])
                                    self.count = self.count + 1
                                    #print("if 1.2", self.clientsList[self.idConnect1], self.connectionList[key] )
                                break
                            if self.clientsList[self.idConnect0] in self.connectionList[key] and \
                                    self.clientsList[self.idConnect1] in self.connectionList[key]:
                                #print("if 2")
                                break
                            if self.clientsList[self.idConnect0] in self.connectionList[key] or \
                                    self.clientsList[self.idConnect1] in self.connectionList[key]:
                                #print("if 3")
                                if self.clientsList[self.idConnect0] in self.connectionList[key]:
                                    roomNumber = self.searchConnection(self.idConnect0)
                                    self.connectionList[roomNumber].append(self.clientsList[self.idConnect1])
                                    #print("if 3.1")
                                    break
                                if self.clientsList[self.idConnect1] in self.connectionList[key]:
                                    roomNumber = self.searchConnection(self.idConnect1)
                                    self.connectionList[roomNumber].append(self.clientsList[self.idConnect0])
                                    #print("if 3.2")
                                    break
                            #self.temp = self.temp + 1
                    #print("chat rooms ", self.connectionList)

                if "disconnect" in message:
                    for client1 in self.clientsList.keys():
                        if message[10:] == client1:
                            self.clientsList.pop(client1)
                if not msgBuffer:
                    break
                self.lastRecieveMessage = msgBuffer.decode('utf-8')
                self.broadcastToAllClients(socket, self.searchConnection(self.sender))
                #print("senders ", self.searchConnection(self.idConnect1))
        except ConnectionError:
            print("Connection lost with ", socket.getpeername())
            socket.close()

    # search a connection
    def searchConnection(self, id):
        key = 0
        for clientKey in self.connectionList.keys():
            for value in self.connectionList[clientKey]:
                if self.clientsList[id] == value:
                    key = clientKey
        #print("roomKey", key)
        return key

    # to add a client to client list
    def addClientToList(self, client, key):
        if client not in self.clientsList:
            self.clientsList[key] = client

    # send client list
    def sendClientList(self, socket):
        nameList = []
        for name in self.clientsList.keys():
            nameList.append(name)
        for socket in self.clientsList.values():
            socket.sendall(("name" + json.dumps(nameList)+"\n").encode('utf-8'))

# call from main
if __name__ == "__main__":
    ServerA()
