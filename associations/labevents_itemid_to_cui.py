from typing import List, Tuple
from associations.util.db_util import DatabaseHandle


class LabeventConversion:
    know_db: DatabaseHandle = None

    def __init__(self, db_params):
        self.know_db = DatabaseHandle(**db_params)

    def create_labevents_UMLS(self, output_table: str = 'LABEVENTS_umls',
                              n: int = 10000,
                              output_db: str = 'knowledge',
                              mimic_db: str = 'mimic',
                              input_table: str = 'LABEVENTS',
                              itemid_table: str = 'D_LABITEMS',
                              umls_db: str = 'umls',
                              umls_table: str = 'MRCONSO',
                              printout=False):

        exec_str = f''' CREATE TABLE {output_db}.{output_table}
                        AS SELECT DISTINCT
                            SUBJECT_ID, HADM_ID, CUI, CHARTTIME, VALUE, VALUENUM, VALUEUOM, FLAG
                        FROM {mimic_db}.{input_table}
                            LEFT JOIN {mimic_db}.{itemid_table}
                                ON 
                            {mimic_db}.{input_table}.ITEMID = {mimic_db}.{itemid_table}.ITEMID
                            LEFT JOIN {umls_db}.{umls_table}
                                ON 
                            {mimic_db}.{itemid_table}.LOINC_CODE = {umls_db}.{umls_table}.CODE 
                        WHERE {mimic_db}.{input_table}.HADM_ID IS NOT NULL
                        limit {n}
                    '''
        if printout:
            print(exec_str)

        self.know_db.cursor.execute(exec_str)
        self.know_db.connection.commit()

    def create_labevents_UMLS_all(self, output_table: str = 'LABEVENTS_umls',
                              output_db: str = 'knowledge',
                              mimic_db: str = 'mimic',
                              input_table: str = 'LABEVENTS',
                              itemid_table: str = 'D_LABITEMS',
                              umls_db: str = 'umls',
                              umls_table: str = 'MRCONSO',
                              printout=False):

        exec_str = f''' CREATE TABLE {output_db}.{output_table}
                        AS SELECT DISTINCT
                            SUBJECT_ID, HADM_ID, CUI, CHARTTIME, VALUE, VALUENUM, VALUEUOM, FLAG
                        FROM {mimic_db}.{input_table}
                            LEFT JOIN {mimic_db}.{itemid_table}
                                ON 
                            {mimic_db}.{input_table}.ITEMID = {mimic_db}.{itemid_table}.ITEMID
                            LEFT JOIN {umls_db}.{umls_table}
                                ON 
                            {mimic_db}.{itemid_table}.LOINC_CODE = {umls_db}.{umls_table}.CODE 
                        WHERE {mimic_db}.{input_table}.HADM_ID IS NOT NULL
                    '''
        if printout:
            print(exec_str)

        self.know_db.cursor.execute(exec_str)
        self.know_db.connection.commit()

