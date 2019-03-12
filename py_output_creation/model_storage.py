from typing import List, Dict, Tuple
from util.db_util import DatabaseHandle

class ModelStorage:
    cond_db: DatabaseHandle = None

    def __init__(self, db_params):
        self.cond_db = DatabaseHandle(**db_params)

    def create_database(self, db_name: str = 'knowledge') -> None:
        exec = f'''
                CREATE DATABASE IF NOT EXISTS {db_name} 
                '''
        self.cond_db.cursor.execute(exec)
        self.cond_db.connection.commit()

    def update_storage(
            self, db_name: str = 'knowledge', storage_tbl: str = 'ModelStorage',
            storage_input:List[Tuple[str,str,int,float]] = [['concA','concB',2,3.2]]) -> None:
        # check if the table exists in the first place
        tbl_query = f'''
                    SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{storage_tbl}' 
                    AND TABLE_SCHEMA = '{db_name}'
                    '''
        self.cond_db.cursor.execute(tbl_query)
        target_tables: Tuple[Tuple[str]] = self.cond_db.cursor.fetchall()
        print(tbl_query)
        num_target_tables: int = len(target_tables)

        # if the number of tables is 0 then a table must be created
        if num_target_tables == 0:
            # creating table
            create_table_query: str = f'''
                                CREATE TABLE {db_name}.{storage_tbl} (
                                    Concept1 VARCHAR(9), Concept2 VARCHAR(9),
                                    Predicate tinyint unsigned, Coefficient FLOAT, 
                                    PRIMARY KEY(Concept1, Concept2, Predicate)
                                 )
                                '''
            self.cond_db.cursor.execute(create_table_query)
            self.cond_db.connection.commit()
            print(create_table_query)

            # creating strings for the values to be inputed
            str_values: str = str(storage_input)[1:-1]
            str_values = str_values.replace('[', '\n(').replace(']', ')')[1:]

            # multi-insert query
            insert_query: str = f'''
                        INSERT INTO {db_name}.{storage_tbl}
                        (Concept1, Concept2, Predicate, Coefficent)
                        Values
                        {str_values}
                        '''

            self.cond_db.cursor.execute(insert_query)
            self.cond_db.connection.commit()
            print(insert_query)

        elif num_target_tables == 1:

            # creating strings for the values to be inputed
            str_values: str = str(storage_input)[1:-1]
            str_values = str_values.replace('[', '\n(').replace(']', ')')[1:]

            # inserting via REPLACE
            insert_query: str = f'''
                        REPLACE INTO {db_name}.{storage_tbl}
                        Values
                        {str_values}
                        '''

            self.cond_db.cursor.execute(insert_query)
            self.cond_db.connection.commit()
            print(insert_query)
