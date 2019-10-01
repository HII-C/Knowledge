
from knowledge.util.database import DatabaseUtil

class FpgrowthDatabaseUtil(DatabaseUtil):
    def get_events(self, max_events):
        limit = f'LIMIT {max_events}' if max_events else ''
        query = f'''
            SELECT HADM_ID, ITEMID
            FROM mimic.CHARTEVENTS
            {limit}
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_support(self):
        query = f'''
            SELECT
                ITEMID,
                COUNT(*) AS ct
            FROM mimic.CHARTEVENTS
            ORDER BY ct DESC
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_admissions(self, min_hadm, max_hadm):
        query = f'''
            SELECT HADM_ID, ITEMID
            FROM mimic.CHARTEVENTS
            WHERE HADM_ID > {min_hadm}
            AND HADM_ID <= {max_hadm}
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()