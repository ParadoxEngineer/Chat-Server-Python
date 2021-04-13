# Client
import socket
import struct
import sys
import select

def main():
    MAXLINE = 4096
    filenos = []

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
        data = struct.unpack('!B', sock.recv(MAXLINE))
        if data[0] == 0:
            
            break
        
        username = input('Username rejected, enter a new username: ')
	
    
    while True:
        #Get user inputs
        userInput = input(username + '>')
        packType = '!Bh' + str(len(userInput)) + 's'
        sock.send(struct.pack(packType, 2, len(userInput), userInput.encode('ASCII')))
        
        #Get message from server and print it out
        data = struct.unpack('!Bh', sock.recv(3))
        messageLen = data[1]
        messageType = '!' + str(messageLen) + 's'
        message = struct.unpack(messageType, sock.recv(struct.calcsize(messageType)))
        message = message[0].decode('ASCII')
        print(message)
    
 
	
    
    sock.close()
    
if __name__ == "__main__":
    main()
