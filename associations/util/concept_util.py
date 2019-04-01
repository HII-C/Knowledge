import json
from enum import Enum
from operator import itemgetter
from typing import List, T, Dict

import associations.util.db_util as db_util
#from associations.util.db_util import DatabaseHandle


class ConceptType(Enum):
    CND = 'Condition'
    OBS = 'Observation'
    TRT = 'Treatment'
    OBSIID = 'Labs'

    def get_int(self) -> int:
        int_dict = {
            'Condition': 0,
            'Observation': 1, 'Labs': 1,
            'Treatment': 2
        }
        return int_dict[self.value]

    def get_table(self) -> str:
        table_dict = {'Condition': 'mimic.DIAGNOSES_ICD',
                      'Observation': 'derived.loinc_labevents',
                      'Treatment': 'derived.rxnorm_prescription_min',
                      'Labs': 'mimic.LABEVENTS'}
        return table_dict[self.value]

    def get_field(self) -> str:
        field_dict = {'Condition': 'ICD9_CODE',
                      'Observation': 'LOINC_CODE',
                      'Treatment': 'RXNORM_CODE',
                      'Labs': 'ITEMID'}
        return field_dict[self.value]

    def get_value(self) -> T:
        # Return the fieldname for types with a continious val
        pass

    def get_str(self) -> str:
        str_dict = {'Labs': 'LABEL'}
        return str_dict[self.value]


class Source(Enum):
    '''Enumerated class for representing the various sources patient
    information may come from.'''
    ICD = "ICD9"
    SMD = "SNOMED"
    LNC = "LOINC"
    RXN = "RxNorm"
    OBSIID = "D_LABITEMS"

    def get_type(self) -> ConceptType:
        type_dict = {
            'ICD9': ConceptType.CND,
            'SNOMED': ConceptType.CND,
            'LOINC': ConceptType.OBS,
            'D_LABITEMS': ConceptType.OBSIID,
            'RxNorm': ConceptType.TRT
        }
        return type_dict[self.value]


class OutputFormat:
    db_handle: db_util.DatabaseHandle = None

    def __init__(self, db_handle):
        self.db_handle = db_handle

    def stringify_scores(self, scores: Dict, src: Source, cutoff=10, fname='scores'):
        conc = ConceptType(src.get_type())
        ret_dict = dict()
        for code in scores:
            if scores[code] > cutoff:
                exec_str = f'''SELECT {conc.get_str()}
                                    FROM D_LABITEMS
                                WHERE 
                                    {conc.get_field()} = {code}'''
                self.db_handle.cursor.execute(exec_str)
                ret_dict[self.db_handle.cursor.fetchall()[0][0]] = scores[code]
        sorted_score = sorted(ret_dict.items(),
                              key=itemgetter(1),
                              reverse=True)
        if len(sorted_score) >= 15:
            length = 15
        else:
            length = len(sorted_score)

        with open(f'{fname}.json', 'w+') as handle:
            json.dump(sorted_score[0:length], handle)
        return ret_dict
