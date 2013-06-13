#!/usr/bin/python

import sys, getopt
import os, os.path
import tempfile
import re, math
import platform

import Image, ImageFont, ImageDraw

class square_code:

	def __init__(self):
		self.version = 1.0
		self.ifile = ''
		self.ofile = ''
		self.tmphandle = None
		self.tmpname = ''
		self.extensions = []
		self.comments = False
		self.font = None
		self.font_size = 1
		self.width = 1600
		self.height = 1200

		self.ws_filter = re.compile('\s\s+')
		self.eol_filter = re.compile('[\r\n]+')
		self.tab_filter = re.compile('\t+')
		self.cpp_comment = re.compile('//.*')
		self.hash_comment = re.compile('#.*')
		self.c_comment = re.compile('/\*.*\*/')
		self.multi_start = re.compile('/\*.*')
		self.multi_end = re.compile('.*\*/')

	def main(self, argv):
		try:
			opts, args = getopt.getopt(argv,
					"?vi:o:ce:f:w:h:",
					["help","version","in=","out=","keep-comments","ext=","font=","width=","height="])
		except getopt.GetoptError:
			self.self_description();
			sys.exit(2)
		for opt, arg in opts:
			if opt in ("-?", "--help"):
				self_description();
				sys.exit()
			elif opt in ("-i", "--in"):
				self.ifile = arg
			elif opt in ("-o", "--out"):
				self.ofile = arg
			elif opt in ("-c", "--keep-comments"):
				self.comments = True
			elif opt in ("-e", "--ext"):
				if (arg[0] != "."): arg = "."+arg
				self.extensions.append(arg)
			elif opt in ("-v", "--version"):
				print self.version
				sys.exit()
			elif opt in ("-f", "--font"):
				self.font = arg
			elif opt in ("-w", "--width"):
				self.width = int(arg)
			elif opt in ("-h", "--height"):
				self.height = int(arg)

		if self.ifile == '' or self.ofile == '':
			self.self_description();
			print self.ifile
			print self.ofile
			sys.exit(2)

		if not(os.path.exists(self.ifile)):
			print "File/directory does not exist: "+self.ifile
			sys.exit(2)

		try:
			self.tmphandle, self.tmpname = tempfile.mkstemp()
		except:
			print "Error creating temporary file"
			sys.exit(2)
		self.tmphandle = os.fdopen(self.tmphandle,'r+')

		self.gather_code(self.ifile)

		self.tmphandle.seek(0)
		everything = self.tmphandle.read()
		self.tmphandle.close()
		print "Total output is "+str(len(everything))+" characters"

		user_font = self.font
		self.font = self.font_file(user_font)
		if self.font == None and user_font != None:
			print "Warning: font '"+user_font+"' not found"

		lines = self.split_lines(everything, self.width, self.height)
		print "Image size: "+str(self.width)+"x"+str(self.height)
		print "Font-size: "+str(self.font_size)
		self.render(lines, self.width, self.height)

		os.unlink(self.tmpname)

	def render(self, lines, width, height):
		im = Image.new('RGB',(width,height),(0xff,0xff,0xff))
		draw = ImageDraw.Draw(im)
		font = self.get_font(self.font_size)
		x = 0
		y = 0
		for line in lines:
			draw.text((x,y),line,font=font,fill=(0,0,0))
			y += font.getsize(line)[1]
		if os.path.splitext(self.ofile)[1] == '': self.ofile += ".png"
		im.save(self.ofile)

	# search system for font file
	def font_file(self, name):
		if name == None: None
		search_path = '/usr/share/fonts'
		if platform.system() == 'Windows':
			search_path = 'C:\\Windows\\Fonts'
		elif platform.system() == 'Darwin':
			search_path = '/Library/Fonts'
		for dirpath, dirs, files in os.walk(search_path):
			for file in files:
				if os.path.splitext(file)[0] == name or file == name:
					return os.path.join(dirpath,file)
		return None

	# get ImageFont object for chosen font
	def get_font(self, size):
		if self.font == None: return ImageFont.load_default()
		else: return ImageFont.truetype(self.font, size)

	def split_lines(self, text, width, height):
		size = 1
		char_per_line = 1
		sample = text[0:20]
		while True:	
			IF = self.get_font(size)
			w, char_height = IF.getsize(sample)
			char_width = w / 20.0
			char_per_line = math.floor(width/char_width)
			lines = math.ceil(len(text) / char_per_line)

			# font is too big
			if lines * char_height > height:
				# use previous size
				if size > 1:
					size -= 1
					break

				if self.font == None:
					print 'Error: cannot fit text to dimensions.'
					print 'Try specifying a truetype font. Those are resizable.'
					sys.exit(2)
				elif size == 1:
					print 'Error: cannot fit text to dimensions with selected font.'
					sys.exit(2)
			elif self.font == None:
				# PIL font isn't resizable but technically fits
				break

			# try next size
			size += 1

		self.font_size = size

		lines = []
		char_per_line = int(char_per_line)
		while text != '':
			if len(text) < char_per_line:
				lines.append(text)
				text = ''
			else:
				lines.append(text[0:char_per_line])
				text = text[char_per_line:]
		print "Writing "+str(len(lines))+" lines with "+str(char_per_line)+" characters each"
		return lines
				
	def gather_code(self, path):
		directories = []
		# if it's a file, process it
		if os.path.isfile(path) and (self.extensions == [] or os.path.splitext(path)[1] in self.extensions):
			self.codefile_to_temp(path)

		elif os.path.isdir(path):
			# process files in the current directory 
			# before going down another directory level
			for entry in os.listdir(path):
				if os.path.isdir(path+os.sep+entry):
					directories.append(path+os.sep+entry)
				elif os.path.isfile(path+os.sep+entry):
					self.gather_code(path+os.sep+entry)

		# process directories discovered earlier
		for dir in directories:
			self.gather_code(dir)
		
	def codefile_to_temp(self, path):
		fp = open(path,'r')
		str = ''
		long_comment = False
		for line in fp:	
			# in a multi-line comment. check for the end of it
			if long_comment:
				chk = self.multi_end.search(line)
				if chk == None: continue
				else: 
					line = self.multi_end.sub('',line)
					long_comment = False

			# change line endings and tabs to spaces
			line = self.eol_filter.sub(' ',line)
			line = self.tab_filter.sub(' ',line)

			# remove comments
			if not(self.comments):
				# single line comments first
				line = self.c_comment.sub('',line)
				line = self.cpp_comment.sub('',line)
				line = self.hash_comment.sub('',line)

				# check for multi-line comments
				if self.multi_start.search(line) != None:
					line = self.multi_start.sub('',line)
					long_comment = True
			
			# knit all the lines together
			str += line

		# reduce multiple spaces to a single space
		str = self.ws_filter.sub(' ',str)
		# write to file
		self.tmphandle.write(str+' ')
	
	def multi_test(self,str):
		return self.multi_start.search(str)

	def self_description(self):
		print 'square-code.py [-c -e <extension> -f <font> -w <width> -h <height>] -i <input file/dir> -o <outputfile>'
		print "-c/--keep-comments\t\tInclude comments"
		print "-e/--ext <extension>\t\tInclude files with this extension"
		print "\t\t\t\tMay be used multiple times"
		print "-f/--font <font>\t\tSpecify font"
		print "-w/--width <in pixels>\t\tSpecify image width"
		print "-h/--height <in pixels>\t\tSpecify image height"
		print "-i/--in <file/dir>\t\tInput file or directory"
		print "-o/--out <file>\t\t\tOutput file name"
		print "-h/--help\t\t\tPrint this"

if __name__ == "__main__":
	obj = square_code()
	obj.main(sys.argv[1:])
