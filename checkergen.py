#!/usr/bin/env python

import Image
import ImageDraw
import ImageColor

path = "checkers/"

for i in xrange(2, 9):
	im = Image.new("RGB", (i * 16, i * 16))
	draw = ImageDraw.Draw(im)

	for j in xrange(i):
		for k in xrange(i):
			colour = (255, 255, 255)

			if (j % 2 and not k % 2) or (k % 2 and not j % 2):
				draw.rectangle(((k * 16, j * 16), (((k + 1) * 16) - 1, ((j + 1) * 16) - 1)), fill=(255, 255, 255))
				colour = (0, 0, 0)

			draw.text(((k * 16) + 2, (j * 16) + 1), str((k + 1) + j * i), fill=colour)
	im.save("%s%dx%d.png" % (path, i, i))
