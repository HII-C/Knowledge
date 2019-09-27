
from knowledge.util.database import DatabaseUtil

class UmlsConceptDatabase(DatabaseUtil):
    
    def fetch_population(self, size):
        query = f'''

        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_concepts(self, concepts=()):
        if len(concepts):
            query = f'''

            '''
        else:
            query = f'''

            '''
        self.cursor.execute(query)
        return self.cursor.fetchall()