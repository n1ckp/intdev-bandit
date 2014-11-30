import argparse, os, sys
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
		print "loading model..."
		self.clf = joblib.load(args.model_file)
		if args.pca_file != "":
			print "loading PCA..."
			pca = True
			self.pca = joblib.load(args.pca_file)
		fft = args.fft
		self.queue = []
		data_dimensions = 9
		self.c = calibration.Calibration()
		print "Initialising buffer, please wait"
		self.stream = StreamRead(args.input_stream)
		while len(self.queue) < args.window_size:
			records = self.stream.readFromStream()
			for record in records:
				if len(record) == data_dimensions and '' not in record:
					record = list(self.c.process(*[float(i) for i in record]))
					record[3] = -1533
					record[4] = -1533
					record[5] = -1533
					self.queue.append(record)

		print "Initialised"

		#Main loop
		while True:
			if len(self.queue) >= args.window_size:
				data = self.queue[:args.window_size]
				self.queue.pop(0)
				data = numpy.array(data).astype(float)
				print data
				if fft: 
					data = self.featureExtract(data, 6)
				if pca:
					data = self.pca.transform(data)

				prediction = self.clf.predict(data)
				print prediction
				prediction = numpy.sum(self.clf.decision_function(data))
				print prediction

			records = self.stream.readFromStream()
			for record in records:
				if len(record) == data_dimensions and '' not in record:
					record = list(self.c.process(*[float(i) for i in record]))
					record[3] = -1533
					record[4] = -1533
					record[5] = -1533
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
	parser.add_argument("-ws", action = "store", default = 5, type = int, dest = "window_size", help = "The size of the input window (default: 5)")
	parser.add_argument("-S", action = "store", default = "/dev/input/smartshoes", type = str, dest = "input_stream", help = "The input stream to read from (deafult: /dev/input/smartshoes")
	parser.add_argument("-FFT", action = "store_true", default = False, dest = "fft", help = "Perform fft feature extraction on input")
	
	inputArgs = parser.parse_args()
	main(inputArgs)