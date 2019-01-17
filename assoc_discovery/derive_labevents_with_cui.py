from typing import List, Tuple, Dict
from util.db_util import DatabaseHandle

class DeriveItemIDtoCUI:
    pred_db: DatabaseHandle

    def __init__(self, db_params):
        self.pred_db = DatabaseHandle(**db_params)

    def derive_itemid_to_cui(self, output_db:str = 'derived', output_table: str = 'LabeventsWithCUI', mimic_db:str = 'mimc', input_table:str = 'LABEVENTS', mappings_table:str = 'ItemIdToCUI'):
        exec_str = f'''DROP TABLE IF EXISTS {output_db}.{output_table}'''
        self.pred_db.cursor.execute(exec_str)
        self.pred_db.connection.commit()
        query = f'''
                    CREATE TABLE {output_db}.{output_table} AS 
                    SELECT SUBJECT_ID, HADM_ID, ITEMID, CUI, FLAG
                    FROM {mimic_db}.{input_table}
                    LEFT JOIN {mimic_db}.{mappings_table} ON {mimic_db}.{input_table}.ITEMID = {mimic_db}.{mappings_table}.ITEMID;
                    '''
        #print(query)
        self.pred_db.cursor.execute(query)
        self.pred_db.connection.commit()