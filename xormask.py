#!/usr/bin/env python

import Image
import pygtk
pygtk.require("2.0")
import gtk

class Xormask:
	def mask_xor(self, pixbuf, selection):
		w = selection[2]
		h = selection[3]
		ow = pixbuf.get_width()
		oh = pixbuf.get_height()
		im = Image.new("RGB", (w, h))
		fullimage = Image.fromstring("RGB", (ow, oh), pixbuf.get_pixels())
		temp = fullimage.crop((selection[0], selection[1], selection[0] + w, selection[1] + h))

		for y in xrange(h):
			for x in xrange(w):
				pixel = temp.getpixel((x, y))
				pixel = ((255 - pixel[0]) ^ 0x80, (255 - pixel[1]) ^ 0x80, (255 - pixel[2]) ^ 0x80)
				im.putpixel((x, y), pixel)

		fullimage.paste(im, (selection[0], selection[1]))

		return gtk.gdk.pixbuf_new_from_data(fullimage.tostring(), gtk.gdk.COLORSPACE_RGB, False, 8, ow, oh, 3 * ow)
