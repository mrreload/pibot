export LD_LIBRARY_PATH=/usr/local/lib
sleep 60; raspivid -t 0 -h 720 -w 1080 -fps 48 -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=192.168.1.227 port=5000
