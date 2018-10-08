from datetime import datetime

from util.concept_util import Source
from pt_input_creation.process_patients import ProcessPtData
from pt_input_creation.patient_matrix import PatientMatrix
from assoc_discovery.bin_boost import BinaryBoostModel

db_ = {'user': 'hiic', 'password': 'greenes2018',
       'db': 'mimic', 'host': 'db01.healthcreek.org'}
diabetes = tuple(['25000', '25001', '25002'])

total_start = datetime.now()
processor = ProcessPtData(db_, 500, diabetes)
start = datetime.now()
processor.get_causal_data(Source('D_LABITEMS'))
end = datetime.now()
print('Fetching Input Data took ', end - start)

start = datetime.now()
processor.gen_code_univ(__print__=False)
print(list(processor.code_map.values())[0:10])
end = datetime.now()
print('Code generation took ', end - start)

start = datetime.now()
processor.get_result_data(Source('ICD9'), target=diabetes)
end = datetime.now()
print('Result retrieval took ', end - start)

start = datetime.now()
inp = processor.matrix_creation()
end = datetime.now()
print('Matrix Creation took ', end - start)

# start = datetime.now()
# inp.occ_threshold(threshold=.15, __print__=True)
# end = datetime.now()
# print('Occurence Threshold Filtering took ', end - start)


start = datetime.now()
assoc = BinaryBoostModel()
assoc.boost(inp.causal, inp.result)
end = datetime.now()
print('Binary Logistic Boosting modeling took ', end - start)


total_end = datetime.now()
print('Total script took ', total_end - total_start)
