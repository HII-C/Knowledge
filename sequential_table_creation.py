from models.util.db_util import DatabaseHandle
from models.util.concept_util import ConceptType

from getpass import getpass

import pandas as pd
import numpy as np

class SequentialTableCreation:
    def __init__(self, db_params = None):
        if db_params is None:
            db_params = {
                'user': 'root',
                'db': 'knowledge',
                'host': 'db01.healthcreek.org',
                'password': getpass('SQL Password:')
            }
        self.db = DatabaseHandle(db_params)

    def create_admissions(self):
        # Create new admissions table with new SEQ_NUM property which
        # provides the order of the HADM_IDs for each SUBJECT_ID.

        query = f'''
            CREATE TABLE knowledge.admissions_seq
            AS 
                SELECT
                    ADM1.SUBJECT_ID,
                    ADM1.HADM_ID,
                    ADM1.ADMITTIME,
                    COUNT(*) - 1 AS `SEQ`
                FROM mimic.ADMISSIONS AS ADM1
                    LEFT JOIN mimic.ADMISSIONS AS ADM2
                    ON ADM1.SUBJECT_ID = ADM2.SUBJECT_ID
                    AND ADM1.ADMITTIME >= ADM2.ADMITTIME
                GROUP BY
                    ADM1.SUBJECT_ID,
                    ADM1.HADM_ID
                ORDER BY
                    SUBJECT_ID,
                    SEQ;            
        '''

        self.db.cursor.execute(query)
        self.db.connection.commit()
    
    def create_concept(self, concept: ConceptType, table_name: str):
        # Create new metadata to easily access sequential occurence of
        # events for any concept type in our database
        
        query = f'''
            CREATE TABLE knowledge.{table_name}
            AS
                SELECT  admissions_seq.SUBJECT_ID,
                        admissions_seq.HADM_ID,
                        admissions_seq.SEQ_NUM,
                        {concept.get_table()}.{concept.get_field()} AS {concept.get_field()}
                        {concept.get_table()}.{concept.get_value()} AS VALUE,
                FROM {concept.get_table()}
                LEFT JOIN admissions_seq
                ON {concept.get_table()}.HADM_ID = admissions_seq.HADM_ID
        '''

        self.db.cursor.execute(query)
        self.db.connection.commit()