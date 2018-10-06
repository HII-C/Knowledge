from numpy.random import randint, shuffle
from typing import List, Dict
from collections import defaultdict
from concept_util import ConceptType
from db_util import *

# This is the # of patients in the mimic DB
POP_N = 46516


class PatientPopulation:
    pt_db: DatabaseHandle = None
    pt_id_list: List[int]

    def __init__(self, db_params):
        self.pt_db = DatabaseHandle(**db_params)

    def get_rand_pts(self, tbl, n=1000) -> List[List[int]]:
        tmp_ = list(range(POP_N))
        shuffle(tmp_)
        tmp_ = tmp_[0:n]
        # This method of random gen is used because
        exec_str = f'''
                        SELECT SUBJECT_ID
                        FROM {tbl}
                        WHERE rand_id IN {tuple(tmp_)}
                        LIMIT {n}'''
        self.pt_db.cursor.execute(exec_str)
        self.pt_id_list = [row[0] for row in self.pt_db.cursor.fetchall()]

    def get_ratio_pos_neg_rand_pts(self, tbl, ratio: float, n=1000):
        gen_ = [[1, (float(n)*ratio), 'pos'],
                [0, float(n)*(1.0 - ratio), 'neg']]
        final_set = list()
        for sw_ in gen_:
            exec_str = f'''
                        SELECT SUBJECT_ID
                        FROM {tbl}
                        WHERE HAS_TARGET = {sw_[0]}'''
            self.pt_db.cursor.execute(exec_str)
            rows = [row[0] for row in self.pt_db.cursor.fetchall()]
            # If we don't have enough patients to support the ratio of pos-neg we want
            if len(rows) < sw_[1]:
                __ = {'pos': 'decrease', 'neg': 'increase'}
                raise ValueError(f'Unable to find {sw_[1]} {sw_[2]} patients.' +
                                 f'Please {__[sw_[2]]} ratio.')
            shuffle(rows)
            final_set.extend(rows[0:int(sw_[1])])

    def get_input_for_pts(self, conc: ConceptType) -> Dict[int, List[str]]:
        ret_dict = dict()
        for subj_id in self.pt_id_list:
            exec_str = f'''select {conc.get_field()} from {conc.get_table()}
                            where SUBJECT_ID = {subj_id}'''
            self.pt_db.cursor.execute(exec_str)
            cons = self.pt_db.cursor.fetchall()
            # We get a list of length-1 tuples, so this is converting to list of int
            ret_dict[subj_id] = [con[0] for con in cons if con[0] is not None]
        return ret_dict

    def get_results_for_pts(self, conc: ConceptType, target_concept: str) -> Dict[int, bool]:
        ret_dict = dict()
        for subj_id in self.pt_id_list:
            exec_str = f'''select {conc.get_field()} from {conc.get_table()}
                            where
                                SUBJECT_ID = {subj_id} 
                            and
                                {conc.get_field()} = {target_concept}'''
            self.pt_db.cursor.execute(exec_str)
            cons = self.pt_db.cursor.fetchall()
            ret_dict[subj_id] = bool(cons)
        return ret_dict
