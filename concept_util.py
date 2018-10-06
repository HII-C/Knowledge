from enum import Enum
# from dataclasses import dataclass
from typing import List, T, Dict


class ConceptType(Enum):
    CND = 'Condition'
    OBS = 'Observation'
    TRT = 'Treatment'

    def get_int(self) -> int:
        int_dict = {'Condition': 0, 'Observation': 1, 'Treatment': 2}
        return int_dict[self.value]

    def get_table(self) -> str:
        table_dict = {'Condition': 'mimic.DIAGNOSES_ICD',
                      'Observation': 'derived.loinc_labevents',
                      'Treatment': 'derived.rxnorm_prescription_min'}
        return table_dict[self.value]

    def get_field(self) -> str:
        field_dict = {'Condition': 'ICD9_CODE',
                      'Observation': 'LOINC_CODE',
                      'Treatment': 'RXNORM_CODE'}
        return field_dict[self.value]


class Source(Enum):
    '''Enumerated class for representing the various sources patient
    information may come from.'''
    ICD = "ICD9"
    SMD = "SNOMED"
    LNC = "LOINC"
    RXN = "RxNorm"

    def get_type(self) -> ConceptType:
        type_dict = {'ICD9': ConceptType.CND, 'SNOMED': ConceptType.CND,
                     'LOINC': ConceptType.OBS, 'RxNorm': ConceptType.TRT}
        return type_dict[self.value]
