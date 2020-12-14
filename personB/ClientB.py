import time
import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import json

nameId = []


class userGUI():

    def __init__(self, master1):
        self.master1 = master1
        self.master1.title("USER")
        self.master1.resizable(100, 100)
        self.frame = tk.Frame(self.master1)
        tk.Label(self.frame, text='Enter your name:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.nameText = tk.Entry(self.frame, width=50, borderwidth=2)
        self.nameText.pack(side='left', anchor='e')
        self.joinButton = tk.Button(self.frame, text="Join", width=10, command=self.onJoin).pack(side='left')
        self.frame.pack(side='top', anchor='nw')

    def onJoin(self):
        if len(self.nameText.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        nameId.append(self.nameText.get())
        self.nameText.config(state='disabled')
        self.newWindow = tk.Toplevel(self.master1)
        self.app = socketGUI(self.newWindow)

    def closeWindow(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                socketGUI.clientSocket.send(("disconnect" + nameId[0]).encode('utf-8'))
                socketGUI.clientSocket.close()
                socketGUI.soc.close()
            except OSError:
                print("None socket detected, window closed")
            self.master1.destroy()
            print("Client finished")
            exit(0)


class socketGUI():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    joinList = []
    # userList = []
    connectionList = []
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, master):

        self.master = master
        self.chatArea = None
        self.textArea = None
        self.comboBox = None
        self.connectButton = None
        self.initializeGUI()
        self.initializeSocket()
        self.listenForMsgInThread()

    def initializeSocket(self):
        print("ID:", nameId[0])
        remote_ip = '127.0.0.1' # local ip
        remote_port = 9990
        self.clientSocket.connect((remote_ip, remote_port))
        self.clientSocket.send(("joined" + nameId[0]).encode('utf-8'))

    def initializeSocket2(self):
        print("ID:", nameId[0])
        remote_ip = '127.0.0.1' # local ip
        remote_port = 9991
        self.soc.connect((remote_ip, remote_port))
        self.soc.send(("joined_server2 " + nameId[0]).encode('utf-8'))

    def initializeGUI(self):
        self.master.title("CHAT")
        self.master.resizable(0, 0)
        self.displayChatArea()
        self.displayChatEntryArea()
        self.displayComboBox()

    def listenForMsgInThread(self):
        thread = threading.Thread(target=self.rcvMsgFromServer, args=(self.clientSocket,))
        thread.start()

    def rcvMsgFromServer(self, socket):
        try:
            while True:
                buffer = socket.recv(1024)
                print(buffer)
                if not buffer:
                    break
                message = buffer.decode('utf-8')

                print("allmsg ", message)

                if "name" in message:
                    lista = message[4:]
                    message2 = lista.split("\n")[0]
                    self.joinList = json.loads(message2)
                    for name in self.joinList:
                        if name == nameId[0]:
                            self.joinList.remove(name)
                    self.comboBox['values'] = self.joinList

                if "connect" in message:
                    user = message[7:].split("to")[0]
                    self.connectionList.append(user)
                    messageConn = user + " has connected"
                    self.textArea.config(state='normal')
                    self.textArea.delete(1.0, 'end')
                    self.chatArea.insert('end', messageConn + '\n')
                    # if messageConn != "":
                    #     self.chatArea.insert('end', "If not connected to -" + user +
                    #                          "- please connect to start chat " + '\n')
                    self.chatArea.yview(tk.END)

                elif "name" not in message and "connect" not in message:
                    self.chatArea.insert('end', message + '\n')
                    self.chatArea.yview(tk.END)

        except ConnectionAbortedError:
            socket.close()
        except:
            print("socket timeout 2")

    def displayChatArea(self):
        self.frame = tk.Frame(self.master)
        tk.Label(self.frame, text='Chat Box:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chatArea = tk.Text(self.frame, width=60, height=10, font=("Serif", 12))
        scrollbar = tk.Scrollbar(self.frame, command=self.chatArea.yview, orient=tk.VERTICAL)
        self.chatArea.config(yscrollcommand=scrollbar.set)
        self.chatArea.bind('<KeyPress>', lambda e: 'break')
        self.chatArea.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
        self.frame.pack(side='top')

    def displayChatEntryArea(self):
        self.frame = tk.Frame(self.master)
        tk.Label(self.frame, text='Enter message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.textArea = tk.Text(self.frame, width=60, height=3, font=("Serif", 12))
        self.textArea.pack(side='left', pady=15)
        self.textArea.bind('<Return>', self.onEnterKeyPressed)
        self.textArea.insert('end', "Disable until connection" + '\n')
        self.textArea.config(state='disabled')
        self.frame.pack(side='top')

    def displayComboBox(self):
        self.frame = tk.Frame(self.master)
        tk.Label(self.frame, text='Clients list:', font=("Serif", 12)).pack(side='left', padx=10)
        n = tk.StringVar()
        self.comboBox = ttk.Combobox(self.frame, width=50, textvariable=n, state="readonly")
        self.comboBox['values'] = self.joinList
        self.comboBox.pack(side='left', anchor='e')
        self.connectButton = tk.Button(self.frame, text="Connect", width=10, command=self.onConnect)
        self.connectButton.pack(side='left')
        self.frame.pack(side='top', anchor='nw')

    def onConnect(self):
        self.textArea.config(state='normal')
        self.textArea.delete(1.0, 'end')
        selected = self.comboBox.get()
        # print("selected ", self.selected[0])
        self.clientSocket.send(("connect" + nameId[0] + "to" + selected).encode('utf-8'))
        print("selected ", selected)

    def onEnterKeyPressed(self, event):
        self.sendChat()
        self.clearText()

    def clearText(self):
        self.textArea.delete(1.0, 'end')

    def sendChat(self):
        sendersName = nameId[0].strip() + ": "
        data = self.textArea.get(1.0, 'end').strip()
        message = (sendersName + data).encode('utf-8')
        self.chatArea.insert('end', message.decode('utf-8') + '\n')
        self.chatArea.yview(tk.END)
        self.clientSocket.send(message)
        self.textArea.delete(1.0, 'end')
        return 'break'


def main():
    root = tk.Tk()
    app = userGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.closeWindow)
    root.mainloop()


if __name__ == '__main__':
    main()
