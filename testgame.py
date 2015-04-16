__author__ = 'mrreload'
import pygame
import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk

cfg = __import__('config')

GObject.threads_init()
Gst.init(None)
global v_host
global v_port


class GameWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)

        vbox = Gtk.VBox(False, 2)
        vbox.show()
        self.add(vbox)

        # create the menu
        file_menu = Gtk.Menu()

        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)

        dialog_item = Gtk.MenuItem()
        dialog_item.set_label("Dialog")
        dialog_item.show()
        dialog_item.connect("activate", self.show_dialog)
        file_menu.append(dialog_item)
        dialog_item.show()

        quit_item = Gtk.MenuItem()
        quit_item.set_label("Quit")
        quit_item.show()
        quit_item.connect("activate", self.quit)
        file_menu.append(quit_item)
        quit_item.show()

        menu_bar = Gtk.MenuBar()
        vbox.pack_start(menu_bar, False, False, 0)
        menu_bar.show()

        file_item = Gtk.MenuItem()
        file_item.set_label("_File")
        file_item.set_use_underline(True)
        file_item.show()

        file_item.set_submenu(file_menu)
        menu_bar.append(file_item)

        #create the drawing area
        da = Gtk.DrawingArea()
        da.set_size_request(800, 450)


        #gstreamer

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

        da.show()
        # You need to get the XID after window.show_all().  You shouldn't get it
        # in the on_sync_message() handler because threading issues will cause
        # segfaults there.
        #self.xid = self.widget.get_window().get_xid()
        self.pipeline.set_state(Gst.State.PLAYING)
        ## other guys code
        #da.show()
        vbox.pack_end(da, False, False, 0)
        da.connect("realize", self._realized)

        #set up the pygame objects
        #self.image = pygame.image.load("sprite.png")
        #self.background = pygame.image.load("background.png")
        self.x = 150
        self.y = 150

        #collect key press events
        self.connect("key-press-event", self.key_pressed)

    def key_pressed(self, widget, event, data=None):
        if event.keyval == 65361:
            self.x -= 5
            print("UP")
        elif event.keyval == 65362:
            self.y -= 5
        elif event.keyval == 65363:
            self.x += 5
        elif event.keyval == 65364:
            self.y += 5

    def show_dialog(self, widget, data=None):
        # prompts.info("A Pygtk Dialog", "See it works easy")
        title = "PyGame embedded in Gtk Example"
        dialog = Gtk.Dialog(title, None, Gtk.DialogFlags.MODAL,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        content_area = dialog.get_content_area()
        label = Gtk.Label("See, it still works")
        label.show()
        content_area.add(label)
        response = dialog.run()
        dialog.destroy()

    def quit(self, widget, data=None):
        self.destroy()

    def draw(self):
        #self.screen.blit(self.background, [0, 0])

        #rect = self.image.get_rect()
        #rect.x = self.x
        #rect.y = self.y
        #self.screen.blit(self.image, rect)
        pygame.display.flip()

        return True

    def _realized(self, widget, data=None):
        os.putenv('SDL_WINDOWID', str(widget.get_window().get_xid()))
        pygame.init()
        pygame.display.set_mode((300, 300), 0, 0)
        self.screen = pygame.display.get_surface()
        GObject.timeout_add(200, self.draw)

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


if __name__ == "__main__":
    v_host = cfg.host
    v_port = cfg.vid_port
    window = GameWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show()
    Gtk.main()