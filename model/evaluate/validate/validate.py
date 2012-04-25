import numpy as np
import pylab as pl
from scipy import interp

from sklearn.metrics import roc_curve, auc
from sklearn.cross_validation import StratifiedKFold

def cross_validate(data, model, folds):
    results = []
    features = data['data']
    targets = data['targets']

    cv = StratifiedKFold(targets, k=folds)
    for i, (train, test) in enumerate(cv):
        probs = model.fit(features[train], targets[train]).predict_proba(features[test])
        fpr, tpr, thresholds = roc_curve(targets[test], probs[:, 1])
        results.append((fpr, tpr))

    return results

def draw_roc_curves(results):
    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)
    all_tpr = []

    # Plot for each cross validation results
    for i in range(len(results)):
        fpr = results[i][0]
        tpr = results[i][1]
        mean_tpr += interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0
        roc_auc = auc(results[i][0], results[i][1])
        pl.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc))

    # Plot default for 'luck'
    pl.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')

    mean_tpr /= len(results)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)

    # Plot the mean ROC curve
    pl.plot(mean_fpr, mean_tpr, 'k--', label='Mean ROC (area = %0.2f)' % mean_auc, lw=2)

    # lot the other axis
    pl.xlim([-0.05, 1.05])
    pl.ylim([-0.05, 1.05])
    pl.xlabel('False Positive Rate')
    pl.ylabel('True Positive Rate')
    pl.title('Receiver operating characteristic example')
    pl.legend(loc="lower right")
    pl.show()
    
