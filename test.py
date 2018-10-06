from time import process_time
from raw_patient_data import ProcessPtData
from concept_util import Source, ConceptType
# from patient_matrix import PatientMatrix

db_ = {'user': 'hiic', 'password': 'greenes2018',
       'db': 'mimic', 'host': 'db01.healthcreek.org'}

processor = ProcessPtData(db_, 20, '')
processor.get_input_data(Source('ICD9'))
start = process_time()
processor.gen_code_univ()
print(process_time() - start)
inp = processor.inp_matrix_creation()
