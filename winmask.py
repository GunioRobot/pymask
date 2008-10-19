#!/usr/bin/env python

import Image
import pygtk
pygtk.require("2.0")
import gtk

class Winmask:
	def mask_win(self, pixbuf, selection):
		win_cell_size = 16
		w = selection[2]
		h = selection[3]
		if selection[2] % win_cell_size:
			w -= 8
		if selection[3] % win_cell_size:
			h -= 8
		ow = pixbuf.get_width()
		oh = pixbuf.get_height()
		im = Image.new("RGB", (w, h))
		fullimage = Image.fromstring("RGB", (ow, oh), pixbuf.get_pixels())
		temp = fullimage.crop((selection[0], selection[1], selection[0] + w, selection[1] + h))

		cell_width = w / win_cell_size

		transform = [12, 8, 6, 15, 9, 13, 2, 11, 1, 4, 14, 7, 0, 5, 10, 3]

		for x in xrange(cell_width):
			for xx in xrange(win_cell_size):
				for yy in xrange(h):
					im.putpixel(((x * win_cell_size + xx), yy), temp.getpixel(((x * win_cell_size + transform[xx]), yy)))

		fullimage.paste(im, (selection[0], selection[1]))

		return gtk.gdk.pixbuf_new_from_data(fullimage.tostring(), gtk.gdk.COLORSPACE_RGB, False, 8, ow, oh, ow * 3)
