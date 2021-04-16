#############################
#
# File name: ChatServer.py
# Notes: Python 3
#
#############################

import socket
import threading
import struct
import select

#Maybe uncessecary
usernames = []

#Sends given message to all users (for Join/Leave notices and Talk)
def sendMessage(message):
    messageLen = len(message)
    packString = '!Bh' + str(messageLen) + 's'
    
    for e in usernames:
        #This syntax may be off, needs testing
        usernames[e][2].send(struct.pack(packString, 2, messageLen, message))

def main():
    MAXLINE = 4096
    PORT = 9000
    usernames = []
    sockets = []
    reply = [] #Hold all the messages in bytes (already packed)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(32)
    sock.setblocking(False)
    sockets.append(sock)
    
    sfd = sock.fileno()

    found = False 
    while True:
    
        
        reads, writes, excepts = select.select(sockets, sockets, [])
        
        for sock in reads:
            #If this is a server socket, accept connections
            if sock.fileno() == sfd:
                conn, addr = sock.accept()
                sockets.append(conn)
            #If it is client socket, recv whatever message 
            else:    
                data = struct.unpack('!Bh', sock.recv(3))
		#Debug STUB
                #print(data)  
                messageLen = data[1]
                messageType = '!' + str(messageLen) + 's'
                message = struct.unpack(messageType, sock.recv(struct.calcsize(messageType)))
                message = message[0].decode('ASCII')
                
                if data[0] == 0:
                    #The first user will always be connected
                    if len(usernames) == 0:
                        #Join success
                        print(str(message) + ' joined the server')
                        sock.send(struct.pack('!B', 0))
                        usernames.append((message, sock))
                        break
                    else:
                        for name in usernames:
                            if name[0] == message:
                                #Join fail
                                sock.send(struct.pack('!B', 1))
                                found = True
                                break
                    if not found:
                        #Join success
                        print(str(message) + ' joined the server')
                        sock.send(struct.pack('!B', 0))
                        usernames.append((message, sock))
                
                #Close client socket
                if data[0] == 1:
                    reads.pop(reads.index(sock))
                    writes.pop(writes.index(sock))
                    sockets.pop(sockets.index(sock))
                    #Delete name and socket from list
                    for s in usernames:
                        if s[1] == sock:
                            usernames.pop(usernames.index(s))
                #TODO: Send message to all clients that this client is leaving the chat
                            
                if data[0] == 2:
                    if message:
                        print(message)
                        #Find out who is sending the message
                        #and append their name to the message before sending to all clients
                        for name in usernames:
                            if name[1].fileno() == sock.fileno():
                                message = '[' + name[0] + ']' + message
                                packType = '!Bh' + str(len(message)) + 's'
                                reply.append(struct.pack(packType, 2, len(message), message.encode('ASCII'))) 
        
        #If there is a message in the list, send all of them one at a time
        for sock in writes:
            if sock.fileno() != sfd: 
                if reply:
                    sock.send(reply[0])
        if reply:
            reply.pop(0)
        
    #close server socket
    sock.close()

if __name__ == "__main__":
    main()
