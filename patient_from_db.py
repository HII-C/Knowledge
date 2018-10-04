from numpy.random import randint
from typing import List
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

    def get_rand_pts(self, type_: ConceptType, n=1000) -> List[List[int]]:
        exec_str = f'''select (SUBJECT_ID) where ROW_ID in {tuple([randint(0, POP_N, n)])}'''
        self.pt_db.cursor.execute(exec_str)
        self.pt_id_list = self.pt_db.cursor.fetchall()

    def get_data_for_pts(self, conc: ConceptType):
        ret_dict = {c: defaultdict(list) for c in ConceptType}
        for subj_id in self.pt_id_list:
            exec_str = f'''select {conc.get_field()} from {conc.get_table()}
                            where SUBJECT_ID = {subj_id}'''
            self.pt_db.cursor.execute(exec_str)
            cons = self.pt_db.cursor.fetchall()
            # We get a list of length-1 tuples, so this is converting to list of int
            ret_dict[conc][subj_id] = [con[0] for con in cons]
        return ret_dict
