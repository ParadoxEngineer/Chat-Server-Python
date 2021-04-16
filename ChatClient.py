# Client
import socket
import struct
import sys
import select
import threading
import tkinter as tk
        

def inputHandler(sock, username):
    while True:
        userInput = input(username + '>')
        packType = '!Bh' + str(len(userInput)) + 's'
        sock.send(struct.pack(packType, 2, len(userInput), userInput.encode('ASCII')))

def outputHandler(sock):
    while True:
        #Get message from server and print it out
        data = struct.unpack('!Bh', sock.recv(3))
        messageLen = data[1]
        messageType = '!' + str(messageLen) + 's'
        message = struct.unpack(messageType, sock.recv(struct.calcsize(messageType)))
        message = message[0].decode('ASCII')
        print(message)
        

def main():
<<<<<<< HEAD

    if len(sys.argv) < 2:
        IP = input('Enter server IP: ')
    else:
        IP = sys.argv[1]
    PORT = 9000

    username = input('Enter your username: ')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP, PORT)) 

    
    while True:
        #Send username to the server, 0 is the join command
        packType = '!Bh' + str(len(username)) + 's'
        sock.send(struct.pack(packType, 0, len(username), username.encode('ASCII')))
        
        #Receive respond from server whether the name is taken or not
        data = struct.unpack('!B', sock.recv(struct.calcsize('!B')))
        if data[0] == 0:
            
            break
        
        username = input('Username rejected, enter a new username: ')

    #Get user inputs
    inputThread = threading.Thread(target=inputHandler, args=(sock, username))
    inputThread.daemon = True
    inputThread.start()

    #Get ouputs 
    OutputThread = threading.Thread(target=outputHandler, args=(sock,))
    OutputThread.daemon = True
    OutputThread.start()

    inputThread.join()
    OutputThread.join()    

    root.mainloop()
    sock.close()
=======
	MAXLINE = 4096
	
	if len(sys.argv) < 2:
		IP = input('Enter server IP: ')
	else:
		IP = sys.argv[1]
	PORT = 9000
	
	username = input('Enter your username: ')
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((IP, PORT))
	
	# Join command
	while True:
		if len(username) > 0:
			packType = '!Bh' + str(len(username)) + 's'
			sock.send(struct.pack(packType, 0, len(username), username.encode('ASCII')))
			
			#Debug STUB
			#print(struct.pack(packType, 0, len(username), username.encode('ASCII')))
			
			data = struct.unpack('!B', sock.recv(MAXLINE))
			if data[0] == 0:
				break
			
			username = input('Username rejected, enter a new username: ')
		else:
			username = input('Username cannot be blank, enter a username: ')
	
	sock.close()
>>>>>>> 6bc021a2f3139a0acd1a46b91fb46cf2c12bce77

if __name__ == "__main__":
    main()
