import torch
import os
import json
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, matthews_corrcoef, roc_auc_score, roc_curve, auc, confusion_matrix
import torch.nn.functional as F
import numpy as np
from itertools import cycle
import math
from sklearn.preprocessing import label_binarize
from torchmetrics import Accuracy, AUROC, AUC, MatthewsCorrCoef, Recall, Specificity, F1Score

class AverageMeter(object):
    """
    Computes and stores the average and
    current value.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

def prepare_dirs(config):
    for path in [config.ckpt_dir]:
        if not os.path.exists(path):
            os.makedirs(path)

def save_config(config):
    model_name = config.save_name
    filename = model_name + '_params.json'
    param_path = os.path.join(config.ckpt_dir, filename)

    print("[*] Model Checkpoint Dir: {}".format(config.ckpt_dir))
    print("[*] Param Path: {}".format(param_path))

    with open(param_path, 'w') as fp:
        json.dump(config.__dict__, fp, indent=4, sort_keys=True)


def accuracy(output, true):
    pred = output.numpy().argmax(axis=1)
    acc = accuracy_score(true.numpy(), pred)
    return acc


def cal_metrics(confusion_matrix):
    # n_classes = confusion_matrix.shape[0]
    metrics_result = []
    n_classes = 6
    for i in range(n_classes):
        ALL = np.sum(confusion_matrix)
        TP = confusion_matrix[i, i]
        FP = np.sum(confusion_matrix[:, i]) - TP
        FN = np.sum(confusion_matrix[i, :]) - TP
        TN = ALL - TP - FP - FN
        Pre = TP/(TP+FP)
        Sen = TP/(TP+FN)
        Spe = TN/(TN+FP)
        F1 = (2*Pre*Sen)/(Pre+Sen)
        MCC = ((TP*TN)-(FP*FN))/(math.sqrt((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN)))
        metrics_result.append([MCC, F1, Sen, Spe, Pre])
    return metrics_result


def metrics(output, true, target):
    output = np.array(output)
    true = np.array(true)
    binary_true = label_binarize(true, classes=[i for i in range(6)])
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    thresholds = dict()


    prediction_fpr5, prediction = binary_threshold(fpr, thresholds, output, binary_true, target)
    max_prediction = np.argmax(output, axis=1)
    cfm = confusion_matrix(true, max_prediction)
    max_binary = label_binarize(max_prediction, classes=[i for i in range(6)])
    print('\n')
    print('Max prediction:')
    print(cfm)

    res = cal_metrics(cfm)
    for i in range(cfm.shape[0]):
        print('partner:%s -auc:%s -MCC:%s -F1:%s -Sen:%s -Spe:%s -Pre:%s' % (target[i],
                                                                             str(round(roc_auc[target[i]], 3)),
                                                                             str(round(res[i][0], 3)),
                                                                             str(round(res[i][1], 3)),
                                                                             str(round(res[i][2], 3)),
                                                                             str(round(res[i][3], 3)),
                                                                             str(round(res[i][4], 3))))
    return max_prediction, prediction_fpr5, prediction




def save_result(save_path, protein, sequence, output, max_binaryprediction, prediction_fpr5):
    # input sequence: string
    sequence = list(sequence.strip())
    print(len(sequence))
    # max_binaryprediction = [np.argmax(y) for y in output]
    print('max prediction:')
    print(''.join('%s' %id for id in max_binaryprediction))
    print('fpr5 prediction')
    print(''.join('%s' % id for id in prediction_fpr5))

    prediction = {
        'residue': sequence,
        'probability for non-RNA binding': list(output[:, 0]),
        'probability for rRNA binding': list(output[:, 1]),
        'probability for tRNA binding': list(output[:, 2]),
        'probability for snRNA binding': list(output[:, 3]),
        'probability for mRNA binding': list(output[:, 4]),
        'probability for SRP binding': list(output[:, 5]),
        'multi_class label': max_binaryprediction,
        'fpr5_label': prediction_fpr5
    }
    dataframe = pd.DataFrame(prediction)
    dataframe.to_csv(save_path+protein+'_prediction.csv', sep=',')



def binary_threshold(fpr, threshold, prediction, true, target):
    f1_value = dict()
    recall = dict()
    mcc = dict()
    precision = dict()
    threshold_prob = dict()
    accuracy = dict()
    for i in range(len(target)):
        threshold_prob[target[i]] = []
        for j in range(len(fpr[target[i]])):
            if fpr[target[i]][j] >= 0.05:
                threshold_prob[target[i]].append(threshold[target[i]][j])

    prediction_fpr5 = []

    for y in prediction:
        eachpred_5 = []
        for j in range(len(target)):
            if y[j] >= threshold_prob[target[j]][0]:
                eachpred_5.append(1)
            else:
                eachpred_5.append(0)
        prediction_fpr5.append(eachpred_5)
    prediction_fpr5 = np.array(prediction_fpr5)

    for i in range(1, len(target)):
        prediction_target = list(prediction_fpr5[:,i])
        if prediction_target.count(0) == 0:
            continue
        if prediction_target.count(0) > 0:
            prediction = prediction_target

    print("\n FPR at 5%:")
    for i in range(len(target)):
        accuracy[target[i]] = accuracy_score(true[:, i], prediction_fpr5[:, i])
        f1_value[target[i]] = f1_score(true[:, i], prediction_fpr5[:, i])
        recall[target[i]] = recall_score(true[:, i], prediction_fpr5[:, i])
        precision[target[i]] = precision_score(true[:, i], prediction_fpr5[:, i])
        mcc[target[i]] = matthews_corrcoef(true[:, i], prediction_fpr5[:, i])
        print('the class %s - acc:%s - f1:%s - recall:%s - precision:%s -mcc:%s' % (str(target[i]),
                                                                                    str(round(accuracy[target[i]], 3)),
                                                                                    str(round(f1_value[target[i]], 3)),
                                                                                    str(round(recall[target[i]], 3)),
                                                                                    str(round(precision[target[i]],
                                                                                              3)),
                                                                                    str(round(mcc[target[i]], 3))))


    return prediction_fpr5, prediction















