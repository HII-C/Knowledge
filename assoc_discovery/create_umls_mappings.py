from typing import List, Tuple, Dict
from util.db_util import DatabaseHandle
import MySQLdb as sql

class MappingToUMLS:
    cond_db : DatabaseHandle = None
    mimic_tables : List[Tuple[str,str,str]] = None


    def __init__(self, db_params):
        self.cond_db = DatabaseHandle(**db_params)
        self.mimic_tables = [('mimic.D_LABITEMS', 'LABEL', 'LOINC'),
                        ('mimic.D_ICD_PROCEDURES', 'SHORT_TITLE', 'ICD9'),
                        ('mimic.D_ICD_DIAGNOSES', 'SHORT_TITLE', 'ICD9')]


    def get_code_and_str(self, db_params, tbl: str, encoding: str, str_col : str) -> List[List]:
        self.cond_db = DatabaseHandle(**db_params)
        exec = f'''
                    SELECT {encoding}, {str_col}  FROM {tbl}'''
        self.cond_db.cursor.execute(exec)
        query: List[List] = self.cond_db.cursor.fetchall()
        return query

    #left outer join on CUI STRs
    def create_table(self, db_params, datab: str, table: str):
        self.cond_db = DatabaseHandle(**db_params)

        # drop the existing table
        exec = f'''
                IF EXISTS(SELECT *
                          FROM {datab}.{table})
                DROP TABLE {datab}.{table}
                '''
        self.cond_db.cursor.execute(exec)
        self.cond_db.connection.commit()

        mimic_exec = list()
        loinc_spot = 0;
        icd9_spot = 0;
        for x in range(0,len(self.mimic_tables)):
            temp_str = f'''left join {self.mimic_tables[x][0]} as t{int(x+3)} on t1.STR = t{int(x+3)}.{self.mimic_tables[x][1]}
             '''
            if(self.mimic_tables[x][2] == 'LOINC' and loinc_spot == 0):
                loinc_spot = x+3
            elif(self.mimic_tables[x][2] == 'ICD9' and icd9_spot == 0):
                icd9_spot = x+3

            mimic_exec.append(temp_str)

        mimic_exec_str = ''.join(mimic_exec)

        if(loinc_spot != 0 and icd9_spot != 0):
            select_str = f'''DISTINCT CUI, RXCUI, t{loinc_spot}.LOINC_CODE, t{icd9_spot}.ICD9_CODE'''

        elif(loinc_spot == 0):
            select_str = f'''DISTINCT CUI, RXCUI, t{icd9_spot}.ICD9_CODE'''

        elif(icd9_spot == 0):
            select_str = f'''DISTINCT CUI, RXCUI, t{loinc_spot}.LOINC_CODE'''

        else:
            select_str = f'''DISTINCT CUI, RXCUI'''

        # create new table
        exec = f''' 
               CREATE TABLE {datab}.{table}
               AS SELECT
               {select_str}
               from umls.MRCONSO as t1 
               left join rxnorm.RXNCONSO as t2 on t1.STR = t2.STR 
               {mimic_exec_str};
               '''

        print(exec)
        self.cond_db.cursor.execute(exec)
        self.cond_db.connection.commit()

        return



def main(self):

    param = {'user': 'root', 'password': 'star2222',
             'host': 'localhost', 'db': 'derived'}

    mod_out = MappingToUMLS(param)

    mod_out.create_table(self, 'derived', 'tableu')




