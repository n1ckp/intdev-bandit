from seqlearn.evaluation import SequenceKFold
from sklearn import cross_validation
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import numpy
import matplotlib.pyplot as plt

#Perform stratified crossvcalidation on sequence classifiers
def seq_cross_val_score(clf, data, classes, seq_lengths, cv=10, n_jobs=1, show_cm=True):
	scores = []
	folds = SequenceKFold(seq_lengths, cv)
	folds = seqStratifiedKFold(classes, seq_lengths, cv=10)
	conf_mat = None
	
	for fold in folds:
		train_indices = fold[0]
		train_seq_lengths = fold[1]
		test_indices = fold[2]
		test_seq_lengths = fold[3]

		train_data = []
		train_classes = []
		test_data = []
		test_classes = []

		for i in xrange(0, len(train_indices)):
			train_data.append(data[train_indices[i]])
			train_classes.append(classes[train_indices[i]])

		for i in xrange(0, len(test_indices)):
			test_data.append(data[test_indices[i]])
			test_classes.append(classes[test_indices[i]])

		clf.fit(train_data, train_classes, train_seq_lengths)

		pred_classes  = clf.predict(test_data, test_seq_lengths)

		scores.append(accuracy_score(test_classes, pred_classes))

		if show_cm:
			cm = confusion_matrix(test_classes, pred_classes)
			
			if conf_mat == None:
				conf_mat = cm
			else:
				conf_mat = numpy.add(conf_mat, cm)

	if show_cm:
		dispConfusionMatrix(conf_mat, train_classes)
	return numpy.array(scores) 

#Use sklearns stratified kfold to produce sequence aware stratified K fold
def seqStratifiedKFold(classes, seq_lengths, cv=3):
	compressed_classes = []
	original_idexes = []
	orginal_length = []
	#Compress class list so that all classes have length 1
	#store origional indexes and lengths for decompression
	seq_len_ptr = 0
	i = 0
	while i <  len(classes):
		original_idexes.append(i)
		orginal_length.append(seq_lengths[seq_len_ptr])
		compressed_classes.append(classes[i])
		i += seq_lengths[seq_len_ptr]
		seq_len_ptr = seq_len_ptr + 1

	#Perform startified cross validation
	skf = cross_validation.StratifiedKFold(compressed_classes, n_folds=cv)
	folds = []

	#Take produced stratifed folds and decompress to give sequence aware folds
	for train, test in skf:
		decompressed_train = []
		decompressed_train_seq_lengths = []
		decompressed_test = []
		decompressed_test_seq_lengths = []
		for t in train:
			idx = original_idexes[t]
			length = orginal_length[t]
			decompressed_train_seq_lengths.append(length)
			for i in xrange(0, length):
				decompressed_train.append(idx + i)

		for t in test:
			idx = original_idexes[t]
			length = orginal_length[t]
			decompressed_test_seq_lengths.append(length)
			for i in xrange(0, length):
				decompressed_test.append(idx + i)

		folds.append([decompressed_train, decompressed_train_seq_lengths, decompressed_test, decompressed_test_seq_lengths])

	return folds


#perform standard stratified crossvalidation
def cross_val_score(clf, data, classes, cv=10, n_jobs=1, show_cm=True):
	scores = []
	conf_mat = None
	#compute stratifed folds
	skf = cross_validation.StratifiedKFold(classes, n_folds=cv)
	for train, test in skf:
		train_data = []
		train_classes = []
		test_data = [] 
		test_classes = []

		for t in train:
			train_data.append(data[t])
			train_classes.append(classes[t])

		for t in test:
			test_data.append(data[t])
			test_classes.append(classes[t])

		clf.fit(train_data, train_classes)

		pred_classes  = clf.predict(test_data)

		scores.append(accuracy_score(test_classes, pred_classes))

		if show_cm:
			cm = confusion_matrix(test_classes, pred_classes)
			
			if conf_mat == None:
				conf_mat = cm
			else:
				conf_mat = numpy.add(conf_mat, cm)

	if show_cm:
		dispConfusionMatrix(conf_mat, train_classes)

	return numpy.array(scores) 


#Display the confusion matrix for the given classes
def dispConfusionMatrix(conf_mat, train_classes):
		classOrder, y  = numpy.unique(train_classes, return_inverse=True)
		for i in xrange(0,len(classOrder)):
				print str(i) + "= " + str(classOrder[i])
		print conf_mat
		plt.matshow(conf_mat)
		plt.title('Confusion matrix')
		plt.colorbar()
		plt.ylabel('True label')
		plt.xlabel('Predicted label')
		plt.show()





