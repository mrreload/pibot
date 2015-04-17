__author__ = 'mrreload'
from Tkinter import *
from os import path
import tkFileDialog
# import pygst
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst, Gtk
# pygst.require("1.0")

filename = path.join(path.dirname(path.abspath(__file__)), '/home/mrreload/Videos/50.mkv')
uri = 'file://' + filename
#
# service routines
#
def on_message(bus, message):
    print 'got message:', message.structure.get_name()
    t = message.type
    if t == gst.MESSAGE_EOS:
        player.set_state(gst.STATE_NULL)
    elif t == gst.MESSAGE_ERROR:
        player.set_state(gst.STATE_NULL)
        err, debug = message.parse_error()
        print "Error: %s" % err, debug


def on_sync_message(bus, message):
    print 'got sync'
    if message.structure is None:
        return
    message_name = message.structure.get_name()
    print 'got sync message:', message_name
    if message_name == "prepare-xwindow-id":
        imagesink = message.src
        imagesink.set_property("force-aspect-ratio", True)
        # comment out the next line to have video pop up in it's own window
        imagesink.set_xwindow_id(field_video.winfo_id())


def get_file():
    file = tkFileDialog.askopenfilename(parent=widget_master, title='Choose a file')
    field_file.delete(0, END)
    field_file.insert(0, file)
    pipeline.set_property("uri", "file://" + file)
    pipeline.set_state(Gst.State.PLAYING)
    print 'playing...'

def on_sync_message(bus, msg):
    if msg.get_structure().get_name() == 'prepare-window-handle':
        print('prepare-window-handle')
        msg.src.set_window_handle(field_video.winfo_id())

#
# tkinter widgets
#
widget_master = Tk()

#
# file frame
#
frame_file = LabelFrame(widget_master, text=" File ")
frame_file.grid(sticky=NW)
field_file = Entry(frame_file, width=128)
field_file.grid()


def select_file(): get_file()


button_select = Button(frame_file, text='Select File', command=select_file)
button_select.grid(pady=8)

#
# video frame
#
frame_video = LabelFrame(widget_master, text=" Video ")
frame_video.grid(row=1, column=0, sticky=NW)
field_video = Canvas(frame_video, width=512, height=384, bg='black')
field_video.grid()
print 'video window id:', field_video.winfo_id()

#
# gstreamer setup
#
# player = Gst.ElementFactory.make("playbin", "player")
# bus = player.get_bus()
# bus.add_signal_watch()
# bus.enable_sync_message_emission()
# bus.connect("message", on_message)
# bus.connect("sync-message::element", on_sync_message)

# Create GStreamer pipeline
pipeline = Gst.Pipeline()

# Create bus to get events from GStreamer pipeline
bus = pipeline.get_bus()
bus.add_signal_watch()
#self.bus.connect('message::eos', self.on_eos)
#self.bus.connect('message::error', self.on_error)

# This is needed to make the video output in our DrawingArea:
bus.enable_sync_message_emission()
bus.connect('sync-message::element', on_sync_message)

# Create GStreamer elements
playbin = Gst.ElementFactory.make('playbin', None)

# Add playbin to the pipeline
pipeline.add(playbin)

# Set properties
playbin.set_property('uri', uri)  #

# let's roll
#
Gtk.gdk.threads_init()
widget_master.mainloop()