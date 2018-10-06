from collections import defaultdict
import numpy as np
from bidict import bidict


from concept_util import *
from patient_from_db import PatientPopulation
from patient_matrix import PatientMatrix


class ProcessPtData:
    # Object holding the instance of random patient ID's being used
    patients: PatientPopulation = None
    # Number of patients to retrieve and collect data for
    pt_count: int = 0
    # The concept we are collecting data to train for
    target_concept: str = None
    # This is the "left hand side" of the matrix, the input for the model
    input_pt_data: Dict[int, List[str]] = dict()
    input_src: Source
    # This is the "right hand side" of the matrix, the result of the model
    result_pt_data: Dict[int, bool] = dict()
    result_src: Source
    # A set of all of the codes that occur in the input_pt_data
    code_universe: List[str] = list()
    # Bidirectional dict (1-1 map); read about: https://pypi.org/project/bidict/
    # This is mapping [code (type=str): int_rep_of_code (for simplification in ML model)]
    code_map: bidict = bidict(dict())

    def __init__(self, db, pt_count, target, rnd_pt_tbl='derived.patients_as_index'):
        self.target_concept = target
        self.pt_count = pt_count
        self.patients = PatientPopulation(db)
        self.patients.get_rand_pts(rnd_pt_tbl, n=self.pt_count)

    def get_input_data(self, src: Source):
        self.input_src = src
        self.input_pt_data = self.patients.get_input_for_pts(src.get_type())

    def get_result_data(self, src: Source):
        self.result_src = src
        self.result_pt_data = self.patients.get_results_for_pts(
            src.get_type(), self.target_concept)

    def gen_code_univ(self, __print__=True):
        ''' Create the universe of codes based on the current
        patient_concept dictionary in the object. '''
        map_count = 0
        for pt_codes in self.input_pt_data.values():
            for code in pt_codes:
                if not self.code_map.get(code):
                    map_count += 1
                    self.code_map[code] = map_count
        self.code_universe = list(self.code_map.keys())
        if __print__:
            print(f'There are {map_count} codes in the current universe')

    def inp_matrix_creation(self) -> PatientMatrix:
        full_pt_dict = defaultdict(list)
        for pt in self.input_pt_data:
            for code in self.code_universe:
                if code in self.input_pt_data[pt]:
                    full_pt_dict[pt].append(1)
                else:
                    full_pt_dict[pt].append(0)

        args = {'columns': self.code_universe, 'index': full_pt_dict.keys()}

        return PatientMatrix(full_pt_dict, args)
