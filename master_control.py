__author__ = 'mrreload'
import Tkinter as tk
cfg = __import__('config')
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:

#GObject.threads_init()
Gst.init(None)


def show_video():
    global v_host
    v_host = cfg.host
    global v_port
    v_port = cfg.vid_port
    p = Player()
    p.run()


class Player(object):
    def __init__(self):

        self.window = tk.Tk()
        self.window.title("PiBot Control")
        self.window.geometry('1280x720')
        self.video = tk.Frame(self.window, bg='#000000')
        self.video.pack(side=tk.BOTTOM,anchor=tk.S,expand=tk.YES,fill=tk.BOTH)
        self.window_id = self.video.winfo_id()
        print(self.window_id)

        # Create GStreamer pipeline
        self.pipeline = Gst.Pipeline()

        # Create bus to get events from GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self.on_eos)
        self.bus.connect('message::error', self.on_error)

        # This is needed to make the video output in our DrawingArea:
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.on_sync_message, self.window_id)

        # Create GStreamer elements
        tcpsrc = Gst.ElementFactory.make("tcpclientsrc", "source")
        self.pipeline.add(tcpsrc)
        tcpsrc.set_property("host", v_host)
        tcpsrc.set_property("port", v_port)

        gdpdepay = Gst.ElementFactory.make("gdpdepay", "gdpdepay")
        self.pipeline.add(gdpdepay)
        tcpsrc.link(gdpdepay)

        rtph264depay = Gst.ElementFactory.make("rtph264depay", "rtph264depay")
        self.pipeline.add(rtph264depay)
        gdpdepay.link(rtph264depay)

        h264parse = Gst.ElementFactory.make("h264parse", "h264parse")
        self.pipeline.add(h264parse)
        rtph264depay.link(h264parse)

        # avdec_h264 = Gst.ElementFactory.make("avdec_h264", "avdec_h264")
        # self.pipeline.add(avdec_h264)
        # h264parse.link(avdec_h264)

        # videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")
        # self.pipeline.add(videoconvert)
        # avdec_h264.link(videoconvert)

        vaapidecode = Gst.ElementFactory.make("vaapidecode", "vaapidecode")
        self.pipeline.add(vaapidecode)
        h264parse.link(vaapidecode)

        vaapisink = Gst.ElementFactory.make("vaapisink", "vaapisink")
        self.pipeline.add(vaapisink)
        vaapisink.set_property("sync", "false")
        vaapidecode.link(vaapisink)

        # autovideosink = Gst.ElementFactory.make("autovideosink", "autovideosink")
        # self.pipeline.add(autovideosink)
        # autovideosink.set_property("sync", "false")
        # videoconvert.link(autovideosink)

    def run(self):
        # Start the Gstreamer pipeline
        self.pipeline.set_state(Gst.State.PLAYING)
        # Open the Tk window
        self.window.mainloop()

    def quit(self, window):
        self.pipeline.set_state(Gst.State.NULL)
        self.window.destroy()

    def on_sync_message(self, bus, message, w_id):
        if message.get_structure() is None:
            return
        if message.get_structure().get_name() == 'prepare-window-handle':
            print('prepare-window-handle')
            image_sink = message.src
            image_sink.set_property('force-aspect-ratio', False)
            image_sink.set_window_handle(w_id)
        else:
            print("No Match")
            print(message.get_structure().get_name())

    def on_eos(self, bus, msg):
        print('on_eos(): seeking to start of video')
        self.pipeline.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            0
        )

    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())


show_video()