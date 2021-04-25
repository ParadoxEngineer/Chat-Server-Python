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







def main():
    MAXLINE = 4096
    PORT = 9000
    usernames = []
    sockets = []
    reply = [] #Hold all the messages in bytes (already packed)
    listOfNames = [] #list of names message to send back to client. Helpful for direct and list.
    direct = [] #Direct message
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(32)
    sock.setblocking(False)
    sockets.append(sock)
    
    sfd = sock.fileno()



    # Main loop
    found = False 
    while True:
    
        # Get sockets with incoming data
        reads, writes, excepts = select.select(sockets, sockets, [])
        
        # Loop through incoming data
        for sock in reads:
            # If this is a server socket, accept connections
            if sock.fileno() == sfd:
                conn, addr = sock.accept()
                sockets.append(conn)
            # If it is client socket, recv whatever message 
            else:    
                #data = struct.unpack('!Bh', sock.recv(3))

                # Receive command type
                sockData = sock.recv(1)
                #When a client disconnects, the sockdata returns nothing, causeing a cascading error
                # This if statement catches that an sets the instruction type to -1 which closes the connection like 1 does
                if sockData.decode() == "":
                    data = [-1]
                else:
                    data = struct.unpack('!B', sockData)

                # Join - Attempt to add connection
                if data[0] == 0:
                    # Get length/message
                    recvData =  sock.recv(2)
                    try:
                        messageLen = struct.unpack('!h', recvData)[0]
                        messageType = '!' + str(messageLen) + 's'
                        message = struct.unpack(messageType, sock.recv(struct.calcsize(messageType)))
                        message = message[0].decode('ASCII')
                    except:
                        print("The message data was not in an expected format")
                        print("Received ", recvData)
                        print(recvData.decode())
                    # The first user will always be connected
                    if len(usernames) == 0:
                        # Join success
                        sock.send(struct.pack('!B', 0))
                        usernames.append((message, sock))
                        
                        joinMessage = '**' + str(message) + ' joined the server**\n'
                        print(joinMessage)
                        packType = '!Bh' + str(len(joinMessage)) + 's'
                        reply.append(struct.pack(packType, 2, len(joinMessage), joinMessage.encode('ASCII')))
                        break
                    else:
                        for name in usernames:
                            if name[0] == message:
                                # Join fail
                                sock.send(struct.pack('!B', 1))
                                found = True
                                break
                    if not found:
                        # Join success
                        sock.send(struct.pack('!B', 0))
                        usernames.append((message, sock))
                        
                        joinMessage = '**' + str(message) + ' is joining the chat**\n'
                        print(joinMessage)
                        packType = '!Bh' + str(len(joinMessage)) + 's'
                        reply.append(struct.pack(packType, 2, len(joinMessage), joinMessage.encode('ASCII')))
                    else: # if username is already taken return a 1
                        sock.send(struct.pack('!B', 1))
                        print("Username is taken")


                # Leave - Close client socket
                if data[0] == 1 or data[0] == -1:

                    reads.pop(reads.index(sock))
                    writes.pop(writes.index(sock))
                    sockets.pop(sockets.index(sock))
                    
                    # Delete name and socket from list
                    for s in usernames:
                        if s[1].fileno() == sock.fileno():
                            # Load leave message
                            leaveMessage = '**' + s[0] + ' is leaving the chat**\n'
                            print(leaveMessage)
                            packType = '!Bh' + str(len(leaveMessage)) + 's'
                            reply.append(struct.pack(packType, 2, len(leaveMessage), leaveMessage.encode('ASCII')))
                            
                            # Remove connection from list
                            usernames.pop(usernames.index(s))
                            # TODO: Check if connection (not sock) needs to be closed
                
                # Talk - Normal Message
                if data[0] == 2:
                    # Get length/message
                    messageLen = struct.unpack('!h', sock.recv(2))[0]
                    messageType = '!' + str(messageLen) + 's'
                    message = struct.unpack(messageType, sock.recv(struct.calcsize(messageType)))
                    message = message[0].decode('ASCII')
                    
                    if message:
                        print(message)
                        # Find out who is sending the message
                        # and append their name to the message before sending to all clients
                        for name in usernames:
                            if name[1].fileno() == sock.fileno():
                                message = '[' + name[0] + ']' + message
                                packType = '!Bh' + str(len(message)) + 's'
                                reply.append(struct.pack(packType, 2, len(message), message.encode('ASCII')))

                # List - Message to ask for list
                if data[0] == 3:
                    message = ''
                    for n in usernames:
                        message += n[0] + ','
                    message += '\n' 
                    for name in usernames:
                        if name[1].fileno() == sock.fileno():
                            packType = '!Bh' + str(len(message)) + 's'
                            listOfNames.append((sock, struct.pack(packType, 3, len(message), message.encode('ASCII'))))

                # Direct
                if data[0] == 4:
                    messageLen = struct.unpack('!h', sock.recv(2))[0]
                    messageType = '!' + str(messageLen) + 's'
                    message = struct.unpack(messageType, sock.recv(struct.calcsize(messageType)))
                    message = message[0].decode('ASCII')
                    dm = ''
                    temp = message.split()
                    for name in usernames:
                        if name[1].fileno() == sock.fileno():
                            dm = '[' + name[0] + ' Private' + ']' + ' '.join(temp[1:]) + '\n'
                    for name in usernames:
                        if name[0] == temp[0][1:]:
                            packType = '!Bh' + str(len(dm)) + 's'
                            direct.append((name[1], struct.pack(packType, 2, len(dm), dm.encode('ASCII'))))
                            #print(direct)
        
        # If there is a message in the list, send all of them one at a time
        for sock in writes:
            if sock.fileno() != sfd: 
                if reply:
                    sock.send(reply[0])
                if listOfNames:
                    for s in listOfNames:
                        if sock.fileno() == s[0].fileno():
                            sock.send(s[1])
                            listOfNames.pop(listOfNames.index(s))
                if direct:
                    # print(direct)
                    for d in direct:
                        if sock.fileno() == d[0].fileno():
                            sock.send(d[1])
                            direct.pop(direct.index(d))

        # Clear reply stack
        if reply:
            reply.pop(0)
                       
            
    # Close server socket
    sock.close()

if __name__ == "__main__":
    main()
