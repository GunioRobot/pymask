#!/usr/bin/env python

import Image
import ImageOps
import pygtk
pygtk.require("2.0")
import gtk

class Q0mask:
	def mask_q0(self, pixbuf):
		q0_cell_size = 8
		w = pixbuf.get_width()
		h = pixbuf.get_height()
		im = Image.new("RGB", (w, h))
		temp = Image.fromstring("RGB", (w, h), pixbuf.get_pixels())

		cell_width = w / q0_cell_size
		cell_height = h / q0_cell_size

		for y in xrange(cell_height):
			for x in xrange(cell_width):
				px = q0_cell_size * x
				py = q0_cell_size * y
				for yy in xrange(q0_cell_size):
					for xx in xrange(q0_cell_size):
						im.putpixel(((px + q0_cell_size - xx - 1), (py + q0_cell_size - yy - 1)), temp.getpixel(((px + xx), (py + yy))))

		im = ImageOps.invert(im)

		return gtk.gdk.pixbuf_new_from_data(im.tostring(), gtk.gdk.COLORSPACE_RGB, False, 8, w, h, 3 * w)
