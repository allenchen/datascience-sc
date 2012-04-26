from evaluate import evaluate as ev
from optparse import OptionParser
from preprocess import preprocess as pp

import pickle
import os.path

def load_data():
    # Check to see if data.pickle exists
    if os.path.isfile("data.pickle"):
        # Start importing data
        data = pickle.load(open("data.pickle", "rb"))
    else:
        data = pp.process_data()
        pickle.dump(data, open("data.pickle", "wb"))

    return data

def evaluate_model(pid, data):
    print "Evaluating Logit"
    ev.evaluate_logit(data[pid],pid)
    print "Evaluating Naive"
    ev.evaluate_naive(data[pid],pid)
    print "Evaluating Decision Tree"
    ev.evaluate_dtree(data[pid],pid)
    print "Evaluating SVM"
    ev.evaluate_svm(data[pid],pid)
    print "Evaluating Ensemble - Forest"
    ev.evaluate_forest(data[pid],pid)
    print "Evaluating Ensemble - Weighted"
    ev.evaluate_wmm(data[pid],pid)
    print "Evaluating Ensemble - Stacking"
    ev.evaluate_smm(data[pid],pid)
