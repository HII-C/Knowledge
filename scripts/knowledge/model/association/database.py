
from knowledge.struct.population import Population

class AssociationDatabase(Population):
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


    def fetch_events(self, source, subjects, admissions):
        subquery = {}
        subquery['observations'] = f'''
            SELECT
                lab.HADM_ID,
                CONCAT("O-", item.LOINC_CODE)
            FROM mimiciiiv14.LABEVENTS AS lab
            INNER JOIN mimiciiiv14.D_LABITEMS AS item
            USING(ITEMID)
            WHERE lab.SUBJECT_ID IN {tuple(subjects)}
            AND lab.HADM_ID IN {tuple(admissions)}
            AND item.LOINC_CODE IS NOT NULL '''
        subquery['conditions'] = f'''
            SELECT
                HADM_ID,
                CONCAT("C-", ICD9_CODE)
            FROM mimiciiiv14.DIAGNOSES_ICD
            WHERE SUBJECT_ID IN {tuple(subjects)}
            AND HADM_ID IN {tuple(admissions)} 
            AND ICD9_CODE IS NOT NULL '''
        subquery['treatments'] = f'''
            SELECT
                HADM_ID,
                CONCAT("T-", NDC)
            FROM mimiciiiv14.PRESCRIPTIONS
            WHERE SUBJECT_ID IN {tuple(subjects)}
            AND HADM_ID IN {tuple(admissions)}
            AND NDC IS NOT NULL'''
        subquery = {key: val for key, val in subquery.items() if key in source}
        query = '\nUNION\n'.join(subquery.values())
        query += '\nORDER BY HADM_ID'
        self.cursor.execute(query)
        return self.cursor.fetchall()
    