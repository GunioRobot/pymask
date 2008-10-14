#!/usr/bin/env python

import pygtk
pygtk.require("2.0")
import gtk
import Image
import sys
import os

class PyMask:
	def __init__(self):
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.connect("delete_event", self.delete_event)
		window.connect("destroy", self.destroy)

		vbox = gtk.VBox()
		window.add(vbox)

		uimanager = gtk.UIManager()

		actiongroup = gtk.ActionGroup("PyMask")
		actiongroup.add_actions([("File", None, "_File"),
			("New", gtk.STOCK_NEW, "_New"),
			("Open", gtk.STOCK_OPEN, "_Open", None, None, self.open_cb),
			("Save", gtk.STOCK_SAVE, "_Save"),
			("Help", None, "_Help"),
			("About", None, "_About...")])

		uimanager.insert_action_group(actiongroup, 0)
		uimanager.add_ui_from_file("%s.xml" % os.path.splitext(sys.argv[0])[0])
		
		menubar = uimanager.get_widget("/Menubar")
		#toolbar = uimanager.get_widget("/Toolbar")

		vbox.pack_start(menubar, False)
		#vbox.pack_start(toolbar, False)

		self.area = gtk.DrawingArea()
		self.area.set_size_request(400, 300)
		self.area.connect("expose-event", self.area_expose)

		vbox.pack_start(self.area, padding=10)

		window.show_all()

	def open_cb(self, action):
		chooser = gtk.FileChooserDialog("Open", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		chooser.set_default_response(gtk.RESPONSE_OK)
		
		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		chooser.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name("Images")
		filter.add_mime_type("image/png")
		filter.add_mime_type("image/jpeg")
		filter.add_mime_type("image/gif")
		filter.add_pattern("*.png")
		filter.add_pattern("*.jpg")
		filter.add_pattern("*.gif")
		chooser.add_filter(filter)

		response = chooser.run()

		if response == gtk.RESPONSE_OK:
			self.draw_image(chooser.get_filename())

		chooser.destroy()

	def draw_image(self, filename):
		#image = Image.open(filename)
		image = gtk.gdk.pixbuf_new_from_file(filename)

		#self.drawable.draw_rgb_image(self.gc, 0, 0, image.size[0], image.size[1], gtk.gdk.RGB_DITHER_NONE, image.tostring())
		self.drawable.draw_pixbuf(self.gc, image, 0, 0, 0, 0)

	def area_expose(self, widget, event, data=None):
		if not self.drawable:
			self.drawable = self.area.window
			self.gc = self.drawable.new_gc()

	def delete_event(self, widget, event, data=None):
		return False

	def destroy(self, widget, data=None):
		gtk.main_quit()

	def main(self):
		gtk.main()

if __name__ == "__main__":
	App = PyMask()
	App.main()
