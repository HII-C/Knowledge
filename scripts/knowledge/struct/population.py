

from knowledge.util.database import DatabaseUtil
from knowledge.util.print import PrintUtil as pr



class Population(DatabaseUtil):
    def __init__(self, database):
        super().__init__(params=database)

        self.mimic = database['mimic_db']
        self.umls = database['umls_db']
        self.rxnorm = database['rxnorm_db']

    
    def fetch_patients(self, size=None, seed=None):
        order = f'ORDER BY RAND({seed})' if seed is not None else ''
        limit = f'LIMIT {size}' if size is not None else ''
        query = f'''
            SELECT
                SUBJECT_ID
            FROM {self.mimic}.PATIENTS
            {order}
            {limit}  '''
        self.cursor.execute(query)
        return self.cursor.fetchall()


    def fetch_admissions(self, patients=None, size=None, seed=None):
        order = f'ORDER BY RAND({seed})' if seed is not None else ''
        limit = f'LIMIT {size}' if size is not None else ''
        cond = f'WHERE SUBJECT_ID IN {tuple(patients)}' if patients is not None else ''
        query = f'''
            SELECT
                SUBJECT_ID,
                HADM_ID
            FROM {self.mimic}.ADMISSIONS
            {cond}
            {order}
            {limit}  '''
        self.cursor.execute(query)
        return self.cursor.fetchall()


    def fetch_prescriptions(self, admissions=None, patients=None, size=None, seed=None):
        order = f'ORDER BY RAND({seed})' if seed is not None else ''
        limit = f'LIMIT {size}' if size is not None else ''
        if patients is not None and admissions is not None:
            cond = f'''
                WHERE SUBJECT_ID IN {tuple(patients)}
                AND HADM_ID IN {tuple(admissions)}  '''
        elif patients is not None:
            cond = f'WHERE SUBJECT_ID IN {tuple(patients)}'
        elif admissions is not None:
            cond = f'WHERE HADM_ID IN {tuple(admissions)}'
        else:
            cond = ''



