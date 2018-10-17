import pandas as pd
import json
import xgboost as xgb
from typing import Dict, List
from numpy.random import rand
from itertools import compress
from operator import itemgetter
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from pt_input_creation.patient_matrix import PatientMatrix
from util.xgb_param_util import XgbParam
from util.concept_util import ConceptType, Source
from util.db_util import DatabaseHandle


class BinaryBoostModel:
    pt_mtrx: PatientMatrix = None
    xbg_param: XgbParam = XgbParam()
    model: xgb.Booster

    def __init__(self):
        pass

    def write_params(self, filename):
        tmp = vars(self.xbg_param)
        smpl = dict()
        for key, value in tmp.items():
            print(key, value, type(key), type(value))
            if isinstance(value, pd.Series):
                value.to_dict()
            smpl[key] = value

        with open(filename, 'w+') as handle:
            json.dump(smpl, handle)

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

    def concept_by_importance(self):
        scores = self.model.get_score()
        scores__ = sorted(scores.items(), key=itemgetter(1), reverse=True)
        with open('tmp.txt', 'w+') as handle:
            for key in scores__:
                handle.write(f'{key[0]}: {key[1]}\n')
        return scores

    def stringify_scores(self, db_handle: DatabaseHandle, scores: Dict, src: Source, cutoff=10, fname='scores'):
        conc = ConceptType(src.get_type())
        ret_dict = dict()
        for code in scores:
            if scores[code] > cutoff:
                exec_str = f'''
                            SELECT {conc.get_str()}
                            FROM D_LABITEMS
                            WHERE {conc.get_field()} = {code}'''
                db_handle.cursor.execute(exec_str)
                ret_dict[db_handle.cursor.fetchall()[0][0]] = scores[code]
        scores__ = sorted(ret_dict.items(), key=itemgetter(1), reverse=True)
        if len(scores__) >= 15:
            len__ = 15
        else:
            len__ = len(scores__)
        with open(f'{fname}.json', 'w+') as handle:
            json.dump(scores__[0:len__], handle)
        return ret_dict
