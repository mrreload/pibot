__author__ = 'mrreload'

import socket, select, string, sys, threading, time
import Queue
mc = __import__('master_control')


class chat_client(object):
	def __init__(self):
		config = {}
		execfile("client.conf", config)
		self.m_host = config["host"]
		self.m_port = config["message_port"]
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.settimeout(2)
		self.msg_q = Queue.Queue(maxsize=0)


	def prompt(self):
		sys.stdout.write('<You> ')
		sys.stdout.flush()

	def listenmsg(self, mq, sl):

		while 1:
			socket_list = [sl]

			# Get the list sockets which are readable
			read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

			for sock in read_sockets:
				#incoming message from remote server
				if sock == sl:
					data = sock.recv(4096)
					if not data:
						print '\nDisconnected from chat server'
						sys.exit()
					else:
						#print data
						# sys.stdout.write(data)
						self.msg_q.put(data)

					# self.prompt()
				time.sleep(.1)

	def connecttoserver(self):
		try:
			self.s.connect((self.m_host, self.m_port))
		except:
			print("Unable to connect to: " + self.m_host + ":" + str(self.m_port))
			sys.exit()

		print 'Connected to remote host. Start sending messages'

	# data = self.s.recv(4096)
	# sys.stdout.write(data)

	def sendcommand(self, cmnd):
		# prompt()
		# sys.stdout.write(cmnd)
		# self.s.send(cmnd)
		self.s.sendall(cmnd)

	def receivedata(self, msgq, sockm, pthr):
		worker1 = threading.Thread(name="msgworker", target=self.listenmsg, args=(msgq, sockm,))
		worker1.setDaemon(True)
		worker1.start()
		# master = mc.Player()
		time.sleep(.5)
		while not self.msg_q.empty():
			dmsg = msgq.get()
			print("Queue data: " + dmsg)
			pthr.update_tele(dmsg)
		time.sleep(.1)





