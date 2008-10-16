#!/usr/bin/env python

# External imports
import pygtk
import gtk
import Image
import sys
import os

# Internal imports
import mekomask
import xormask

pygtk.require("2.0")

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
			("Xormask", None, "XOR 0x80", None, None, self.xormask_cb),

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
		self.area.connect("expose-event", self.area_expose)

		vbox.pack_start(self.area, padding=10)

		window.show_all()

		# Variables
		self.drawable = None
		self.image = None
		self.mekomask = None
		self.xormask = None

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

	def xormask_cb(self, action):
		if not self.xormask:
			self.xormask = xormask.Xormask()

		self.image = self.xormask.mask_xor(self.image)
		rect = self.drawable.get_size()
		rect = gtk.gdk.Rectangle(0, 0, rect[0], rect[1])
		self.drawable.invalidate_rect(rect, False)

	def mekomask_cb(self, plus):
		if not self.mekomask:
			self.mekomask = mekomask.Mekomask()

		self.image = self.mekomask.mask_meko(self.image, plus)
		rect = self.drawable.get_size()
		rect = gtk.gdk.Rectangle(0, 0, rect[0], rect[1])
		self.drawable.invalidate_rect(rect, False)

	def draw_image(self, filename):
		self.image = gtk.gdk.pixbuf_new_from_file(filename)

		self.drawable.draw_pixbuf(self.gc, self.image, 0, 0, 0, 0)

	def area_expose(self, widget, event, data=None):
		if not self.drawable:
			self.drawable = self.area.window
			self.gc = self.drawable.new_gc()

		if self.image:
			self.drawable.draw_pixbuf(self.gc, self.image, 0, 0, 0, 0)

	def delete_event(self, widget, event, data=None):
		return False

	def destroy(self, widget, data=None):
		gtk.main_quit()

	def main(self):
		gtk.main()

if __name__ == "__main__":
	App = PyMask()
	App.main()
