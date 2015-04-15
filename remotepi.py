#!/usr/bin/python

import threading, time
mc = __import__('messageclient')
vc = __import__('playa')
cfg = __import__('config')

thread_list = []


t2 = threading.Thread(target=vc.show_video(cfg.host, cfg.vid_port))
thread_list.append(t2)


t1 = threading.Thread(target=mc.control())
thread_list.append(t1)
t1.start()
t1.join()
t2.start()
t2.join()


# Starts threads
# for thread in thread_list:
#     thread.start()
#
# for thread in thread_list:
#     thread.join()

