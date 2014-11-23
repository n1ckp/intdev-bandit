import io

#class for writing to a named stream
class StreamWrite():

	#constructor for class
	def __init__(self, fname):
		#open file for binary writing    
		self.stream = io.open(fname, 'w+b')
		self.stream.seek(0)
		self.stream.truncate()
		self.MAX_BUFF_SIZE = 1024*1024*1024

	#write values is list data to stream
	def writeToStream(self, data):
	    #if file size is past limit trunacte
	    if self.stream.tell() > self.MAX_BUFF_SIZE:
	        self.stream.seek(0)
	        self.stream.truncate()

	    #encode data and write to stream
	    enc_data = ','.join(map(str,data)) + '\n'
	    self.stream.write(enc_data)
	    #flush so reciver gets near real time updates
	    self.stream.flush()