# Import validate functions
from validate import validate

# Import models to use
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

def evaluate_logit(player_data):
    player_model = LogisticRegression()
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
    player_model = SVC()
    results = validate.cross_validate(player_data, player_model, 10)
    validate.draw_roc_curves(results)

def evaluate_wmm(player_data):
    # This is a to-do... got to figure out if we want to go this path
    return None
