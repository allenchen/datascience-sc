#!/usr/bin/env python
from evaluate import evaluate as ev
from optparse import OptionParser
from preprocess import preprocess as pp

# Import models to use
from sklearn.linear_model import *
from sklearn.naive_bayes import *
from sklearn.tree import *
from sklearn.svm import *
from sklearn.ensemble import *
from ensemble.MajorityModel import MajorityModel
from ensemble.StackingModel import StackingModel

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
    ev.evaluate_logit(data[pid],"2_" + str(pid) + "_logit")
    print "Evaluating Multi"
    ev.evaluate_naive(data[pid],"2_" + str(pid) + "_multi")
    print "Evaluating Decision Tree"
    ev.evaluate_dtree(data[pid],"2_" + str(pid) + "_dtree")
    print "Evaluating SVM"
    ev.evaluate_svm(data[pid], "2_" + str(pid) + "_svm")
    print "Evaluating Ensemble - Forest"
    ev.evaluate_forest(data[pid], "2_" + str(pid) + "_forest")
    print "Evaluating Ensemble - Weighted"
    ev.evaluate_wmm(data[pid], "2_" + str(pid) + "_wmm")
    print "Evaluating Ensemble - Stacking"
    ev.evaluate_smm(data[pid], "2_" + str(pid) + "_smm")

def create_model(pid, data):
    # Create the model
    models = [LogisticRegression(penalty='l1'),
              MultinomialNB(),
              DecisionTreeClassifier(),
              SVC(probability=True, kernel='rbf', gamma=0.3),
              RandomForestClassifier(n_estimators=20, n_jobs=-1)]
    player_model = StackingModel(models)

    # Fit the model
    player_model.fit(data[pid]['data'], data[pid]['targets'])

    # Save the model
    pickle.dump(player_model, open("save/" + str(pid) + ".pickle", "wb"))

    return player_model

def predict_model_features(pid, cid, m1, m2):
    pmodel = pickle.load(open("save/" + str(pid) + ".pickle", "rb"))
    cmodel = pickle.load(open("save/" + str(cid) + ".pickle", "rb"))

    ppredictions = pmodel.predict(m1)[0]
    cpredictions = cmodel.predict(m2)[0]
    pprob = pmodel.predict_proba(m1)[0]
    cprob = cmodel.predict_proba(m2)[0]

    print "==================="
    print "WINNER: " + str(pid)
    if ppredictions == cpredictions:
        print "PREDICTED WINNER: TIE"
    elif ppredictions > cpredictions:
        print "PREDICTED WINNER: " + str(pid)
    else:
        print "PREDICTED WINNER: " + str(cid)

    print str(pid) + " probabilities:"
    print pprob
    print str(cid) + " probabilities:"
    print cprob
    print "==================="

def predict_model(time, mid, pid, prace, cid, crace):
    m1 = pp.get_features(time, mid, pid, prace, cid, crace)
    m2 = pp.get_features(time, mid, cid, crace, pid, prace)

    return predict_model_features(pid, cid, m1, m2)


if __name__ == "__main__":
    predict_model(734618, 510, 2322, 0, 70, 1)
    predict_model(734618, 500, 2322, 0, 70, 1)
    predict_model(734618, 510, 959, 1, 1849, 1)
    predict_model(734618, 538, 959, 1, 1849, 1)
    predict_model(734618, 528, 2322, 0, 959, 1)
    predict_model(734618, 527, 959, 1, 2322, 0)
    predict_model(734618, 479, 2322, 0, 959, 1)
    predict_model(734618, 528, 1849, 1, 70, 1)
    predict_model(734618, 479, 1849, 1, 70, 1)
    predict_model(734618, 527, 1849, 1, 959, 1)
    predict_model(734618, 499, 1849, 1, 959, 1)
    
