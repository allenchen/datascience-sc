# Import validate functions
from ensemble.MajorityModel import MajorityModel
from ensemble.StackingModel import StackingModel
from validate import validate

# Import metrics
from sklearn.metrics import precision_recall_fscore_support

# Import models to use
from sklearn.linear_model import *
from sklearn.naive_bayes import *
from sklearn.tree import *
from sklearn.svm import *
from sklearn.ensemble import *

def evaluate_whole(data, model):
    predictions = model.fit(data['data'], data['targets']).predict(data['data'])
    results = precision_recall_fscore_support(data['targets'], predictions)
    return results

def evaluate_logit(player_data, id):
    player_model = LogisticRegression(penalty='l1')
    results = validate.cross_validate(player_data, player_model, 10)
    validate.save_roc_curves(results, "logit/" + str(id))
    #print "Logistic regression results:"
    #print evaluate_whole(player_data, player_model)

def evaluate_naive(player_data, id):
    player_model = MultinomialNB()
    results = validate.cross_validate(player_data, player_model, 10)
    validate.save_roc_curves(results, "naive/" + str(id))
    #print "Naiive Baye results:"
    #print evaluate_whole(player_data, player_model)

def evaluate_dtree(player_data, id):
    player_model = DecisionTreeClassifier()
    results = validate.cross_validate(player_data, player_model, 10)
    validate.save_roc_curves(results, "dtree/" + str(id))
    #print "Decision Tree results:"
    #print evaluate_whole(player_data, player_model)

def evaluate_svm(player_data, id):
    player_model = SVC(probability=True, kernel='rbf', gamma=0.3)
    results = validate.cross_validate(player_data, player_model, 10)
    validate.save_roc_curves(results, "svm/" + str(id))
    #print "SVM results:"
    #print evaluate_whole(player_data, player_model)

def evaluate_forest(player_data, id):
    player_model = RandomForestClassifier(n_estimators=20, n_jobs=-1)
    results = validate.cross_validate(player_data, player_model, 10)
    validate.save_roc_curves(results, "forest/" + str(id))
    #print "Ensemble of forest tree results:"
    #print evaluate_whole(player_data, player_model)

def evaluate_wmm(player_data, id):
    models = [LogisticRegression(penalty='l1'),
              MultinomialNB(),
              DecisionTreeClassifier(),
              SVC(probability=True, kernel='rbf', gamma=0.3),
              RandomForestClassifier(n_estimators=20, n_jobs=-1)]
    player_model = MajorityModel(models)
    results = validate.cross_validate(player_data, player_model, 10)
    validate.save_roc_curves(results, "wmm/" + str(id))
    #print "Weighted  model results:"
    #print evaluate_whole(player_data, player_model)    

def evaluate_smm(player_data, id):
    models = [LogisticRegression(penalty='l1'),
              MultinomialNB(),
              DecisionTreeClassifier(),
              SVC(probability=True, kernel='rbf', gamma=0.3),
              RandomForestClassifier(n_estimators=20, n_jobs=-1)]
    player_model = StackingModel(models)
    results = validate.cross_validate(player_data, player_model, 10)
    validate.save_roc_curves(results, "smm/" + str(id))
    #print "Stacking model results:"
    #print evaluate_whole(player_data, player_model)    
