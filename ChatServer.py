# Server
import socket
import threading
import struct

usernames = []

#Leftover for threading
#def clientHandler():

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
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('', PORT))
	sock.listen(32)
	
	conn, addr = sock.accept()
	
	####
	#This should all be in thread func
	####
	
	#Receive Join command
	found = False
	while True:
		data = struct.unpack('!Bh', conn.recv(3))
		
		#Debug STUB
		#print(data)
		nameLen = data[1]
		namePackType = '!' + str(nameLen) + 's'
		attemptName = struct.unpack(namePackType, conn.recv(MAXLINE))
		attemptName = attemptName[0].decode('ASCII')
		
		if data[0] == 0:
			if len(usernames) == 0:
				#Join success
				print(str(attemptName) + ' joined the server')
				conn.send(struct.pack('!B', 0))
				usernames.append((attemptName, addr, conn))
				break
			else:
				for e in usernames:
					if e[0] == attemptName:
						#Join fail
						conn.send(struct.pack('!B', 1))
						found = True
						break
			if not found:
				#Join success
				print(str(attemptName) + ' joined the server')
				conn.send(struct.pack('!B', 0))
				usernames.append((attemptName, addr))
				break
	
	#Send user joined message
	
	#Main loop
	
	####
	#End of thread section
	####
	
	conn.close()
	
if __name__ == "__main__":
	main()
