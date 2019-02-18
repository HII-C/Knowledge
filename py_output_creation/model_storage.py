from typing import List, Dict, Tuple
from util.db_util import DatabaseHandle

class ModelStorage:
    cond_db: DatabaseHandle = None

    def __init__(self, db_params):
        self.cond_db = DatabaseHandle(**db_params)

    def create_database(self, db_name:str = 'knowledge'):
        exec = f'''
                CREATE DATABASE IF NOT EXISTS {db_name} 
                '''
        self.cond_db.cursor.execute(exec)
        self.cond_db.connection.commit()

    def update_storage(self, storage_tbl:str = 'ModelStorage', storage_input:List[List] = []):
        #check if the table exists in the first place
        exec = f'''
                SELECT * FROM sys.tables WHERE name = '{storagle_tbl}'
                '''