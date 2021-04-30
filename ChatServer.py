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
import ipaddress
import time


def main():
    MAXLINE = 4096
    PORT = 9000
    usernames = []
    sockets = []
    reply = [] #Hold all the messages in bytes (already packed)
    listOfNames = [] #list of names message to send back to client. Helpful for direct and list.
    direct = [] #Direct message
    closeSockets = [] #List of sockets to be closed
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(32)
    sock.setblocking(False)
    sockets.append(sock)
    
    sfd = sock.fileno()

    log("****Log Start****")

    # Main loop
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
                data = struct.unpack('!B', sock.recv(1))
                print(data)  
                
                # Join
                if data[0] == 0:
                    messageLen = struct.unpack('!h', sock.recv(2))[0]
                    messageType = '!' + str(messageLen) + 's'
                    message = struct.unpack(messageType, sock.recv(messageLen))
                    message = message[0].decode('ASCII')
                    
                    joinMessage = '**' + message + ' is joining the chat**\n'
                    packType = '!Bh' + str(len(joinMessage)) + 's'
                    if len(usernames) == 0:
                        sock.send(struct.pack('!B', 0))
                        usernames.append((message, sock))
                        print(joinMessage)
                        reply.append(struct.pack(packType, 2, len(joinMessage), joinMessage.encode('ASCII')))
                        #logfile
                        log(joinMessage + " with ip: " + str(sock.getpeername()[0]) + " and port: " + str(9000) + " username requested: " + str(message) + 
                            " Respond: Accepted" + "\n Local Time: " + time.asctime( time.localtime(time.time())))
                    else:
                        if(checkUsername(message, usernames)):
                            #Join success if name not found in usernames                                        
                            sock.send(struct.pack('!B', 0))
                            usernames.append((message, sock)) 
                            print(joinMessage)
                            reply.append(struct.pack(packType, 2, len(joinMessage), joinMessage.encode('ASCII')))  
                            #logfile
                            log(joinMessage + " with ip: " + str(sock.getpeername()[0]) + " and port: " + str(9000) + " username requested: " + str(message) + 
                            " Respond: Accepted" + "\n Local Time: " + time.asctime( time.localtime(time.time())))
                        else:
                            #Join failed                                        
                            sock.send(struct.pack('!B', 1))
                            log(joinMessage + " with ip: " + str(sock.getpeername()[0]) + " and port: " + str(9000) + " username requested: " + str(message) + 
                            " Respond: Rejected-Name In Use" + "\n Local Time: " + time.asctime(time.localtime(time.time())))
                                          
                        
                # Leave
                if data[0] == 1:
                    for s in usernames:
                        if s[1].fileno() == sock.fileno():
                            # Load leave message
                            leaveMessage = '**' + s[0] + ' is leaving the chat**\n'
                            print(leaveMessage)
                            packType = '!Bh' + str(len(leaveMessage)) + 's'
                            reply.append(struct.pack(packType, 2, len(leaveMessage), leaveMessage.encode('ASCII')))
                            #logfile
                            log(leaveMessage + " with ip: " + str(sock.getpeername()[0]) + " and port: " + str(9000) + "\n Local Time: " + time.asctime(time.localtime(time.time())))
                            # Remove name from usernames
                            usernames.pop(usernames.index(s))
                    reads.pop(reads.index(sock))
                    writes.pop(writes.index(sock))
                    sockets.pop(sockets.index(sock))
                   
                    
                # Talk - Normal Message
                if data[0] == 2:
                    messageLen = struct.unpack('!h', sock.recv(2))[0]
                    messageType = '!' + str(messageLen) + 's'
                    message = struct.unpack(messageType, sock.recv(messageLen))
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
                                log(str(message) + "  with ip: " + str(sock.getpeername()[0]) + " and port: " + str(9000)+ "\n Local Time: " + time.asctime(time.localtime(time.time())))


                # List - Message to ask for list
                if data[0] == 3:
                    #Append all names seperated by a comma
                    message = ''
                    for n in usernames:
                        message += n[0] + ','
                    message += '\n'
                    #check who is asking for the list. Append the sock and message that will later be sent ((sock, message)) 
                    for name in usernames:
                        if name[1].fileno() == sock.fileno():
                            log(name[0] + " asked for list with ip: " + str(sock.getpeername()[0]) + " and port: " + str(9000) + "\n Local Time: " + time.asctime(time.localtime(time.time())))
                            packType = '!Bh' + str(len(message)) + 's'
                            listOfNames.append((sock, struct.pack(packType, 3, len(message), message.encode('ASCII'))))


                # Direct
                if data[0] == 4:
                    messageLen = struct.unpack('!h', sock.recv(2))[0]
                    messageType = '!' + str(messageLen) + 's'
                    message = struct.unpack(messageType, sock.recv(messageLen))
                    message = message[0].decode('ASCII')
                    
                    dm = ''
                    temp = message.split()
                    
                    #Check who is the sender, and craft the packet.
                    for name in usernames:
                        if name[1].fileno() == sock.fileno():
                            dm = '[' + name[0] + ' Private' + ']' + ' '.join(temp[1:]) + '\n'
                    #Check who is the receiver and append their socket, so it can be sent later below.
                    for name in usernames:
                        if name[0] == temp[0][1:]:
                            packType = '!Bh' + str(len(dm)) + 's'
                            direct.append((name[1], struct.pack(packType, 2, len(dm), dm.encode('ASCII'))))
                            log(dm + " to " + name[0] + " with sender ip: " + str(sock.getpeername()[0]) + " and port: " + str(9000) + "\n Local Time: " + time.asctime(time.localtime(time.time())))
        
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


def log(indata):
    logFile = open("logFile.txt", "a")
    logFile.write("=>" + indata + "\n\n")
    logFile.close()

def checkUsername(target, usernames):
    for name in usernames:
        print(name[0])
        if name[0] == target:
            return False
    return True

if __name__ == "__main__":
    main()
