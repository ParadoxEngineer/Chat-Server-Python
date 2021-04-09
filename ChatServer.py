# Server
import socket
import threading
import struct

def clientHandler():
	

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
		data = struct.unpack('!Bhs', conn.recv(MAXLINE)
		
		if data[0] = 0:
			for e in usernames:
				if e[0] = data[2]:
					#Join fail
					conn.send(struct.pack('!B', 1))
					found = True
					break
			if not found:
				#Join success
				conn.send(struct.pack('!B', 0))
				usernames.add((data[2], addr))
				break
	
	#Send user joined message
	
	conn.close()
	
if __name__ == "__main__":
	main() 