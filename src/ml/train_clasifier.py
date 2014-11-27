import argparse
import multiprocessing

from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn import svm
from sklearn.naive_bayes import MultinomialNB
from sklearn import cross_validation, metrics
from sklearn.externals import joblib
from sklearn.decomposition import PCA

from seqlearn.perceptron import StructuredPerceptron
from seqlearn.hmm import MultinomialHMM

from MakeSamples.MakeSamples import SamplesFromDir
from Evaluation import CrossValidation
from Preprocessing.FeatureExtraction import FequencyExtraction

#Base classifier utility methods
def baseClassifierTest(clf, clf_name, data, classes, n_folds, metric=''):
	print("Testing: ", clf_name)
	num_cores = multiprocessing.cpu_count()
	scores = CrossValidation.cross_val_score(clf, data, classes, cv=n_folds, n_jobs=num_cores)
	print(clf_name, ", Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

def baseClassifierTrain(clf, clf_name, data, classes, dump_file):
	print("Training: ", clf_name)
	clf.fit(data, classes)
	joblib.dump(clf, dump_file)

def baseSeqClassifierTest(clf, clf_name, data, classes, seq_lengths, n_folds, metric=''):
	print("Testing: ", clf_name)
	num_cores = multiprocessing.cpu_count()
	scores = CrossValidation.cross_val_score(clf, data, classes, cv=n_folds, n_jobs=num_cores)
	print(clf_name, ", Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

def baseSeqClassifierTrain(clf, clf_name, data, classes, seq_lengths, dump_file):
	print("Training: ", clf_name)
	clf.fit(data, classes, seq_lengths)
	joblib.dump(clf, dump_file)


#perform crossfold validation on passive agressive calssifier
def testPassiveAgressive(data, classes, n_folds, metric=''):
	clf = PassiveAggressiveClassifier(loss='squared_hinge', C=1.0)
	baseClassifierTest(clf, "Passive Aggressive Classifier", data, classes, n_folds, metric)


#train passive agressive classifier on all data and dump model to file
def trainPassiveAgressive(data, classes, dump_file):
	clf = PassiveAggressiveClassifier(loss='squared_hinge', C=1.0)
	baseClassifierTrain(clf, "Passive Aggressive Classifier", data, classes, dump_file)


#perform crossfold validation on passive agressive calssifier
def testSVM(data, classes, n_folds, metric=''):
	clf = svm.SVC()
	baseClassifierTest(clf, "Support Vector Machine", data, classes, n_folds, metric)

#train passive agressive classifier on all data and dump model to file
def trainSVM(data, classes, dump_file):
	clf = svm.SVC()
	baseClassifierTrain(clf, "Support Vector Machine", data, classes, dump_file)

#perform crossfold validation on Multinomial NB calssifier
def testMultinomialNaiveBayes(data, classes, n_folds, metric=''):
	clf = MultinomialNB(alpha=1.0)
	baseClassifierTest(clf, "Multinomial Naive Bayes", data, classes, n_folds, metric)

#train Multinomial NBclassifier on all data and dump model to file
def trainMultinomialNaiveBayes(data, classes, dump_file):
	clf = MultinomialNB(alpha=1.0)
	baseClassifierTrain(clf, "Multinomial Naive Bayes", data, classes, dump_file)

def testStructuredPerceptron(data, classes, seq_lengths, n_folds, metric=''):
	clf = StructuredPerceptron(max_iter=10)
	baseSeqClassifierTest(clf, "Structured Perceptron", data, classes, seq_lengths, n_folds, metric)

#train structured classifier on all data and dump model to file
def trainStructuredPerceptron(data, classes, seq_lengths, dump_file):
	clf = StructuredPerceptron(max_iter=10)
	baseSeqClassifierTrain(clf, "Structured Perceptron", data, classes, seq_lengths, dump_file)


def testMultinomialHMM(data, classes, seq_lengths, n_folds, metric=''):
	clf = MultinomialHMM(decode='bestfirst', alpha=1.0)
	baseSeqClassifierTest(clf, "Multinomial Hidden Markov Model", data, classes, seq_lengths, n_folds, metric)
	

#train multinomial HMM classifier on all data and dump model to file
def trainMultinomialHMM(data, classes, seq_lengths, dump_file):
	clf = MultinomialHMM(decode='viterbi', alpha=0.01)
	baseSeqClassifierTrain(clf, "Multinomial Hidden Markov Model", data, classes, seq_lengths, dump_file)
	
	
def main(args):
	cv_folds = 10
	data, classes, seq_lengths = SamplesFromDir(args.input_dir)

	if args.preprocess == 'freq':
		data, classes = FequencyExtraction(data, classes, seq_lengths)

	if args.pca_comps:
		pca = PCA(n_components=args.pca_comps)
		pca.fit(data)
		data = pca.transform(data)

	if args.dump_file != '':
		if args.classifier == 'pa':
			trainPassiveAgressive(data, classes, args.dump_file)
		elif args.classifier == 'sp':
			trainStructuredPerceptron(data, classes, seq_lengths, args.dump_file)
		elif args.classifier == 'mhmm':
			trainMultinomialHMM(data, classes, seq_lengths, args.dump_file)
		elif args.classifier == 'mnb':
			trainMultinomialNaiveBayes(data, classes, args.dump_file)
		elif args.classifier == 'svm':
			trainSVM(data, classes, args.dump_file)
		else:
			raise NameError("Unknown Classifer type")	
	else:	
		if args.classifier == 'pa':
			testPassiveAgressive(data, classes, cv_folds)
		elif args.classifier == 'sp':
			testStructuredPerceptron(data, classes, seq_lengths, cv_folds)
		elif args.classifier == 'mhmm':
			testMultinomialHMM(data, classes, seq_lengths, cv_folds)
		elif args.classifier == 'mnb':
			testMultinomialNaiveBayes(data, classes, cv_folds)
		elif args.classifier == 'svm':
			testSVM(data, classes, cv_folds)
		else:
			raise NameError("Unknown Classifer type")	
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Train classifers on traing data')
	parser.add_argument('input_dir', help="The directory containing training data files of the form <class>_<uuid>.csv")
	parser.add_argument('--dump_file', default='', help="Dump the trained model to a file")
	parser.add_argument('--classifier', default='pa', help="The directory containing taring data files of the form <class>_<uuid>.csv")
	parser.add_argument('--pca', default=0, type=int, dest='pca_comps', help="The Number of components to extract with pca (default : 0<off>)")
	parser.add_argument('--preprocess', default='', dest='preprocess', help="Apply preprocessing to data <freq>")
	args = parser.parse_args()
	main(args)