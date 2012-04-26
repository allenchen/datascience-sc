import numpy as np
from sklearn.linear_model import *
from sklearn.tree import *
from sklearn.cross_validation import KFold

class StackingModel:
    def __init__(self, models):
        # Actually create the majority model
        self.model_0 = LinearRegression()
        self.model_1 = LinearRegression()
        self.models = models

    def fit(self, features, targets):
        # Train all the passed in models first using 10-fold CV
        cv = KFold(len(targets), k=10)
        probs = []
        probs_targets = []
        
        for i in range(len(self.models)):
            pm_probs = []
            for j, (train, test) in enumerate(cv):
                self.models[i].fit(features[train], targets[train])
                pm_probs.extend(self.models[i].predict_proba(features[test]))
                if (i == 0):
                    probs_targets.extend(targets[test])
            probs.append(pm_probs)
        probs_targets = np.array(probs_targets).astype(np.int)

        # Transform the results
        results_0 = []
        results_1 = []
        targets_0 = []
        targets_1 = []
        for i in range(len(features)):
            if probs_targets[i] == 0:
                targets_0.append(1)
                targets_1.append(0)
            else:
                targets_0.append(0)
                targets_1.append(1)

            mfeature_0 = []
            mfeature_1 = []
            for j in range(len(probs)):
                mfeature_0.append(probs[j][i][0])
                mfeature_1.append(probs[j][i][1])
            results_0.append(mfeature_0)
            results_1.append(mfeature_1)

        results_0 = np.array(results_0).astype(np.float)
        results_1 = np.array(results_1).astype(np.float)
        targets_0 = np.array(targets_0).astype(np.float)
        targets_1 = np.array(targets_1).astype(np.float)
        
        # Train on these results
        self.model_0.fit(results_0, targets_0)
        self.model_1.fit(results_1, targets_1)

        # Re-train the models on the whole test set
        for i in range(len(self.models)):
            self.models[i].fit(features, targets)

        return self

    def predict_meta(self, features):
        # Predict the probabilities
        probs = []
        for i in range(len(self.models)):
            probs.append(self.models[i].predict_proba(features))

        # Transform the probabilities
        results_0 = []
        results_1 = []
        for i in range(len(features)):
            mfeature_0 = []
            mfeature_1 = []
            for j in range(len(probs)):
                mfeature_0.append(probs[j][i][0])
                mfeature_1.append(probs[j][i][1])
            results_0.append(mfeature_0)
            results_1.append(mfeature_1)
        results_0 = np.array(results_0).astype(np.float)
        results_1 = np.array(results_1).astype(np.float)

        return (results_0, results_1)
    
    def predict(self, features):
        results_0, results_1 = self.predict_meta(features)
        predict_0 = self.model_0.predict(results_0)
        predict_1 = self.model_1.predict(results_1)

        prediction = []

        for r0, r1 in zip(predict_0, predict_1):
            if r0 > r1:
                prediction.append(0)
            else:
                prediction.append(1)

        prediction = np.array(prediction).astype(np.int)
        return prediction

    def predict_proba(self, features):
        results_0, results_1 = self.predict_meta(features)
        predict_0 = self.model_0.predict(results_0)
        predict_1 = self.model_1.predict(results_1)

        prediction = []

        for r0, r1 in zip(predict_0, predict_1):
            prediction.append([r0, r1])

        prediction = np.array(prediction).astype(np.float)
        return prediction

