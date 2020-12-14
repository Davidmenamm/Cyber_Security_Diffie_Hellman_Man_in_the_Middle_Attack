import socket
import threading
import json
from collections import defaultdict

class ChatServer:
    clientsList = {}
    lastRecieveMessage = ""
    nameIdList = []
    id = ""
    idConnect0 = ""
    idConnect1 = ""
    connectionList = defaultdict(list)
    cont = 0
    sender = ""

    def __init__(self):
        self.serverSocket = None
        # self.soc = None
        self.createServer()
        # self.createServer2()
        self.rcvFiles()



    def createServer(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        localIp = '127.0.0.1'
        localPort = 9990
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((localIp, localPort))
        print('Server started at ', str(localIp), 'at port ', str(localPort))
        print('Waiting for connections ...')
        self.serverSocket.listen(10)
        self.rcvMsgInNewThread()

    def createServer2(self):
        localIp = '192.168.100.103'
        localPort = 9991
        print('Started server 2')
        print('Server started at ', str(localIp), 'at port ', str(localPort))
        print('Server2 Waiting for connections ...')
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.bind((localIp, localPort))
        self.soc.listen(10)
        self.rcvFilesInNewThread()




    def rcvMessages(self, socket):
        try:
            while True:
                msgBuffer = socket.recv(1024)
                print("allEncode:", msgBuffer)
                message = msgBuffer.decode('utf-8')
                print("allDecode:", message)

                if ":" in message:
                    self.sender = message.split(":")[0]

                if "File" in message:
                    print("funcion abierta")
                    self.rcvFiles(message)

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
                        self.connectionList[self.cont].append(self.clientsList[self.idConnect0])
                        self.connectionList[self.cont].append(self.clientsList[self.idConnect1])
                        self.cont = self.cont + 1
                    else:
                        for key in self.connectionList.keys():
                            if self.clientsList[self.idConnect0] not in self.connectionList[key]:
                                #print("if 1.1", self.clientsList[self.idConnect0], self.connectionList[key])
                                if self.clientsList[self.idConnect1] not in self.connectionList[key]:
                                    self.connectionList[self.cont].append(self.clientsList[self.idConnect0])
                                    self.connectionList[self.cont].append(self.clientsList[self.idConnect1])
                                    self.cont = self.cont + 1
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

    # def findSockOfId(self, id):
    #     try:
    #         for key in self.clientsList.keys():
    #             if key == id:
    #                 return self.clientsList[id]
    #     except ConnectionError:
    #         print("An error occurred")


    def rcvMsgInNewThread(self):
        while True:
            socket, (ip, port) = self.serverSocket.accept()
            t = threading.Thread(target=self.rcvMessages, args=(socket,))
            t.start()

    def rcvFilesInNewThread(self):
        while True:
            socket, (ip, port) = self.soc.accept()
            t = threading.Thread(target=self.rcvFiles, args=(socket,))
            t.start()

    # def rcvFiles(self, message):
    #     try:
    #         print("Enters here!!!!")
    #         name = message[4:]
    #         self.broadcastFileToAllClients(self.clientsList[name], self.searchConnection(name), "File".encode('utf-8'))
    #         sock = socket.socket()
    #         sock.bind(("localhost", 9997))
    #         sock.listen(10)  # Acepta hasta 10 conexiones entrantes.
    #         conn, address = sock.accept()
    #
    #         print (self.clientsList[name])
    #         buff = conn.recv(1024)
    #         while buff:
    #             self.broadcastFileToAllClients(self.clientsList[name], self.searchConnection(name), buff)
    #             buff = conn.recv(1024)
    #             print(buff)
    #             if not buff:
    #                 sock.close()
    #
    #     except ConnectionError:
    #         print("Connection lost")
    #         socket.close()

    def rcvFiles(self, message):
        try:
            print("Enters here!!!!")
            name = message[4:]
            self.broadcastFileToAllClients(self.clientsList[name], self.searchConnection(name), "File".encode('utf-8'))

            sock = socket.socket()
            sock.bind(("localhost", 9997))
            sock.listen(10)  # Acepta hasta 10 conexiones entrantes.
            conn, address = sock.accept()

            print (self.clientsList[name])
            buff = conn.recv(1024)
            while buff:
                self.broadcastFileToAllClients(self.clientsList[name], self.searchConnection(name), buff)
                buff = conn.recv(1024)
                print(buff)
                if not buff:
                    print("if not")
                    self.broadcastFileToAllClients(self.clientsList[name], self.searchConnection(name), b'') #EOF
                    self.broadcastFileToAllClients(self.clientsList[name], self.searchConnection(name), b'') #EOF

                    sock.close()

        except ConnectionError:
            print("Connection lost")
            socket.close()



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

    def broadcastFileToAllClients(self, sendersSocket, idRoom, msg):
        try:
            for key in self.connectionList.keys():
                if idRoom == key:
                    #print(self.connectionList[idRoom])
                    for socket in self.connectionList[idRoom]:
                        if socket is not sendersSocket:
                            socket.sendall(msg)
        except ConnectionError:
            print("An error occurred")

    def searchConnection(self, id):
        key = 0
        for clientKey in self.connectionList.keys():
            for value in self.connectionList[clientKey]:
                if self.clientsList[id] == value:
                    key = clientKey
        #print("roomKey", key)
        return key

    def sendClientList(self, socket):
        nameList = []
        for name in self.clientsList.keys():
            nameList.append(name)
        for socket in self.clientsList.values():
            socket.sendall(("name" + json.dumps(nameList)+"\n").encode('utf-8'))

    def addClientToList(self, client, key):
        if client not in self.clientsList:
            self.clientsList[key] = client


if __name__ == "__main__":
    ChatServer()
