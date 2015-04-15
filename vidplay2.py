__author__ = 'mrreload'
import sys, gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk
from gi.repository import GdkX11, GstVideo

GObject.threads_init()
Gst.init(None)

def new_decode_pad(dbin, pad, islast):
        pad.link(convert.get_pad("sink"))

# create a pipeline and add [tcpserversrc ! decodebin ! audioconvert ! alsasink]
pipeline = Gst.Pipeline()

tcpsrc = Gst.ElementFactory.make("tcpclientsrc", "source")
pipeline.add(tcpsrc)
tcpsrc.set_property("host", "192.168.1.227")
tcpsrc.set_property("port", 5000)

gdpdepay = Gst.ElementFactory.make("gdpdepay", "gdpdepay")
pipeline.add(gdpdepay)
tcpsrc.link(gdpdepay)

rtph264depay = Gst.ElementFactory.make("rtph264depay", "rtph264depay")
pipeline.add(rtph264depay)
gdpdepay.link(rtph264depay)

h264parse = Gst.ElementFactory.make("h264parse", "h264parse")
pipeline.add(h264parse)
rtph264depay.link(h264parse)

avdec_h264 = Gst.ElementFactory.make("avdec_h264", "avdec_h264")
pipeline.add(avdec_h264)
h264parse.link(avdec_h264)

videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")
pipeline.add(videoconvert)
avdec_h264.link(videoconvert)

# convert = Gst.ElementFactory.make("audioconvert", "convert")
# pipeline.add(convert)
#
# sink = Gst.ElementFactory.make("alsasink", "sink")
# pipeline.add(sink)
# convert.link(sink)

pipeline.set_state(Gst.State.PLAYING)

# enter into a mainloop
loop = GObject.MainLoop()
loop.run()