__author__ = 'marc.hoaglin'
# telnet program example
import socket, select, string, sys
import traceback

def prompt() :
    sys.stdout.write('<You> ')
    sys.stdout.flush()

#main function
if __name__ == "__main__":

	# if(len(sys.argv) < 3) :
	#     print 'Usage : python telnet.py hostname port'
	#     sys.exit()
	config = {}
	execfile("client.conf", config)
	thost = config["host"]
	tport = config["message_port"]

	# host = sys.argv[1]
	# port = int(sys.argv[2])

	s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s3.settimeout(2)

	# connect to remote host
	try:
		print("Connecting to: " + thost + str(tport))
		s3.connect((thost, tport))
	except:
		print 'Unable to connect to: ' + thost + str(tport)
		print traceback.format_exc()
		sys.exit()

	print 'Connected to remote host. Start sending messages'
	prompt()

	while 1:
		socket_list = [sys.stdin, s3]

		# Get the list sockets which are readable
		read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

		for sock in read_sockets:
			#incoming message from remote server
			if sock == s3:
				data = sock.recv(4096)
				if not data:
					print '\nDisconnected from chat server'
					sys.exit()
				else :
					#print data
					sys.stdout.write(data)
					prompt()

			#user entered a message
			else:
				msg = sys.stdin.readline()
				s3.send(msg)
				prompt()
