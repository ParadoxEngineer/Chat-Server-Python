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
		packType = '!Bh' + str(len(username)) + 's'
		sock.send(struct.pack(packType, 0, len(username), username.encode('ASCII')))
		
		#sock.send(struct.pack('!Bh', 0, 7))
		
		print(struct.pack(packType, 0, len(username), username.encode('ASCII')))
		
		data = struct.unpack('!B', sock.recv(MAXLINE))
		
		if data[0] == 0:
			break
		
		username = input('Username rejected, enter a new username: ')
	
	
	sock.close()

if __name__ == "__main__":
	main()
