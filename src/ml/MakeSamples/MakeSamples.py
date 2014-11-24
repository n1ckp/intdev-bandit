import os
import glob
import re
import ntpath
import numpy

#geneerate sampels for directory of CSV files
def SamplesFromDir(directory, sep='_', data_dimensions=9):
	data = []
	classes =[]
	seq_lengths = []
	files = glob.glob(os.path.join(directory, '*.csv'))
	#process each file in directory
	for file_name in files:
		print "processing file: " + file_name
		#extract class name from file name
		class_name = path_leaf(file_name).split(sep, 1)[0]
		sample_file = open(file_name, 'r')
		seq_length = 0
		for line in sample_file:
			#clean up line
			line = re.sub('\s+','', line)
			sample = line.split(',')
			#check for corrupt data
			if len(sample) != data_dimensions:
				break
			data.append(sample)
			classes.append(class_name)
			seq_length = seq_length + 1
		if seq_length > 0:
			seq_lengths.append(seq_length)
	
	return numpy.array(data).astype(float), numpy.array(classes), numpy.array(seq_lengths).astype(int)

#get the file name from a path
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)