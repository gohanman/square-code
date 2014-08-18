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
	from PIL import Image, ImageFont, ImageDraw
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

Cairo_enabled = True
try:
	import cairo
except:
	Cairo_enabled = False
class cairo_layer (draw_layer):

	def __init__(self):
		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1024, 768)
		self.context = cairo.Context(surface)

	def get_image(self, (r,g,b), width, height):
		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
		self.context = cairo.Context(surface)
		self.context.scale(width, height)
		self.context.rectangle(0,0,width-1,height-1)
		self.context.set_source_rgb(r, g, b)
		self.context.fill()
		return surface	

	def get_font(self, name, size):
		# name is a file name
		family = 'cairo:monospace'
		if name != None:
			family = os.path.splitext(os.path.basename(name))[0]
		self.context.select_font_face(family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		self.context.set_font_size(size)
		return None

	def text_size(self, str):
		x_bearing, y_bearing, w, h = self.context.text_extents(str)[:4]
		return (w, h)

	def write_text(self, image, x, y, str):
		self.context.set_source_rgb(0,0,0)
		self.context.move_to(x, y)
		self.context.show_text(str)

	def save(self, image, filename):
		if os.path.splitext(filename)[1] == '': filename += ".png"
		image.write_to_png(filename)	
