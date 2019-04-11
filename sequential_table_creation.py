from util.db_util import DatabaseHandle
from util.concept_util import ConceptType

from getpass import getpass

import pandas as pd
import numpy as np

class SequentialTableCreation:
    def __init__(self, db_paramas):
        if db_params is None:
            db_params = {
                'user': 'root',
                'db': 'knowledge',
                'host': 'db01.healthcreek.org',
                'password': getpass('SQL Password:')
            }
        db = DatabaseHandle(db_params)

    def create_admissions(self):
        ''' Create new admissions table with new SEQ_NUM property which
            provides the order of the HADM_IDs for each SUBJECT_ID.'''

        query = f'''
            set @seq = 0;
            set @subj = 0;

            SELECT  SUBJECT_ID,
                    HADM_ID,
                    SEQ_NUM
            INTO    admissions_seq
            FROM (
                SELECT  SUBJECT_ID,
                        HADM_ID,
                        @seq := IF(@subj = SUBJECT_ID, @seq+1, 0) AS SEQ_NUM,
                        @subj := SUBJECT_ID
                FROM (
                    SELECT  SUBJECT_ID,
                            HADM_ID,
                            ADMITTIME
                    FROM    mimic.ADMISSIONS
                    ORDER BY SUBJECT_ID, ADMITTIME
                ) AS ORDERED
            ) AS SEQUENCED;
        '''

        self.db.cursor.execute(query)
        self.db.connection.commit()
    
    def create_concept(self, concept: ConceptType, table_name: str):
        ''' Create new metadata to easily access sequential occurence of
            events for any concept type in our database.'''

        # Note: expressions for UMLS table info empty
        query = f'''
            SELECT  *
            INTO knowledge.{table_name}
            FROM (
                SELECT  admissions_seq.SUBJECT_ID,
                        admissions_seq.HADM_ID,
                        admissions_seq.SEQ_NUM,
                        {concept.get_table()}.{concept.get_field()} AS ORIGIN_CODE,
                        {}.{} AS UMLS_CODE,
                        {concept.get_table()}.{concept.get_value()} AS VALUE,
                FROM {concept.get_table()}
                LEFT JOIN admissions_seq
                ON {concept.get_table()}.HADM_ID = admissions_seq.HADM_ID
                LEFT JOIN {concept.get_table()}
                ON {}.{} = {concept.get_table()}.{concept.get_field()}
            ) AS TEMP;
        '''

        self.db.cursor.execute(query)
        self.db.connection.commit()