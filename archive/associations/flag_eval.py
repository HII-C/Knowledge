import xgboost as xgb


from pt_input_creation.patient_matrix import PatientMatrix
from associations.util.xgb_param_util import XgbParam
from associations.util.concept_util import ConceptType, Source
from associations.util.db_util import DatabaseHandle


class flag_boost:
    def __init__(self):
        pt_mtrx: PatientMatrix = None
        xbg_param: XgbParam = XgbParam()
        model: xgb.Booster

    def modified_input(self, inp):
        pass
