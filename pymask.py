#!/usr/bin/env python

# External imports
import pygtk
pygtk.require("2.0")
import gtk
import Image
import ImageOps
import sys
import os

# Internal imports
import mekomask
import xormask
import q0mask
import flmask
import winmask

class PyMask:
	def __init__(self):
		# Gtk Stuff
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.connect("delete_event", self.delete_event)
		window.connect("destroy", self.destroy)

		vbox = gtk.VBox()
		window.add(vbox)

		uimanager = gtk.UIManager()

		actiongroup = gtk.ActionGroup("PyMask")
		actiongroup.add_actions([("File", None, "_File"),
			("Open", gtk.STOCK_OPEN, "_Open", None, None, self.open_cb),
			("Save", gtk.STOCK_SAVE, "_Save", None, None, self.save_cb),
			("Quit",  gtk.STOCK_QUIT, "_Quit", None, None, self.destroy),

			("Tools", None, "_Tools"),
			("Mekoplus", None, "Meko+", None, None, lambda a: self.mekomask_cb(True)),
			("Mekominus", None, "Meko-", None, None, lambda a: self.mekomask_cb(False)),
			("Q0mask", None, "Q0", None, None, self.q0mask_cb),
			("Flmask", None, "FL", None, None, self.flmask_cb),
			("Winmask", None, "WIN", None, None, self.winmask_cb),
			("Xormask", None, "XOR 0x80", None, None, self.xormask_cb),
			("Negmask", None, "Invert", None, None, self.neg_cb),

			("Help", None, "_Help"),
			("About", None, "_About...")])

		uimanager.insert_action_group(actiongroup, 0)
		uimanager.add_ui_from_file("%s.xml" % os.path.splitext(sys.argv[0])[0])

		accelgroup = uimanager.get_accel_group()
		window.add_accel_group(accelgroup)
		
		menubar = uimanager.get_widget("/Menubar")
		#toolbar = uimanager.get_widget("/Toolbar")

		vbox.pack_start(menubar, False)
		#vbox.pack_start(toolbar, False)

		self.area = gtk.DrawingArea()
		self.area.set_size_request(400, 300)
		self.area.connect("expose_event", self.area_expose)
		self.area.connect("motion_notify_event", self.area_motion)
		self.area.connect("button_press_event", self.area_button)
		self.area.connect("button_release_event", self.area_button)
		self.area.set_events(gtk.gdk.EXPOSURE_MASK
				   | gtk.gdk.LEAVE_NOTIFY_MASK
				   | gtk.gdk.BUTTON_PRESS_MASK
				   | gtk.gdk.BUTTON_RELEASE_MASK
				   | gtk.gdk.POINTER_MOTION_MASK
				   | gtk.gdk.POINTER_MOTION_HINT_MASK)

		vbox.pack_start(self.area, padding=10)

		window.show_all()

		# Variables
		self.drawable = None
		self.image = None
		self.mekomask = None
		self.xormask = None
		self.q0mask = None
		self.flmask = None
		self.winmask = None
		self.selection = None
		self.marchstate = 0

	def area_motion(self, widget, event):
		if event.is_hint:
			x, y, state = event.window.get_pointer()
		else:
			x = event.x
			y = event.y
			state = event.state

		if self.selection and self.selection[4] is True:
			x = int(x) / 8 * 8
			y = int(y) / 8 * 8

			self.oldselection[2] = self.selection[2]
			self.oldselection[3] = self.selection[3]

			self.selection[2] = x - self.selection[0]
			self.selection[3] = y - self.selection[1]
			self.draw_selection()
			
		return True

	def area_button(self, widget, event):
		if self.image:
			if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
				self.invalidate()
				self.selection = [int(event.x) / 8 * 8, int(event.y) / 8 * 8, 0, 0, True]
				self.oldselection = [self.selection[0], self.selection[1], 0, 0]
			elif event.type == gtk.gdk.BUTTON_RELEASE:
				self.selection[4] = False
				self.marchstate = 2
				self.draw_selection()
				if 0 in self.selection[2:3]:
					self.selection = None

		return True

	def draw_selection(self):
		if not self.selection:
			return
		self.gc.set_function(gtk.gdk.INVERT)

		if self.selection[4] is False:
			sellist = [self.selection]
			self.gc.set_line_attributes(1, gtk.gdk.LINE_ON_OFF_DASH, gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
			self.marchstate ^= 1
		else:
			sellist = [self.oldselection, self.selection]

		for selection in sellist:
			if selection[2] > 0 and selection[3] > 0:
				x = selection[0]
				y = selection[1]
				w = selection[2]
				h = selection[3]
			elif selection[2] < 0 and selection[3] > 0:
				x = selection[0] + selection[2]
				y = selection[1]
				w = abs(selection[2])
				h = selection[3]
			elif selection[2] > 0 and selection[3] < 0:
				x = selection[0]
				y = selection[1] + selection[3]
				w = selection[2]
				h = abs(selection[3])
			elif selection[2] < 0 and selection[3] < 0:
				x = selection[0] + selection[2]
				y = selection[1] + selection[3]
				w = abs(selection[2])
				h = abs(selection[3])
			else:
				continue

			if self.selection[4] is False:
				self.selection[0] = x
				self.selection[1] = y
				self.selection[2] = w
				self.selection[3] = h

			self.drawable.draw_rectangle(self.gc, False, x, y, w, h)
		self.gc.set_line_attributes(1, gtk.gdk.LINE_SOLID, gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
		self.gc.set_function(gtk.gdk.COPY)

	def open_cb(self, action):
		chooser = gtk.FileChooserDialog("Open", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		chooser.set_default_response(gtk.RESPONSE_OK)
		
		filter = gtk.FileFilter()
		filter.set_name("Images")
		filter.add_mime_type("image/png")
		filter.add_mime_type("image/jpeg")
		filter.add_mime_type("image/gif")
		filter.add_pattern("*.png")
		filter.add_pattern("*.jpg")
		filter.add_pattern("*.gif")
		chooser.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		chooser.add_filter(filter)

		response = chooser.run()

		if response == gtk.RESPONSE_OK:
			self.draw_image(chooser.get_filename())

		chooser.destroy()

	def save_cb(self, action):
		chooser = gtk.FileChooserDialog("Save", None, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		chooser.set_default_response(gtk.RESPONSE_OK)

		response = chooser.run()

		if response == gtk.RESPONSE_OK:
			self.image.save(chooser.get_filename(), "png")

		chooser.destroy()

	def invalidate(self):
		rect = self.drawable.get_size()
		rect = gtk.gdk.Rectangle(0, 0, rect[0], rect[1])
		self.drawable.invalidate_rect(rect, False)

	def winmask_cb(self, action):
		if not self.winmask:
			self.winmask = winmask.Winmask()

		if self.selection is not None and self.selection[4] is False:
			self.image = self.winmask.mask_win(self.image, self.selection)
			self.invalidate()

	def flmask_cb(self, action):
		if not self.flmask:
			self.flmask = flmask.Flmask()

		if self.selection is not None and self.selection[4] is False:
			self.image = self.flmask.mask_fl(self.image, self.selection)
			self.invalidate()

	def q0mask_cb(self, action):
		if not self.q0mask:
			self.q0mask = q0mask.Q0mask()

		if self.selection is not None and self.selection[4] is False:
			self.image = self.q0mask.mask_q0(self.image, self.selection)
			self.invalidate()

	def xormask_cb(self, action):
		if not self.xormask:
			self.xormask = xormask.Xormask()

		if self.selection is not None and self.selection[4] is False:
			self.image = self.xormask.mask_xor(self.image, self.selection)
			self.invalidate()

	def mekomask_cb(self, plus):
		if not self.mekomask:
			self.mekomask = mekomask.Mekomask()

		if self.selection is not None and self.selection[4] is False:
			self.image = self.mekomask.mask_meko(self.image, plus, self.selection)
			self.invalidate()

	def neg_cb(self, action):
		if self.selection is not None and self.selection[4] is False:
			w = self.selection[2]
			h = self.selection[3]
			ow = self.image.get_width()
			oh = self.image.get_height()
			im = Image.new("RGB", (w, h))
			fullimage = Image.fromstring("RGB", (ow, oh), self.image.get_pixels())
			temp = fullimage.crop((self.selection[0], self.selection[1], self.selection[0] + w, self.selection[1] + h))

			im = ImageOps.invert(temp)
			fullimage.paste(im, (self.selection[0], self.selection[1]))

			self.image = gtk.gdk.pixbuf_new_from_data(fullimage.tostring(), gtk.gdk.COLORSPACE_RGB, False, 8, ow, oh, ow * 3)
			self.invalidate()

	def draw_image(self, filename):
		self.image = gtk.gdk.pixbuf_new_from_file(filename)

		self.drawable.draw_pixbuf(self.gc, self.image, 0, 0, 0, 0)

	def area_expose(self, widget, event, data=None):
		if not self.drawable:
			self.drawable = self.area.window
			self.gc = self.drawable.new_gc()

		if self.image:
			self.drawable.draw_pixbuf(self.gc, self.image, 0, 0, 0, 0)
			self.draw_selection()

	def delete_event(self, widget, event, data=None):
		return False

	def destroy(self, widget, data=None):
		gtk.main_quit()

	def main(self):
		gtk.main()

if __name__ == "__main__":
	App = PyMask()
	App.main()
