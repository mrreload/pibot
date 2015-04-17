import Tkinter as tkinter
cfg = __import__('config')
import gi

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk

videof = "/home/mrreload/Videos/50.mkv"
global v_host
global v_port

def quit(window):
    pipeline.set_state(Gst.State.NULL)
    Gtk.main_quit()


def on_eos(bus, msg):
    print('on_eos(): seeking to start of video')
    pipeline.seek_simple(
        Gst.Format.TIME,
        Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
        0
    )


def on_error(bus, msg):
    print('on_error():', msg.parse_error())


def on_sync_message(bus, message, window_id):
    if not message.structure is None:
        if message.structure.get_name() == 'prepare-xwindow-id':
            image_sink = message.src
            image_sink.set_property('force-aspect-ratio', True)
            image_sink.set_xwindow_id(window_id)

v_host = cfg.host
v_port = cfg.vid_port
GObject.threads_init()

window = tkinter.Tk()
window.geometry('800x450')

video = tkinter.Frame(window, bg='#000000')
video.pack(side=tkinter.BOTTOM, anchor=tkinter.S, expand=tkinter.YES, fill=tkinter.BOTH)

window_id = video.winfo_id()
print(window_id)
# Create GStreamer pipeline
pipeline = Gst.Pipeline()

# Create bus to get events from GStreamer pipeline
bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect('message::eos', on_eos)
bus.connect('message::error', on_error)

# This is needed to make the video output in our DrawingArea:
bus.enable_sync_message_emission()
bus.connect('sync-message::element', on_sync_message, window_id)

# # Create GStreamer elements
# playbin = Gst.ElementFactory.make('playbin', None)
#
# # Add playbin to the pipeline
# pipeline.add(playbin)
#
# # Set properties
# playbin.set_property('uri', uri)

tcpsrc = Gst.ElementFactory.make("tcpclientsrc", "source")
pipeline.add(tcpsrc)
tcpsrc.set_property("host", v_host)
tcpsrc.set_property("port", v_port)

gdpdepay = Gst.ElementFactory.make("gdpdepay", "gdpdepay")
pipeline.add(gdpdepay)
tcpsrc.link(gdpdepay)

rtph264depay = Gst.ElementFactory.make("rtph264depay", "rtph264depay")
pipeline.add(rtph264depay)
gdpdepay.link(rtph264depay)

h264parse = Gst.ElementFactory.make("h264parse", "h264parse")
pipeline.add(h264parse)
rtph264depay.link(h264parse)

# avdec_h264 = Gst.ElementFactory.make("avdec_h264", "avdec_h264")
# pipeline.add(avdec_h264)
# h264parse.link(avdec_h264)

# videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")
# pipeline.add(videoconvert)
# avdec_h264.link(videoconvert)

vaapidecode = Gst.ElementFactory.make("vaapidecode", "vaapidecode")
pipeline.add(vaapidecode)
h264parse.link(vaapidecode)

vaapisink = Gst.ElementFactory.make("vaapisink", "vaapisink")
pipeline.add(vaapisink)
vaapisink.set_property("sync", "false")
vaapidecode.link(vaapisink)

window.mainloop()