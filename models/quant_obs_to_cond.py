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


class QuantObsToCond:
    pt_mtrx: PatientMatrix = None
    xbg_param: XgbParam = XgbParam()
    model: xgb.Booster

    def __init__(self):
        pass

    def train(self, x, y):
        dtrain = xgb.DMatrix(x, y)
        self.model = xgb.train(vars(self.xbg_param), dtrain)
