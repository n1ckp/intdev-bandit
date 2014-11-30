import argparse, os, sys, re
sys.path.append(os.path.abspath("../"))

from utils.streamUtils.StreamRead import StreamRead

from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn import svm
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import cross_validation, metrics
from sklearn.externals import joblib
from sklearn.decomposition import PCA
from receiver import calibration

import numpy

class main():

	def __init__(self, args):
		#confidence interval on classification
		self.confidence_lim = 0.65
		print "loading model..."
		self.clf = joblib.load(args.model_file)
		self.classes = []
		if args.pca_file != "":
			print "loading PCA..."
			pca = True
			self.pca = joblib.load(args.pca_file)
		if args.classes_file != "":
			f = open(args.classes_file, "r")
			line = f.readline()
			line = re.sub('\s+','', line)
			self.classes = line.split(',')
			print self.classes
		fft = args.fft
		self.queue = []
		data_dimensions = 9
		#self.c = calibration.Calibration()
		print "Initialising buffer, please wait"
		self.stream = StreamRead(args.input_stream, exclude_indexes=[9])
		while len(self.queue) < args.window_size:
			records = self.stream.readFromStream()
			for record in records:
				print record
				if len(record) == data_dimensions and '' not in record:
					self.queue.append(record)

		print "Initialised"

		#Main loop
		while True:
			if len(self.queue) >= args.window_size:
				data = self.queue[:args.window_size]
				self.queue.pop(0)
				data = numpy.array(data).astype(float)
				if fft: 
					data = self.featureExtract(data, 6)
				if pca:
					data = self.pca.transform(data)

				prediction = self.clf.predict(data)
				probs = self.clf.predict_proba(data)
				confidence = probs[0][self.classes.index(prediction[0])]
				if confidence >= self.confidence_lim:
					print prediction
					print "confidence:", confidence
				else:
					print "Im not sure"

			records = self.stream.readFromStream()
			for record in records:
				if len(record) == data_dimensions and '' not in record:
					self.queue.append(record)


	def featureExtract(self, input, n_freqs):
		freqs = numpy.fft.fft(input, n=n_freqs, axis=0)
		freqs = numpy.reshape(freqs, freqs.size)
		freqs = freqs.real
		return freqs


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Run Online classification of input for device')
	parser.add_argument("model_file", action = "store", default = '', type=str, help = "The model file to load")
	parser.add_argument("-pca", action = "store", default = "", type = str, dest = "pca_file", help = "A serialised pca object to load")
	parser.add_argument("-cls", action = "store", default = "", type = str, dest = "classes_file", help = "A file containg the class ordering for the classifer")
	parser.add_argument("-ws", action = "store", default = 5, type = int, dest = "window_size", help = "The size of the input window (default: 5)")
	parser.add_argument("-S", action = "store", default = "/dev/input/smartshoes", type = str, dest = "input_stream", help = "The input stream to read from (deafult: /dev/input/smartshoes")
	parser.add_argument("-FFT", action = "store_true", default = False, dest = "fft", help = "Perform fft feature extraction on input")
	
	inputArgs = parser.parse_args()
	main(inputArgs)