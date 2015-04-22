__author__ = 'mrreload'
# Tcp Chat server

import socket, select, sys, traceback

ms = __import__('messageserv')
cfg = __import__('config')


class msg_server(object):
	def __init__(self):
		# List to keep track of socket descriptors
		self.CONNECTION_LIST = []
		self.RECV_BUFFER = 4096  # Advisable to keep it as an exponent of 2
		self.PORT = cfg.msg_port

	# Function to broadcast chat messages to all connected clients
	def broadcast_data(self, message):
		# Do not send the message to master socket and the client who has send us the message
		for socket in self.CONNECTION_LIST:
			if socket != server_socket and socket != sock:
				try:
					socket.send(message)
				except:
					# broken socket connection may be, chat client pressed ctrl+c for example
					socket.close()
					self.CONNECTION_LIST.remove(socket)


	def nothuman(self):
		mserv = ms.MessageServ()

		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# this has no effect, why ?
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind(("0.0.0.0", self.PORT))
		server_socket.listen(10)

		# Add server socket to the list of readable connections
		self.CONNECTION_LIST.append(server_socket)

		print "Chat server started on port " + str(self.PORT)

		while 1:
			# Get the list sockets which are ready to be read through select
			read_sockets, write_sockets, error_sockets = select.select(self.CONNECTION_LIST, [], [])

			for sock in read_sockets:
				# New connection
				if sock == server_socket:
					# Handle the case in which there is a new connection received through server_socket
					sockfd, addr = server_socket.accept()
					self.CONNECTION_LIST.append(sockfd)
					print "Client (%s, %s) connected" % addr

					broadcast_data("[%s:%s] entered room\n" % addr)

				#Some incoming message from a client
				else:
					# Data received from client, process it
					#try:
					#In Windows, sometimes when a TCP program closes abruptly,
					# a "Connection reset by peer" exception will be thrown
					data = sock.recv(self.RECV_BUFFER)
					if data:
						#broadcast_data("\r" + '<' + str(sock.getpeername()) + '> ' + data)
						mserv.read_data(data)

					#except:
					#	print "Unexpected error:", sys.exc_info()[0]
					#	broadcast_data("Client (%s, %s) is offline" % addr)
					#	print "Client (%s, %s) is offline" % addr
					#	sock.close()
					#	CONNECTION_LIST.remove(sock)
					#	continue

		server_socket.close()

if __name__ == "__main__":
	m = msg_server()
	m.nothuman()