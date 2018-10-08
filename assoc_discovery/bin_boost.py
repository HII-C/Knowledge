import pandas as pd
import xgboost as xgb
from typing import Dict, List
from numpy.random import rand
from itertools import compress

from sklearn.model_selection import train_test_split
from pt_input_creation.patient_matrix import PatientMatrix
from util.xgb_param_util import XgbParam


class BinaryBoostModel:
    pt_mtrx: PatientMatrix = None
    xbg_param: XgbParam = XgbParam()
    model: xgb.Booster

    def __init__(self):
        pass

    def boost(self, causal: pd.DataFrame, result: List[int], ratio=.5):
        # x1, x2, y1, y2 = train_test_split(
        #     inp_mtrx, rslt_mtrx, train_size=ratio)
        mask: List[bool] = rand(len(causal)) < ratio
        x_train = causal[mask]
        x_test = causal[~mask]
        y_train = [d for d, s in zip(result, mask) if s]
        y_test = [d for d, s in zip(result, mask) if not s]
        self.train_booster(x_train, y_train)
        self.eval_model_acc(x_test, y_test)

    def train_booster(self, x_train, y_train):
        dtrain = xgb.DMatrix(x_train, y_train)
        self.model = xgb.train(vars(self.xbg_param), dtrain)

    def eval_model_acc(self, x_test, y_test):
        dtest = xgb.DMatrix(x_test, y_test)
        preds = self.model.predict(dtest)
        labels = dtest.get_label()
        err_per = (sum(1 for i in range(len(preds)) if int(
            preds[i] > 0.5) != labels[i]) / float(len(preds)))
        print(f'Error={err_per}')
