#!/usr/bin/python

import sys, getopt
import os, os.path
import tempfile
import re

class square_code:

	def __init__(self):
		self.version = 1.0
		self.ifile = ''
		self.ofile = ''
		self.tmphandle = None
		self.tmpname = ''
		self.extensions = []
		self.comments = False

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
			opts, args = getopt.getopt(argv,"hvi:o:ce:",["help","version","in=","out=","keep-comments","ext="])
		except getopt.GetoptError:
			self.self_description();
			sys.exit(2)
		for opt, arg in opts:
			if opt in ("-h", "--help"):
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
		print everything

		os.unlink(self.tmpname)

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

	def self_description(self):
		print 'square-code.py [-c -e <extension>] -i <input file/dir> -o <outputfile>'
		print "-c/--keep-comments\t\tInclude comments"
		print "-e/--ext <extension>\t\tInclude files with this extension"
		print "\t\t\t\tMay be used multiple times"
		print "-i/--in <file/dir>\t\tInput file or directory"
		print "-o/--out <file>\t\t\tOutput file name"
		print "-h/--help\t\t\tPrint this"

if __name__ == "__main__":
	obj = square_code()
	obj.main(sys.argv[1:])
