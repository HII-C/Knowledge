from typing import List, Dict, Tuple
from collections import defaultdict
import numpy as np
from numpy.random import randint, shuffle
import pandas as pd

from models.util.concept_util import ConceptType
from models.util.db_util import DatabaseHandle


class PatientPopulation:
    database: DatabaseHandle = None
    patient_count: int = None
    concept_universe: set = None
    # List of subject id's
    subject_id: List[int] = list()
    rhs: pd.DataFrame = None
    lhs: pd.DataFrame = None

    def __init__(self, db_handle: DatabaseHandle, patient_count=46516):
        self.database = db_handle
        self.patient_count = patient_count
        self.concept_universe = set()

    def random_pid_generation(self, table, n=1000):
        if n > self.patient_count:
            raise ValueError(f'''Maximum patient count
                                    of {self.patient_count}''')
        # This method of random gen is used because
        # mysql random is terribly slow
        id_tup = tuple(randint(0, self.patient_count, n))
        exec_str = f''' SELECT SUBJECT_ID
                        FROM {table}
                        WHERE rand_id
                        IN {id_tup}'''
        self.database.cursor.execute(exec_str)
        self.subject_id = [row[0] for row in self.database.cursor.fetchall()]

    def form_lhs_bin(self, concept: ConceptType):
        raw_lhs = self.database.lhs_bin(self.subject_id, concept)
        # concepts_by_sid = {subject_id: [list of concepts]}
        concept_by_sid = defaultdict(list)
        concepts = list()
        for row in raw_lhs:
            concept_by_sid[row[0]].append(row[1])
            concepts.append(row[1])
        self.concept_universe = set(concepts)
        self.lhs = pd.DataFrame(np.zeros(shape=(self.patient_count,
                                                len(self.concept_universe)),
                                         index=self.subject_id,
                                         columns=self.concept_universe))
        # iterate with value = (subject_id, [list of concepts])
        for value in list(concept_by_sid.items()):
            for code in value[1]:
                self.lhs.at[value[0], code] = 1

    def form_lhs_cont(self, concept: ConceptType):
        raw_lhs = self.database.lhs_cont(self.subject_id, concept)
        # concepts_by_side = {subject_id: [list of concepts]}
        concept_by_sid = defaultdict(list)
        concepts = list()
        for row in raw_lhs:
            concept_by_sid[row[0]].append([row[1], row[2]])
            concepts.append(row[1])
        self.concept_universe = set(concepts)
        # Create a matrix of N x M with values NaN
        self.lhs = pd.DataFrame(np.full(shape=(self.patient_count,
                                               len(self.concept_universe)),
                                        fill_value=np.nan),
                                index=self.subject_id,
                                columns=self.concept_universe)
        # iterate with value = (subject_id, [list of concepts])
        for value in list(concept_by_sid.items()):
            for code in value[1]:
                self.lhs.at[value[0], code] = value[2]

    def form_rhs(self, target_type: ConceptType, target_concept: str):
        ''''''
        self.rhs = pd.Series(np.zeros(self.patient_count),
                             index=self.subject_id)
        rows = self.database.rhs_bin(self.subject_id,
                                     target_type,
                                     target_concept)
        for row in rows:
            self.rhs[row[0]] = 1

    def form_rhs_mult_and(self, target_type: ConceptType,
                          target_concept: List[str]):
        ''''''
        self.rhs = pd.Series(np.zeros(self.patient_count),
                             index=self.subject_id)
        rows = self.database.rhs_bin(self.subject_id,
                                     target_type,
                                     target_concept)
        intermed_dict = defaultdict(0)
        for row in rows:
            intermed_dict[row[0]] += 1
        target_count = len(target_concept)
        for subject_id, count in list(intermed_dict.items()):
            if count == target_count:
                self.rhs[subject_id] = 1

    def form_rhs_mult_or(self, target_type: ConceptType,
                         target_concept: List[str]):
        ''''''
        self.rhs = pd.Series(np.zeros(self.patient_count),
                             index=self.subject_id)
        rows = self.database.rhs_bin(self.subject_id,
                                     target_type,
                                     target_concept)
        for row in rows:
            self.rhs[row[0]] = 1
