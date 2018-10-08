from collections import defaultdict
from typing import List, Dict, Tuple
import numpy as np


from util.concept_util import ConceptType, Source
from .patients_from_db import PatientPopulation
from .patient_matrix import PatientMatrix


class ProcessPtData:
    # Object holding the instance of random patient ID's being used
    patients: PatientPopulation = None
    # Number of patients to retrieve and collect data for
    pt_count: int = 0
    # The concept we are collecting data to train for
    target: Tuple[str] = None
    # This is the "left hand side" of the matrix, the input for the model
    causal_data: Dict[int, List[str]] = dict()
    causal_src: Source
    # This is the "right hand side" of the matrix, the result of the model
    result_data: Dict[int, Dict] = dict()
    result_src: Source
    # A set of all of the codes that occur in the causal_pt_data
    code_universe: List[str] = list()
    # Mapping [code: index in universe], for simplification in matrix gen
    code_map: Dict[str, int] = dict()

    def __init__(self, db, pt_count, target, rnd_pt_tbl='derived.patients_as_index'):
        self.target = target
        self.pt_count = pt_count
        self.patients = PatientPopulation(db)
        self.patients.get_rand(rnd_pt_tbl, n=self.pt_count)

    def get_causal_data(self, src: Source):
        self.causal_src = src
        self.causal_data = self.patients.get_causal(src.get_type())

    def get_result_data(self, src: Source, target=None):
        if target is not None:
            self.target = target
        self.result_src = src
        self.result_data = self.patients.get_result(
            src.get_type(), self.target)

    def gen_code_univ(self, __print__=True):
        ''' Create the universe of codes based on the current
        patient_concept dictionary in the object. '''
        map_count = 0
        tmp_cm = dict()
        for pt_codes in self.causal_data.values():
            for code in pt_codes:
                if code not in tmp_cm and code is not None:
                    tmp_cm[code] = map_count
                    map_count += 1
        self.code_map = {k: v for (k, v) in tmp_cm.items()}
        self.code_universe = self.code_map.keys()

        if __print__:
            print(f'There are {map_count} codes in the current universe')

    def matrix_creation(self) -> PatientMatrix:
        causal_dict = defaultdict(list)
        for pt in self.causal_data:
            causal_dict[pt] = [0]*len(self.code_universe)
            for code in self.causal_data[pt]:
                causal_dict[pt][self.code_map[code]] = 1

        result_list = [self.result_data[pt]['final'] for pt in causal_dict]
        result_meta = {pt: self.result_data[pt]['meta'] for pt in causal_dict}

        args = {'columns': self.code_universe, 'index': causal_dict.keys()}

        return PatientMatrix(causal_dict, result_list, result_meta, args)
