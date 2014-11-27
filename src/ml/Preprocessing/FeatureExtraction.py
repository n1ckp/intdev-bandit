import numpy

#Apply fft to data sequence to transfrom from time domain to the freqency domain
#n_freqs is the number of freqencies to extract
def FequencyExtraction(data, classes, seq_lengths, n_freqs=12):
	data_out = []
	classes_out = []
	i = 0
	sequence = 0
	while i  < len(data):
		tmp_data = []
		for j in xrange(0, seq_lengths[sequence]):
			tmp_data.append(data[i + j])
		tmp_data = numpy.array(tmp_data)
		freqs = numpy.fft.fft(tmp_data, n=n_freqs, axis=0)
		freqs = numpy.reshape(freqs, freqs.size)
		freqs = freqs.real
		data_out.append(freqs)
		classes_out.append(classes[i])
		i = i + seq_lengths[sequence]
		sequence = sequence + 1

	return numpy.array(data_out), numpy.array(classes_out)

