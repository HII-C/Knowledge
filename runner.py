from datetime import datetime

from pt_input_creation.process_patients import ProcessPtData
from pt_input_creation.patient_matrix import PatientMatrix
from util.concept_util import Source

db_ = {'user': 'hiic', 'password': 'greenes2018',
       'db': 'mimic', 'host': 'db01.healthcreek.org'}


total_start = datetime.now()
processor = ProcessPtData(db_, 10000, '')
start = datetime.now()
processor.get_input_data(Source('ICD9'))
end = datetime.now()
print('Fetching Input Data took ', end - start)

start = datetime.now()
processor.gen_code_univ(__print__=False)
print(list(processor.code_map.values())[0:10])
end = datetime.now()
print('Code generation took ', end - start)

start = datetime.now()
inp = processor.inp_matrix_creation()
end = datetime.now()
print('Matrix Creation took ', end - start)

start = datetime.now()
inp.occ_threshold(threshold=.15, __print__=True)
end = datetime.now()
print('Occurence Threshold Filtering took ', end - start)

total_end = datetime.now()
print('Total script took ', total_end - total_start)
