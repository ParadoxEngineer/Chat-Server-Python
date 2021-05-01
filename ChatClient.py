############################################
#
# Authors: Jonathan Edwards, Cor Sawai,
#          Jaydon Tipton, Richard Swanson
# Course: Advanced Networks (COSC4653-01)
# Assignment: Chat Client and Server
# File name: ChatClient.py
# Usage: python3 ChatClient.py <IP>
#        Defaults to 127.0.0.1 if
#        no ip is proveded.
# Description: A chat client with GUI that
#              has simple chat commands.
# Notes: Python 3
#
############################################

import socket
import struct
import sys
import select
import threading
import tkinter as tk
import time

class App:
    def __init__(self, master, ip):
        self.master = master
        self.master.title('Chat App')
        self.IP = ip
        self.PORT = 9000
        self.isConnect = False
        
        self.outputThread = threading.Thread(target=self.updateChatScreen)
        self.outputThread.daemon = True
      
        self.mainFrame = tk.Frame(self.master)
        self.mainFrame.pack(expand=True, fill=tk.BOTH)

        self.usernameLabel = tk.Label(self.mainFrame, text='Username')
        self.usernameLabel.pack()

        self.usernameEntry = tk.Entry(self.mainFrame)
        self.usernameEntry.pack()

        self.connectBtn = tk.Button(self.mainFrame, text='Connect', command=self.joinOrLeaveServer, bg='green')
        self.connectBtn.pack()

        self.chatScreen = tk.Text(self.mainFrame, wrap='word')
        self.chatScreen.pack(expand=True, fill=tk.BOTH)
        self.chatScreen.config(state='disabled')

        self.userInput = tk.Text(self.mainFrame, height=5, wrap='word')
        self.userInput.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.sendBtn = tk.Button(self.mainFrame, text='Send', width=10, command=self.sendMessage)
        self.sendBtn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        

    def joinOrLeaveServer(self):
        #Connect for the first time, it might only connect the socket if the name is taken that is isConnect used for
        if self.isConnect == False:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.IP, self.PORT))
            self.isConnect = True

        username = self.usernameEntry.get()
        if len(username) == 0:
            self.chatScreen.config(state='normal')
            self.chatScreen.insert('end', '!!!USERNAME CANNOT BE EMPTY!!!\n')
            self.chatScreen.config(state='disabled')
            return
        
        if self.connectBtn['text'] == 'Connect':
            #Check for whitespace
            if (' ' in username):
                self.chatScreen.config(state='normal')
                self.chatScreen.insert('end', 'Username cannot contain a space\n')
                self.chatScreen.config(state='disabled')
                
                return
            #Send username to the server, 0 is the join command
            packType = '!Bh' + str(len(username)) + 's'
            self.sock.send(struct.pack(packType, 0, len(username), username.encode('ASCII')))

            #Receive respond from server whether the name is taken or not
            data = struct.unpack('!B', self.sock.recv(struct.calcsize('!B')))
            if data[0] == 0:
                self.usernameEntry.config(state='disabled')
                self.connectBtn.config(bg='red', text='Disconnect')
                self.outputThread.start()
            elif data[0] == 1:
                print("Your username was already taken")
                self.chatScreen.config(state='normal')
                self.chatScreen.insert('end', "Your username is already taken.\n")
                self.chatScreen.config(state='disabled')
            
        elif self.connectBtn['text'] == 'Disconnect':
            packType = '!Bh' + str(len(username)) + 's'
            self.sock.send(struct.pack(packType, 1, len(username), username.encode('ASCII')))
            self.usernameEntry.config(state='normal')
            self.connectBtn.config(bg='green', text='Connect')
            self.sock.close()
            self.isConnect = False


    def sendMessage(self):
        #Get message from user and send it to server
        messageToSend = ''
        prtclNo = 2
        isList = False
        messageToSend = self.userInput.get('1.0', 'end')
        #Set the type of message
        temp = messageToSend.split()
        if  messageToSend == "\n" : # if nothing was typed in the message box, do nothing
            pass
        if temp[0] == '@list':
            prtclNo = 3
            isList = True
        elif temp[0][0] == '@':
            prtclNo = 4
        
        if isList:
            packType = '!B'
            self.sock.send(struct.pack(packType, prtclNo))
            self.userInput.delete('1.0', tk.END)
        else:
            packType = '!Bh' + str(len(messageToSend)) + 's'
            self.sock.send(struct.pack(packType, prtclNo, len(messageToSend), messageToSend.encode('ASCII')))
            self.userInput.delete('1.0', tk.END)
        

    def updateChatScreen(self):
        while True:
            try:
                if self.connectBtn['text'] == 'Disconnect':
                    #Get message from server and print it out
                    data = struct.unpack('!Bh', self.sock.recv(3))
                    messageLen = data[1]
                    messageType = '!' + str(messageLen) + 's'
                    message = struct.unpack(messageType, self.sock.recv(struct.calcsize(messageType)))
                    message = message[0].decode('ASCII')
                    print(message)
                    self.chatScreen.config(state='normal')
                    self.chatScreen.insert('end', message)
                    self.chatScreen.config(state='disabled')
            except:
                pass


def main():
    ip = '127.0.0.1'
    if len(sys.argv) > 1:
        ip = sys.argv[1]

    root = tk.Tk()
    app = App(root, ip)
    root.mainloop()

if __name__ == '__main__':
    main()
