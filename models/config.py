from typing import Dict, List, T
import json
from getpass import getpass
import pandas as pd
from warnings import warn

from util.concept_util import ConceptType
from util.db_util import DatabaseHandle
from models.patient_population import PatientPopulation


class Config:
    params: Dict[T, T] = None
    database: DatabaseHandle = None
    patients: PatientPopulation = None
    # Left and Right Hand side matrices
    lhs: pd.DataFrame = None
    rhs: pd.Series = None

    def __init__(self):
        pass

    def load(self, filepath):
        with open(filepath, 'r') as infile:
            self.params = json.load(infile)
        self.database_handle(self.params['database'])
        self.patients = PatientPopulation(self.database,
                                          self.params['patient_count'])
        self.lefthand_side(self.params['lefthand_side'])
        self.lhs = self.patients.lhs
        self.rhs = self.patients.rhs

    def database_handle(self, db_params):
        pw = getpass(f'''Password for user={db_params["user"]}
                        on the database={db_params["db"]}
                        located at host={db_params["host"]}:''')
        db_params['password'] = pw
        self.database = DatabaseHandle(**db_params)

    def lefthand_side(self, lhs_params):
        concept = ConceptType(lhs_params['concept'])
        if lhs_params['datatype'] == 'binary':
            self.patients.form_lhs_bin(concept)
        elif lhs_params['datatype'] == 'continuous':
            self.patients.form_lhs_cont(concept)
        else:
            raise ValueError(f'''Check config file.
                    {lhs_params["datatype"]} is not a valid
                    lefthand_side datatype''')

    def righthand_side(self, rhs_params):
        concept = ConceptType(rhs_params['concept'])
        eval_ = rhs_params['evaluation']
        target = rhs_params['target']
        logic = rhs_params['logic']
        if isinstance(target, str):
            if eval_ != 'single' or logic != 'none':
                raise ValueError(f'''Check config file.
                            A single target requires
                            evaluation=single and logic=none.''')
            self.patients.form_rhs(concept, target)
            return

        if len(target) == 1 and eval_ == "single":
            if logic != 'none':
                raise ValueError(f'''Check config file.
                            A single target requires
                            evaluation=single and logic=none.''')
            self.patients.form_rhs(concept, target)
            return

        if len(target) == 1 and eval_ in ('and', 'or'):
            warn(f'''Evaluation={eval_} has no effect with length=1 target''')
            self.patients.form_rhs(concept, target[0])
            return

        if logic == 'and':
            self.patients.form_rhs_mult_and(concept, target)
            return

        elif logic == 'or':
            self.patients.form_rhs_mult_or(concept, target)
            return

        raise ValueError(f'''Check config file. Uncaught invalid config''')
