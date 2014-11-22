import os
import glob
import re
import ntpath
import numpy

#geneerate sampels for directory of CSV files
def SamplesFromDir(directory, sep='_'):
	data = []
	classes =[]
	files = glob.glob(os.path.join(directory, '*.csv'))
	#process each file in directory
	for file_name in files:
		print "processing file: " + file_name
		#extract class name from file name
		class_name = path_leaf(file_name).split(sep, 1)[0]
		sample_file = open(file_name, 'r')
		for line in sample_file:
			#clean up line
			line = re.sub('\s+','', line)
			sample = line.split(',')
			data.append(sample)
			classes.append(class_name)

	return numpy.array(data).astype(float), numpy.array(classes)

#get the file name from a path
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)