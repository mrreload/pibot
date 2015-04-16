__author__ = 'mrreload'

import gi
import os

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk
import pygame


# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:


GObject.threads_init()
Gst.init(None)


def show_video(host, port):
    global v_host
    v_host = host
    global v_port
    v_port = port
    p = Player()
    p.run()

class Player(object):
    def __init__(self):
        self.window = Gtk.Window()
        self.window.connect('destroy', self.quit)
        self.window.set_default_size(800, 450)

        self.drawingarea = Gtk.DrawingArea()
        self.window.add(self.drawingarea)

        # Create GStreamer pipeline
        self.pipeline = Gst.Pipeline()

        # Create bus to get events from GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self.on_eos)
        self.bus.connect('message::error', self.on_error)

        # This is needed to make the video output in our DrawingArea:
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.on_sync_message)

        # # Create GStreamer elements
        # self.playbin = Gst.ElementFactory.make('playbin', None)
        #
        # # Add playbin to the pipeline
        # self.pipeline.add(self.playbin)
        #
        # # Set properties
        # self.playbin.set_property('uri', uri)

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

    def run(self):
        self.window.show_all()
        # You need to get the XID after window.show_all().  You shouldn't get it
        # in the on_sync_message() handler because threading issues will cause
        # segfaults there.
        self.xid = self.drawingarea.get_property('window').get_xid()
        self.window.connect("realize", self._realized)
        self.pipeline.set_state(Gst.State.PLAYING)

        Gtk.main()

    def _realized(self, widget, data=None):
        os.putenv('SDL_WINDOWID', str(widget.window.xid))
        pygame.init()
        pygame.display.set_mode((800, 450), 0, 0)
        self.screen = pygame.display.get_surface()
            # Fill background
        background = pygame.Surface(self.screen.get_size())
        background = background.convert()
        background.fill((250, 250, 250))
        #background = pygame.image.load("background.png")
        # Display some text
        font = pygame.font.Font(None, 36)
        text = font.render("hello", 1, (10, 10, 10))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        background.blit(text, textpos)

        # Blit everything to the screen
        self.screen.blit(background, (0, 0))
        pygame.display.flip()
        GObject.timeout_add(200, self.draw)

    def quit(self, window):
        self.pipeline.set_state(Gst.State.NULL)
        Gtk.main_quit()

    def on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            print('prepare-window-handle')
            msg.src.set_window_handle(self.xid)

    def on_eos(self, bus, msg):
        print('on_eos(): seeking to start of video')
        self.pipeline.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            0
        )

    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())



# p = Player()
# p.run()
#show_video("192.168.1.227", 5000)
#Player.displaytext("HEY THERE")