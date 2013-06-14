#!/usr/bin/python

import os.path

class draw_layer:

	def __init__(self):
		pass

	def get_image(self, (r,g,b), width, height):
		return None

	def get_font(self, name, size):
		return None

	def text_size(self, font, str):
		return (0, 0)
		
	def write_text(self, image, x, y, str):
		pass

	def save(self, image, filename):
		pass

PIL_enabled = True
try:
	import Image, ImageFont, ImageDraw
except:
	PIL_enabled = False
class pil_layer (draw_layer):

	def get_image(self, (r,b,g), width, height):
		im = Image.new('RGB',(width,height),(r,b,g))
		self.draw = ImageDraw.Draw(im)
		return im

	def get_font(self, name, size):
		if name == None: 
			self.font = ImageFont.load_default()
		else: 
			self.font = ImageFont.truetype(name, size)
			return self.font

	def text_size(self, str):
		w,h = self.font.getsize(str)
		return (w,h)

	def write_text(self, image, x, y, str):
		self.draw.text((x,y),str,font=self.font,fill=(0,0,0))

	def save(self, image, filename):
		if os.path.splitext(filename)[1] == '': filename += ".png"
		image.save(filename)
