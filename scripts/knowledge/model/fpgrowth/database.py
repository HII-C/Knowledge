
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


