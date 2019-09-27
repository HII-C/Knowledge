
from knowledge.util.database import DatabaseUtil

class FpgrowthDatabaseUtil(DatabaseUtil):
    def get_items(self):
        query = f'''
            SELECT DISTINCT ITEMID
            FROM mimic.CHARTEVENTS
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()


