import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cross_validation import KFold

class MajorityModel:
    # Actually create the majority model
    model = LogisticRegression()

    def __init__(self, models):
        # TO-DO: Probably should pass models as parameters
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
                pm_probs.extend(self.models[i].predict(features[test]))
                if (i == 0):
                    probs_targets.extend(targets[test])
            probs.append(pm_probs)
        probs_targets = np.array(probs_targets).astype(np.int)

        # Transform the results
        results = []
        for i in range(len(features)):
            mfeature = []
            for j in range(len(probs)):
                mfeature.append(probs[j][i])
            results.append(mfeature)
        results = np.array(results).astype(np.float)

        # Train on these results
        self.model.fit(results, probs_targets)
        return self

    def predict_meta(self, features):
        # Predict the probabilities
        probs = []
        for i in range(len(self.models)):
            probs.append(self.models[i].predict(features))

        # Transform the probabilities
        results = []
        for i in range(len(features)):
            mfeature = []
            for j in range(len(probs)):
                mfeature.append(probs[j][i])
            results.append(mfeature)
        results = np.array(results).astype(np.float)

        return results
    
    def predict(self, features):
        results = self.predict_meta(features)
        return self.model.predict(results)

    def predict_log_proba(self, features):
        results = self.predict_meta(features)
        return self.model.predict_log_proba(results)
    
    def predict_proba(self, features):
        results = self.predict_meta(features)
        return self.model.predict_proba(results)
    
