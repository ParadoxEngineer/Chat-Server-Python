# Client
import socket
import struct
import sys

def main():
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

if __name__ == "__main__":
	main()
