#!/usr/bin/env python

import Image
import pygtk
pygtk.require("2.0")
import gtk

class Xormask:
	def mask_xor(self, pixbuf):
		w = pixbuf.get_width()
		h = pixbuf.get_height()
		im = Image.new("RGB", (w, h))
		temp = Image.fromstring("RGB", (w, h), pixbuf.get_pixels())

		for y in xrange(h):
			for x in xrange(w):
				#pixel = temp.getpixel(((px + q0_cell_size - xx - 1), (py + q0_cell_size - yy - 1)))
				pixel = temp.getpixel((x, y))
				pixel = ((255 - pixel[0]) ^ 0x80, (255 - pixel[1]) ^ 0x80, (255 - pixel[2]) ^ 0x80)
				#im.putpixel(((px + q0_cell_size - xx - 1), (py + q0_cell_size - yy - 1)), pixel)
				im.putpixel((x, y), pixel)

		return gtk.gdk.pixbuf_new_from_data(im.tostring(), gtk.gdk.COLORSPACE_RGB, False, 8, w, h, 3 * w)
