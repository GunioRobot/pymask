#!/usr/bin/env python

import Image
import pygtk
pygtk.require("2.0")
import gtk

class Flmask:
	def mask_fl(self, pixbuf, selection):
		fl_cell_size = 8
		w = selection[2]
		h = selection[3]
		ow = pixbuf.get_width()
		oh = pixbuf.get_height()
		im = Image.new("RGB", (w, h))
		fullimage = Image.fromstring("RGB", (ow, oh), pixbuf.get_pixels())
		temp = fullimage.crop((selection[0], selection[1], selection[0] + w, selection[1] + h))

		cell_width = w / fl_cell_size
		cell_height = h / fl_cell_size

		self.fl_init(cell_width, cell_height)

		for y in xrange(cell_height):
			for x in xrange(cell_width):
				(inv, u, v) = self.fl_transform(x, y)

				src_x = fl_cell_size * x
				src_y = fl_cell_size * y
				dst_x = fl_cell_size * u
				dst_y = fl_cell_size * v

				for yy in xrange(fl_cell_size):
					for xx in xrange(fl_cell_size):
						pixel = temp.getpixel(((src_x + xx), (src_y + yy)))

						if inv:
							pixel = (255 - pixel[0], 255 - pixel[1], 255 - pixel[2])

						im.putpixel(((dst_x + xx), (dst_y + yy)), pixel)

		fullimage.paste(im, (selection[0], selection[1]))

		return gtk.gdk.pixbuf_new_from_data(fullimage.tostring(), gtk.gdk.COLORSPACE_RGB, False, 8, ow, oh, ow * 3)

	def fl_init(self, width, height):
		self.fl_table = []
		self.fl_x = []
		self.fl_y = []

		dx = (1, 0, -1, 0)
		dy = (0, -1, 0, 1)

		for y in xrange(height):
			self.fl_table.append([])
			for x in xrange(width):
				self.fl_table[y].append({"no": -1})

		x = d = 0
		y = height - 1

		for i in xrange(width * height):
			self.fl_x.append(x)
			self.fl_y.append(y)
			self.fl_table[y][x]["no"] = i
			self.fl_table[y][x]["pair"] = width * height - i - 1

			x += dx[d]
			y += dy[d]

			if (x < 0) or (width <= x) or (y < 0) or (height <= y) or (0 <= self.fl_table[y][x]["no"]):
				x -= dx[d]
				y -= dy[d]
				d = (d + 1) % 4
				x += dx[d]
				y += dy[d]

	def fl_transform(self, x, y):
		dx = self.fl_x[self.fl_table[y][x]["pair"]]
		dy = self.fl_y[self.fl_table[y][x]["pair"]]

		return ((self.fl_table[y][x]["no"] != self.fl_table[y][x]["pair"]), dx, dy)
