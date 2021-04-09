# Client
import socket
import struct

def main():
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
		sock.send(struct.pack('!Bhs', 0, len(username), username))
		
		data = struct.unpack('!B', sock.recv())
		
		if data[0] = 0:
			break
		
		username = input('Username rejected, enter a new username: ')
	
	
	sock.close()

if __name__ == "__main__":
	main()