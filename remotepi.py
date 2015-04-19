#!/usr/bin/python

import threading as th
from cfg_glob import msg_send_q
import time

master = __import__('master_control')
chat = __import__('chat_client')


def main():
	t1 = th.Thread(target=chat.run)
	t1.start()

	time.sleep(1)
	t2 = th.Thread(target=master.show_video, args=(msg_send_q,))
	t2.start()


main()




