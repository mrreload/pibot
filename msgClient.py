import os
from socket import *
cfg = __import__('config')

addr = (cfg.host, cfg.msg_port)

def sendMsg(message):
	UDPSock = socket(AF_INET, SOCK_DGRAM)
	msgSent = False
	while not msgSent:
		UDPSock.sendto(message, addr)    	
		UDPSock.close()
		msgSent = True
