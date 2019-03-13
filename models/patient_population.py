from typing import List, Dict, Tuple
from collections import defaultdict
import numpy as np
from numpy.random import randint, shuffle
import pandas as pd

from util.concept_util import ConceptType
from util.db_util import DatabaseHandle


class PatientPopulation:
    database: DatabaseHandle = None
    population_size: int = None
    concept_universe: set = None
    # List of subject id's
    subject_id: List[int] = list()
    rhs: pd.DataFrame = None
    lhs: pd.DataFrame = None

    def __init__(self, db_params, population_size=46516):
        self.database = DatabaseHandle(**db_params)
        self.population_size = population_size
        self.concept_universe = set()

    def random_pid_generation(self, tbl, n=1000) -> List[List[int]]:
        if n > self.population_size:
            raise ValueError(f'''Maximum patient count
                                    of {self.population_size}''')
        # This method of random gen is used because
        exec_str = f''' SELECT SUBJECT_ID
                        FROM {tbl}
                        WHERE rand_id
                            IN
                        {tuple(randint(0, self.population_size, n))}'''
        self.database.cursor.execute(exec_str)
        self.subject_id = [row[0] for row in self.database.cursor.fetchall()]

    def form_lhs_bin(self, concept: ConceptType) -> Dict[int, List[str]]:
        raw_lhs = self.database.subj_lhs_bin(self.subject_id, concept)
        # concepts_by_side = {subject_id: [list of concepts]}
        concept_by_sid = defaultdict(list)
        concepts = list()
        for row in raw_lhs:
            concept_by_sid[row[0]].append(row[1])
            concepts.append(row[1])
        self.concept_universe = set(concepts)
        lhs: pd.DataFrame
        lhs = pd.DataFrame(np.zeros(shape=(self.population_size,
                                           len(self.concept_universe)),
                                    index=self.subject_id,
                                    columns=self.concept_universe))
        # iterate with value = (subject_id, [list of concepts])
        for value in list(concept_by_sid.items()):
            for code in value[1]:
                lhs.at[value[0], code] = 1

    def form_lhs_cont(self, concept: ConceptType) -> Dict[int, List[str]]:
        raw_lhs = self.database.subj_lhs_cont(self.subject_id, concept)
        # concepts_by_side = {subject_id: [list of concepts]}
        concept_by_sid = defaultdict(list)
        concepts = list()
        for row in raw_lhs:
            concept_by_sid[row[0]].append([row[1], row[2]])
            concepts.append(row[1])
        self.concept_universe = set(concepts)
        lhs: pd.DataFrame
        lhs = pd.DataFrame(np.zeros(shape=(self.population_size,
                                           len(self.concept_universe)),
                                    index=self.subject_id,
                                    columns=self.concept_universe))
        # iterate with value = (subject_id, [list of concepts])
        for value in list(concept_by_sid.items()):
            for code in value[1]:
                lhs.at[value[0], code] = value[2]

    def form_rhs_single(self, conc: ConceptType,
                        target_concept: str,
                        print_=False) -> Dict[int, bool]:
        ret_dict = dict()
        if print_:
            pos_count = 0
            neg_count = 0
        for subj_id in self.subject_id:
            neg_count += 1
            cons = self.database.subj_rhs_single(self.subject_id,
                                                 conc,
                                                 target_concept)
            ret_dict[subj_id] = {'meta': {
                code: 0 for code in target_concept}, 'final': 0}

        if print_:
            print(
                f'''There were {pos_count} patients with 
                    the target and {neg_count} without.''')
        return ret_dict

    def form_rhs_mult(self, conc: ConceptType,
                      target_concept: Tuple[str],
                      inclusive=True,
                      print_=False) -> Dict[int, bool]:
        ret_dict = dict()
        if print_:
            pos_count = 0
            neg_count = 0
        for subj_id in self.subject_id:
            neg_count += 1
            if len(target_concept) == 1:
                f_str = f'= \'{target_concept[0]}\''
            else:
                f_str = f'IN {target_concept}'
            exec_str = f'''
                        SELECT {conc.get_field()}
                        FROM {conc.get_table()}
                        WHERE SUBJECT_ID = {subj_id}
                        AND {conc.get_field()} {f_str}'''
            self.database.cursor.execute(exec_str)
            cons = self.database.cursor.fetchall()
            ret_dict[subj_id] = {'meta': {
                code: 0 for code in target_concept}, 'final': 0}

            if inclusive:
                if len(cons) > 0:
                    if print_:
                        neg_count -= 1
                        pos_count += 1
                    ret_dict[subj_id]['final'] = 1
                    for code in cons:
                        ret_dict[subj_id]['meta'][code] = 1
            else:
                if len(cons) == len(target_concept):
                    ret_dict[subj_id]['final'] = 1
                    if print_:
                        pos_count += 1
                elif print_:
                    neg_count -= 1
                for code in cons:
                    ret_dict[subj_id]['meta'][code] = 1
        if print_:
            print(
                f'There were {pos_count} patients with the target and {neg_count} without.')
        return ret_dict
