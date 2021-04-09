# Server
import socket
import threading
import struct

#def clientHandler():
#	

def main():
	MAXLINE = 4096
	PORT = 9000
	usernames = []
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('', PORT))
	sock.listen(32)
	
	#Move to threading
	conn, addr = sock.accept()
	
	found = False
	while True:
		data = struct.unpack('!Bh', conn.recv(3))
		print(data)
		nameLen = data[1]
		namePackType = '!' + str(nameLen) + 's'
		attemptName = struct.unpack(namePackType, conn.recv(MAXLINE))
		attemptName = attemptName[0].decode('ASCII')
		
		if data[0] == 0:
			if len(usernames) == 0:
				#Join success
				print(str(attemptName) + ' joined the server')
				conn.send(struct.pack('!B', 0))
				usernames.append((attemptName, addr))
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
	
	conn.close()
	
if __name__ == "__main__":
	main()
