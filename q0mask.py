#!/usr/bin/env python

import Image
import ImageOps
import pygtk
pygtk.require("2.0")
import gtk

class Q0mask:
	def mask_q0(self, pixbuf, selection):
		q0_cell_size = 8
		w = selection[2]
		h = selection[3]
		ow = pixbuf.get_width()
		oh = pixbuf.get_height()
		im = Image.new("RGB", (w, h))
		fullimage = Image.fromstring("RGB", (ow, oh), pixbuf.get_pixels())
		temp = fullimage.crop((selection[0], selection[1], selection[0] + w, selection[1] + h))

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

		fullimage.paste(im, (selection[0], selection[1]))

		return gtk.gdk.pixbuf_new_from_data(fullimage.tostring(), gtk.gdk.COLORSPACE_RGB, False, 8, ow, oh, 3 * ow)
