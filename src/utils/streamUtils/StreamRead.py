import io, re

#Class for reading from a named stream
class StreamRead():
	#constructor for class
	def __init__(self, fname):
		self.stream = io.open(fname, 'rb')
		self.stream.seek(0,2)
		self.pattern = re.compile(r'\s+')

	#read recent updates from stream and return list of lists containg values
	def readFromStream(self):
		records = []
		data = self.stream.readlines()
		#if new data decode
		if data:
			for reading in data:
				reading = re.sub(self.pattern, '', reading)
				records.append(reading.split(','))
		return records

	#Empty the buffer can be called before reading to discard
	#out of date data
	def emptyStreamBuffer():
		self.stream.seek(0,2)