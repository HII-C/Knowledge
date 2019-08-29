import pickle
from datetime import datetime
import json
import xgboost as xgb
import numpy as np
from typing import Dict
from models.core.model import Model
from models.util.xgb_param_util import XgbParam


class BinaryBoost(Model):
    param: XgbParam = XgbParam()
    model: xgb.Booster = None
    results: Dict = None
    preds: np.array = None

    def __init__(self, config_file: str):
        super.__init__(config_file)

    def set_params(self, param: Dict = {}, **kwargs):
        for key in param:
            setattr(self.param, key, param[key])
        for key in kwargs:
            setattr(self.param, key, param[key])

    def boost_all(self):
        self.boost_train()
        self.boost_test()
        self.boost_results()

    def boost_train(self):
        dtrain = xgb.DMatrix(self.train.x, self.train.y)
        self.start_time = datetime.now()
        self.model = xgb.train(vars(self.param), dtrain)

    def boost_test(self):
        dtest = xgb.DMatrix(self.test.x, self.test.y)
        self.preds = self.model.predict(dtest)

    def boost_results(self, tol: float = 0.5):
        size = len(self.preds)
        accuracy = sum(1 for i in range(size) if
                       int(self.preds[i] > tol) == self.train.y[i]) / float(size)
        false_neg = sum(1 for i in range(size) if self.train.y[i]
                        and int(self.preds[i] > tol) != self.train.y[i]) / float(size)
        false_pos = 1 - false_neg

        self.results = {
            'accuracy': accuracy,
            'false_neg': false_neg,
            'false_pos': false_pos,
            # Talk to Austin about including concepts/scores
            # 'concepts': [],
            # 'concept_scores': [],
            'train_size': len(self.train.y),
            'test_size': len(self.test.y),
            'time_elapsed': str(datetime.now() - self.start_time),
            'end_time': str(datetime.now()),
        }

    def save_results(self, path: str):
        with open(path, 'w') as writefile:
            json.dump(self.results, writefile)

    def load_model(self, path: str):
        with open(path, 'rb') as infile:
            self.model = pickle.load(infile)

    def save_model(self, path: str):
        with open(path, 'wb+') as outfile:
            pickle.dump(self.model, outfile)
