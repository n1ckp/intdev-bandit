import os
import glob
import re
import ntpath
import numpy
import random

#geneerate sampels for directory of CSV files
def SamplesFromDir(directory, sep='_', data_dimensions=17, exclude_classes = [], exclude_indexes=[]):
	data = []
	classes =[]
	seq_lengths = []
	files = glob.glob(os.path.join(directory, '*.csv'))
	#process each file in directory
	for file_name in files:
		print "processing file: " + file_name
		#extract class name from file name
		class_name = path_leaf(file_name).split(sep, 1)[0]
		if class_name not in exclude_classes:
			sample_file = open(file_name, 'r')
			seq_length = 0
			for line in sample_file:
				#clean up line
				line = re.sub('\s+','', line)
				sample = line.split(',')
				#check for corrupt data
				if len(sample) != data_dimensions or '' in sample:
					break
				data.append([sample[i] for i in range(0, len(sample)) if i not in  exclude_indexes])
				classes.append(class_name)
				seq_length = seq_length + 1
			if seq_length > 0:
				seq_lengths.append(seq_length)
	data = numpy.array(data).astype(float)
	classes  = numpy.array(classes)
	seq_lengths = numpy.array(seq_lengths).astype(int)

	#data, classes, seq_lengths = resample(data, classes, seq_lengths, 5)

	return numpy.array(data).astype(float), numpy.array(classes), numpy.array(seq_lengths).astype(int)

#get the file name from a path
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def resample(data, classes, seq_lengths, resample_rate, noise_factor=0.1):
	resample_data = []
	resample_classes = []
	resample_seq_lengths = []

 	i = 0
 	seq = 0
 	while i < len(data):
 		for j in xrange(i, i + seq_lengths[seq]):
 			resample_data.append(data[j])
 			resample_classes.append(classes[j])
 		resample_seq_lengths.append(seq_lengths[seq])

 		for k in xrange(0, resample_rate):
 			for j in xrange(i, i + seq_lengths[seq]):
 				resampled_record = []
 				for q in xrange(0, len(data[j])):
 					data_noise = noise_factor * data[j][q]
	 				resampled_record.append(data[j][q] + random.uniform(-data_noise, data_noise))
	 			resample_data.append(resampled_record)	
	 			resample_classes.append(classes[j])
	 		resample_seq_lengths.append(seq_lengths[seq])

	 	i += seq_lengths[seq]
	 	seq += 1
	return resample_data, resample_classes, resample_seq_lengths