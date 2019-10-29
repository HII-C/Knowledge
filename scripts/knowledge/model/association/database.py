
from knowledge.util.database import DatabaseUtil

class AssociationDatabase(DatabaseUtil):
    def fetch_population(self, size, seed=None):
        seed = seed if seed is not None else ''
        query = f'''
            SELECT
                SUBJECT_ID,
                HADM_ID
            FROM mimiciiiv14.ADMISSIONS
            ORDER BY RAND({seed})
            LIMIT {size}
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_events(self, subjects, admissions):
        query = f'''
            SELECT
                HADM_ID,
                ICD9_CODE
            FROM mimiciiiv14.DIAGNOSES_ICD
            WHERE SUBJECT_ID IN {tuple(subjects)}
            AND HADM_ID IN {tuple(admissions)}
            ORDER BY HADM_ID
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_support(self, table):
        query = f'''
            SELECT *
            FROM {self.db}.{table}
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()
