# Import validate functions
from ensemble.MajorityModel import MajorityModel
from validate import validate

# Import models to use
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

def evaluate_logit(player_data):
    player_model = LogisticRegression(penalty='l1')
    results = validate.cross_validate(player_data, player_model, 10)
    validate.draw_roc_curves(results)

def evaluate_naive(player_data):
    player_model = GaussianNB()
    results = validate.cross_validate(player_data, player_model, 10)
    validate.draw_roc_curves(results)

def evaluate_dtree(player_data):
    player_model = DecisionTreeClassifier()
    results = validate.cross_validate(player_data, player_model, 10)
    validate.draw_roc_curves(results)

def evaluate_svm(player_data):
    player_model = SVC(probability=True, kernel='rbf', gamma=0.3)
    results = validate.cross_validate(player_data, player_model, 10)
    validate.draw_roc_curves(results)

def evaluate_forest(player_data):
    player_model = RandomForestClassifier(n_estimators=30, n_jobs=-1)
    results = validate.cross_validate(player_data, player_model, 10)
    validate.draw_roc_curves(results)

def evaluate_wmm(player_data):
    models = [LogisticRegression(penalty='l1'),
              GaussianNB(),
              DecisionTreeClassifier(),
              SVC(probability=True, kernel='rbf', gamma=0.3),
              RandomForestClassifier(n_estimators=30, n_jobs=-1)]
    player_model = MajorityModel(models)
    results = validate.cross_validate(player_data, player_model, 10)
    validate.draw_roc_curves(results)
    
