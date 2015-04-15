import subprocess
import time, shlex

pi_address = "192.168.1.227"
pi_port = "5000"

def playvid():
	cmd = "gst-launch-1.0 -v tcpclientsrc host=192.168.1.227 port=5000 ! gdpdepay ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false"
	args = shlex.split(cmd)

	try:
       		player = subprocess.Popen(args, stdin=subprocess.PIPE)
    
	except:
    		print "Unexpected error:", sys.exc_info()[0]
