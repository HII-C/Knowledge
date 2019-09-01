import pickle
import json
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from typing import Dict, List
from datetime import datetime

from models.core.config import Config
from models.util.data_util import Dataset
from models.core.patient_population import PatientPopulation
from models.util.xgb_param_util import XgbParam


class Model:
    config: Config = None
    data: Dataset = None
    train: Dataset = None
    test: Dataset = None
    param: XgbParam = XgbParam()
    model: xgb.Booster = None
    results: Dict = None
    preds: np.array = None

    def __init__(self, config_file):
        self.config = Config()
        self.config.load(config_file)
        self.data = Dataset()
        self.train = Dataset()
        self.test = Dataset()

    def retrieve_patients(self, population=None):
        self.config.get_patients(population)
        print(f'''Retrieved {self.config.patients.patient_count} patients
                with LHS ConceptType = {self.config.params["lefthand_side"]["concept"]},
                RHS ConceptType = {self.config.params["righthand_side"]["concept"]},
                Evaluation = {self.config.params["righthand_side"]["evaluation"]},
                and Logic = {self.config.params["righthand_side"]["logic"]}''')
        self.data.x = self.config.lhs
        self.data.y = self.config.rhs

    def load_patients(self, pickle_base='models/data/patients/static'):
        self.data.x = pd.DataFrame.from_pickle(f'{pickle_base}_x.pickle')
        self.data.y = pd.Series.from_pickle(f'{pickle_base}_y.pickle')

    def dump_patients(self, pickle_base='models/data/patients/static'):
        self.data.x.to_pickle(f'{pickle_base}_x.pickle')
        self.data.y.to_pickle(f'{pickle_base}_y.pickle')

    def split_patients(self, test_size=.5, random_state=42):
        x_train, x_test, y_train, y_test = train_test_split(
            self.data.x, self.data.y, test_size=test_size, random_state=random_state)

        self.train.x = x_train
        self.train.y = y_train
        self.test.x = x_test
        self.test.y = y_test

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
