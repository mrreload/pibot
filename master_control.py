__author__ = 'mrreload'
import Tkinter as tk
ch = __import__('chat_client')
import time, Queue, threading, os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
# from gi.repository import GdkX11, GstVideo
from gi.repository import GdkX11, GstVideo

# GObject.threads_init()
Gst.init(None)
Empty = Queue.Empty


def show_video():
	p = Player()
	p.run()


class Player(object):
	def __init__(self):
		config = {}
		execfile("client.conf", config)
		global v_host
		v_host = config["host"]
		global v_port
		v_port = config["video_port"]
		self.msg_q = Queue.Queue(maxsize=0)
		self.window = tk.Tk()
		self.window.title("PiBot Control")
		self.window.geometry('1280x740')
		self.window.protocol("WM_DELETE_WINDOW", self.exithandler)
		self.videoframe = tk.Frame(self.window, width=1280, height=720)

		# Keyboard bindings
		self.setup_key_binds()
		self.telemetry = tk.Label(self.window, text="Hello, world!", font=("Arial", 12), bg='black', fg="white")

		self.telemetry.place(relwidth=1, height=20)
		self.videoframe.pack(side=tk.BOTTOM, anchor=tk.S, expand=tk.YES, fill=tk.BOTH)
		self.window_id = self.videoframe.winfo_id()

		# Setup Messaging Connection
		self.chat = ch.chat_client()
		self.chat.connecttoserver()
		self.chat.receivedata(self.msg_q, self.chat.s, self)
		self.msg_q.put("Waiting for messages!")
		self.update_tele2()

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

		if os.name == "posix":
			vaapidecode = Gst.ElementFactory.make("vaapidecode", "vaapidecode")
			self.pipeline.add(vaapidecode)
			h264parse.link(vaapidecode)

			vaapisink = Gst.ElementFactory.make("vaapisink", "vaapisink")
			self.pipeline.add(vaapisink)
			vaapisink.set_property("sync", "false")
			vaapidecode.link(vaapisink)
		else:
			avdec_h264 = Gst.ElementFactory.make("avdec_h264", "avdec_h264")
			self.pipeline.add(avdec_h264)
			h264parse.link(avdec_h264)

			videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")
			self.pipeline.add(videoconvert)
			avdec_h264.link(videoconvert)

			autovideosink = Gst.ElementFactory.make("autovideosink", "autovideosink")
			self.pipeline.add(autovideosink)
			autovideosink.set_property("sync", "false")
			videoconvert.link(autovideosink)

	# def key(self, event):
	# print "pressed", repr(event.char)

	def setup_key_binds(self):
		# self.video.bind("<Key>", self.key)
		self.videoframe.bind("<Button-1>", self.callback)
		self.videoframe.bind('<Left>', self.leftKey)
		self.videoframe.bind('<Right>', self.rightKey)
		self.videoframe.bind('<Up>', self.upKey)
		self.videoframe.bind('<Down>', self.downKey)
		self.videoframe.bind('<KeyRelease-Left>', self.move_stop)
		self.videoframe.bind('<KeyRelease-Right>', self.move_stop)
		self.videoframe.bind('<KeyRelease-Up>', self.move_stop)
		self.videoframe.bind('<KeyRelease-Down>', self.move_stop)
		self.videoframe.bind('<a>', self.leftPan)
		self.videoframe.bind('<d>', self.rightPan)
		self.videoframe.bind('<w>', self.upTilt)
		self.videoframe.bind('<x>', self.downTilt)
		self.videoframe.bind('<s>', self.centerCam)
		self.videoframe.bind('<4>', self.leftSweep)
		self.videoframe.bind('<6>', self.rightSweep)
		self.videoframe.bind('<8>', self.upSweep)
		self.videoframe.bind('<2>', self.downSweep)

	def callback(self, event):
		self.videoframe.focus_set()
		print "clicked at", event.x, event.y

	def leftKey(self, event):
		# print "Left arrow pressed"
		self.telemetry.config(text="Left")
		self.telemetry.update_idletasks()
		#mc.sendMsg("L")
		self.chat.sendcommand("L")

	def rightKey(self, event):
		#print "Right arrow pressed"
		self.telemetry.config(text="Right")
		self.telemetry.update_idletasks()
		self.chat.sendcommand("R")

	def upKey(self, event):
		#print "Up arrow pressed"
		self.telemetry.config(text="Forward")
		self.telemetry.update_idletasks()
		self.chat.sendcommand("F")

	def downKey(self, event):
		#print "Down arrow pressed"
		self.telemetry.config(text="Backward")
		self.telemetry.update_idletasks()
		self.chat.sendcommand("B")

	def leftPan(self, event):
		# print "Left Pan pressed"
		self.telemetry.config(text="Pan Left")
		self.telemetry.update_idletasks()
		# mc.sendMsg("Pan_Left")
		#chat.sendcommand("Pan_Left")
		self.chat.sendcommand("Pan_Left")

	def rightPan(self, event):
		# print "Right Pan pressed"
		self.telemetry.config(text="Pan Right")
		self.telemetry.update_idletasks()
		#chat.sendcommand("Pan_Right")
		self.chat.sendcommand("Pan_Right")

	def upTilt(self, event):
		# print "Up Tilt pressed"
		self.telemetry.config(text="Tilt Up")
		self.telemetry.update_idletasks()
		self.chat.sendcommand("Tilt_Up")

	def downTilt(self, event):
		# print "Down tilt pressed"
		self.telemetry.config(text="Tilt Down")
		self.telemetry.update_idletasks()
		self.chat.sendcommand("Tilt_Down")

	def leftSweep(self, event):
		# print "Left Pan pressed"
		self.telemetry.config(text="Pan Left")
		self.telemetry.update_idletasks()
		# mc.sendMsg("Pan_Left")
		#chat.sendcommand("Pan_Left")
		self.chat.sendcommand("Sweep_Left")

	def rightSweep(self, event):
		# print "Right Pan pressed"
		self.telemetry.config(text="Pan Right")
		self.telemetry.update_idletasks()
		#chat.sendcommand("Pan_Right")
		self.chat.sendcommand("Sweep_Right")

	def upSweep(self, event):
		# print "Up Tilt pressed"
		self.telemetry.config(text="Tilt Up")
		self.telemetry.update_idletasks()
		self.chat.sendcommand("Sweep_Up")

	def downSweep(self, event):
		# print "Down tilt pressed"
		self.telemetry.config(text="Tilt Down")
		self.telemetry.update_idletasks()
		self.chat.sendcommand("Sweep_Down")

	def centerCam(self, event):
		# print "Camera/Sensor Reset to Center"
		self.telemetry.config(text="Camera/Sensor Reset to Center")
		self.telemetry.update_idletasks()
		self.chat.sendcommand("Reset")

	def move_stop(self, event):
		self.telemetry.config(text="Stop")
		self.telemetry.update_idletasks()
		#mc.sendMsg("S")
		self.chat.sendcommand("S")

	def run(self):
		#self.send_q.put("Hello")
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
			#print('prepare-window-handle')
			image_sink = message.src
			image_sink.set_property('force-aspect-ratio', True)
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

	def update_tele(self, servertext):
		self.telemetry.config(text=servertext)
		self.telemetry.update_idletasks()

	def update_tele2(self):
		if not self.msg_q.empty():
			servertext = self.msg_q.get_nowait()
			self.telemetry.config(text=servertext)
			self.telemetry.update_idletasks()
		self.telemetry.after(100, self.update_tele2)


	def exithandler(self):
		print "Closing out"
		try:
			while 1:
				print "Q:" + self.msg_q.get_nowait()
		except Empty:
			print "Queue empty"
			pass
		print "Closing Video Stream"
		self.pipeline.set_state(Gst.State.NULL)
		print "Destroying root window"
		self.window.destroy()
		print "Quitting"
		self.window.quit()

		#show_video()