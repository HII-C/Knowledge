from dataclasses import dataclass
import json


@dataclass
class XgbParam:
    silent = 1
    # https://xgboost.readthedocs.io/en/latest/parameter.html#general-parameters
    objective = 'binary:logistic'
    booster = 'gbtree'
    # Increased eta -> less overfitting -> more conservative boosting. range: [0, 1]
    eta = .3
    # Minimum loss reduction. The larger gamma the more conservative. range: [0, INF]
    gamma = 0
    # Tree depth. Inc -> more complex model -> more overfitting. range: [1: INF]
    max_depth = 6
    # check link. range: [0, INF]
    min_child_weight = 1
    # check link. range: [0, INF]
    max_delta_step = 0
    # subsample ratio. Set to .5 -> 1/2 data used, randomly. range: (0, 1]
    subsample = 1
    # subsample of cols each boost iter. range (0, 1]
    colsample_bytree = 1
    # subsample of cols in EACH LEVEL, every time a split is made. (0, 1]
    colsample_byleve = 1
    # L2 regularization, increasing -> more conservative.
    reg_lambda = 1
    # L1 regularization, increasing -> more conservative.
    reg_alpha = 0
