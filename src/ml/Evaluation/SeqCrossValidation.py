from seqlearn.evaluation import SequenceKFold
from sklearn.metrics import accuracy_score
import numpy


def cross_val_score(clf, data, classes, seq_lengths, cv=10):
	scores = []
	folds = SequenceKFold(seq_lengths, cv)
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

	return numpy.array(scores) 


