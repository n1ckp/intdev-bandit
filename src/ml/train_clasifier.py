import argparse
import multiprocessing

from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn import cross_validation, metrics
from sklearn.externals import joblib

from MakeSamples.MakeSamples import SamplesFromDir

#perform crossfold validation on passive agressive calssifier
def testPassiveAgressive(data, classes, n_folds, metric=''):
	num_cores = multiprocessing.cpu_count()
	clf = PassiveAggressiveClassifier(loss='squared_hinge', C=1.0)
	scores = cross_validation.cross_val_score(clf, data, classes, cv=n_folds, n_jobs=num_cores)
	print("Passive Agressivce Classifier, Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

#train passive agressive classifier on all data and dump model to file
def trainPassiveAgressive(data, classes, dump_file):
	num_cores = multiprocessing.cpu_count()
	clf = PassiveAggressiveClassifier(loss='squared_hinge', C=1.0)
	clf.fit(data, classes)
	joblib.dump(clf, dump_file)
	

def main(args):
	cv_folds = 10
	data, classes = SamplesFromDir(args.input_dir)
	if args.dump_file != '':
		if args.classifier == 'pa':
			trainPassiveAgressive(data, classes, args.dump_file)
		else:
			raise NameError("Unknown Classifer type")	
	else:	
		if args.classifier == 'pa':
			testPassiveAgressive(data, classes, cv_folds)
		else:
			raise NameError("Unknown Classifer type")	
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Train classifers on traing data')
	parser.add_argument('input_dir', help="The directory containing training data files of the form <class>_<uuid>.csv")
	parser.add_argument('--dump_file', default='', help="Dump the trained model to a file")
	parser.add_argument('--classifier', default='pa', help="The directory containing taring data files of the form <class>_<uuid>.csv")
	args = parser.parse_args()
	main(args)