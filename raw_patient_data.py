from concept_util import *
from patient_from_db import PatientPopulation


class ProcessPtData:
    patients: PatientPopulation = None
    # This is the left hand side of the matrix, what we will use to train/test
    # the machine learning model.
    input_pt_data: Dict[int, List[int]] = dict()
    input_src: Source
    # This is the right hand side of the matrix, tells if a patient has the
    # target medical concept or not.
    result_pt_data: Dict[int, bool] = dict()
    result_src: Source
    # A set of all of the codes that occur in the input_pt_data
    code_universe: List[int] = list()
    # The concept we are collecting data to train for
    target_concept: int = None

    def __init__(self, db, pt_count):
        self.patients = PatientPopulation(**db, pt_count=pt_count)

    def get_input_data(self, src: Source, concept_type: ConceptType):
        pass

    def get_result_data(self, src: Source, concept_type: ConceptType):
        pass

    def gen_code_univ(self):
        '''
        Create the universe of codes based on the current
        patient_concept dictionary in the object.
        '''
        pass

    def occ_threshold(self, cutoff=0.8):
        '''
        Remove codes that occur in less then (len(patient_concept) * cutoff). 
        Enforces that no "rare" conditions are fed to ML model.

        Keyword arguments:
        cutoff -- The ratio of occ we filter at (default = 0.8)
        '''
        pass
