from enum import Enum
from typing import List, T, Dict


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
            'ICD9': ConceptType.CND, 'SNOMED': ConceptType.CND,
            'LOINC': ConceptType.OBS, 'D_LABITEMS': ConceptType.OBSIID,
            'RxNorm': ConceptType.TRT}
        return type_dict[self.value]
