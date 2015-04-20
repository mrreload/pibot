__author__ = 'mrreload'

import socket, select, string, sys, threading, time
import Queue
from cfg_glob import msg_send_q
mc = __import__('master_control')

class chat_client(object):
	def __init__(self):
		config = {}
		execfile("client.conf", config)
		self.m_host = config["host"]
		self.m_port = config["message_port"]
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.settimeout(2)

	def prompt(self):
		sys.stdout.write('<You> ')
		sys.stdout.flush()

	def run(self):
		#time.sleep(1)
		# self.init_vars()
		# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# s.settimeout(2)
		# # connect to remote host
		# try:
		# 	self.s.connect((self.m_host, self.m_port))
		# except:
		# 	print("Unable to connect to: " + self.m_host + ":" + str(self.m_port))
		# 	sys.exit()
		#
		# print 'Connected to remote host. Start sending messages'
		# self.prompt()

		while 1:
			socket_list = [self.s]

			# Get the list sockets which are readable
			read_sockets, write_sockets, error_sockets  = select.select(socket_list, [], [])

			for sock in read_sockets:
				#incoming message from remote server
				if sock == self.s:
					data = sock.recv(4096)
					if not data:
						print '\nDisconnected from chat server'
						sys.exit()
					else:
						#print data
						mc.update_tele(data)
						sys.stdout.write(data)

					# self.prompt()
				time.sleep(.1)
				#user entered a message
				# else:
					# if not msg_send_q.empty():
					# 	mes = msg_send_q.get()
					# 	print(mes)
						#msg = q.get(True, 0.05)
					# msg = sys.stdin.readline()
					# s.send(msg)
					# self.prompt()

	def connecttoserver(self):
		try:
			self.s.connect((self.m_host, self.m_port))
		except:
			print("Unable to connect to: " + self.m_host + ":" + str(self.m_port))
			sys.exit()

		print 'Connected to remote host. Start sending messages'

		data = self.s.recv(4096)
		sys.stdout.write(data)

	def sendcommand(self, cmnd):
		# prompt()
		# sys.stdout.write(cmnd)
		# self.s.send(cmnd)
		self.s.sendall(cmnd)



