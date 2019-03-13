from datetime import datetime
from getpass import getpass

from util.concept_util import Source, OutputFormat
from pt_input_creation.process_patients import ProcessPtData
from pt_input_creation.patient_matrix import PatientMatrix
from assoc_discovery.bin_boost import BinaryBoostModel

user = 'hiic'
password = getpass(f'Password for {user}')
db_ = {'user': user, 'password': password,
       'db': 'mimic', 'host': 'db01.healthcreek.org'}
diabetes = tuple(['25000'])

total_start = datetime.now()
processor = ProcessPtData(db_, 10000, diabetes)
print(f'Fetching {processor.pt_count} patients.')

start = datetime.now()
processor.get_causal_data(Source('D_LABITEMS'))
end = datetime.now()
print('Fetching Input Data took ', end - start)

start = datetime.now()
processor.gen_code_univ(__print__=False)
end = datetime.now()
print('Code generation took ', end - start)

start = datetime.now()
processor.get_result_data(Source('ICD9'), __print__=True)
end = datetime.now()
print('Result retrieval took ', end - start)

start = datetime.now()
inp = processor.matrix_creation()
end = datetime.now()
print('Matrix Creation took ', end - start)

start = datetime.now()
# inp.occ_threshold(threshold=.10, __print__=True)
end = datetime.now()
print('Occurence Threshold Filtering took ', end - start)


start = datetime.now()
assoc = BinaryBoostModel()
assoc.boost(inp.causal, inp.result)
end = datetime.now()
print('Binary Logistic Boosting modeling took ', end - start)


scores = assoc.concept_by_importance()
out = OutputFormat(db_handle=processor.patients.pt_db)
out.stringify_scores(scores=scores, src=Source('D_LABITEMS'), cutoff=10)
assoc.write_params('params.json')
total_end = datetime.now()
print('Total script took ', total_end - total_start)
