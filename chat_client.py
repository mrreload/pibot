__author__ = 'mrreload'
# telnet program example
import socket, select, string, sys, threading, time
import Queue
from cfg_glob import msg_send_q




def init_vars():
	config = {}
	execfile("client.conf", config)
	global m_host
	m_host = config["host"]
	global m_port
	m_port = config["message_port"]
	global s
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)




def prompt():
	sys.stdout.write('<You> ')
	sys.stdout.flush()


def snd(msg):
	msg_send_q.put(msg)


# main function
def run():
	init_vars()
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)
	# connect to remote host
	try:
		s.connect((m_host, m_port))
	except:
		print("Unable to connect to: " + m_host + ":" + str(m_port))
		sys.exit()

	print 'Connected to remote host. Start sending messages'
	prompt()

	while 1:
		socket_list = [sys.stdin, s]

		# Get the list sockets which are readable
		read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

		for sock in read_sockets:
			#incoming message from remote server
			if sock == s:
				data = sock.recv(4096)
				if not data:
					print '\nDisconnected from chat server'
					sys.exit()
				else:
					#print data
					sys.stdout.write(data)
				prompt()

			#user entered a message
			else:
				# if not msg_send_q.empty():
				# 	mes = msg_send_q.get()
				# 	print(mes)
					#msg = q.get(True, 0.05)
				msg = sys.stdin.readline()
				s.send(msg)
				prompt()


# def run():
# 	do_connect()

# def sendMsg(c_msg):
# 	con = Message()
# 	con.snd(con, c_msg)


def connecttoserver():
	init_vars()


	# connect to remote host
	try:
		s.connect((m_host, m_port))
	except:
		print("Unable to connect to: " + m_host + ":" + str(m_port))
		sys.exit()

	print 'Connected to remote host. Start sending messages'

	data = s.recv(4096)
	sys.stdout.write(data)


def sendcommand(cmnd):
	prompt()
	sys.stdout.write(cmnd)
	s.send(cmnd)



