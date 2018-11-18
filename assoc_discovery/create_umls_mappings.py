from typing import List, Tuple, Dict
from util.db_util import DatabaseHandle
import MySQLdb as sql

class MappingToUMLS:
    cond_db : DatabaseHandle = None


    def __init__(self, db_params):
        self.cond_db = DatabaseHandle(**db_params)


    def get_code_and_str(self, db_params, tbl: str, encoding: str, str_col : str) -> List[List]:
        self.cond_db = DatabaseHandle(**db_params)
        exec = f'''
                    SELECT {encoding}, {str_col}  FROM {tbl}'''
        self.cond_db.cursor.execute(exec)
        query: List[List] = self.cond_db.cursor.fetchall()
        return query

    #[('derived.d_items', 'LABEL', 'LOINC'),('derived.d_diag', 'SHORT_TITLE', 'ICD9'),('derived.d_proc', 'SHORT_TITLE', 'ICD9')] <- for debug
    def create_table(self, db_params, datab: str, table: str, mimic_tables : List[Tuple[str,str,str]] = [('mimic.D_LABITEMS', 'LABEL', 'LOINC'),('mimic.D_ICD_DIAGNOSES', 'SHORT_TITLE', 'ICD9'),('mimic.D_ICD_PROCEDURES', 'SHORT_TITLE', 'ICD9')]):

        # drop the existing table
        exec = f'''
                DROP TABLE IF EXISTS {datab}.{table};
                '''
        print(exec)
        self.cond_db.cursor.execute(exec)
        self.cond_db.connection.commit()

        mimic_exec = list()
        loinc_spot = 0;
        icd9_spot = 0;
        snomed_spot = 0;
        for x in range(0,len(mimic_tables)):
            temp_str = f'''left join {mimic_tables[x][0]} as t{int(x+3)} on t1.STR = t{int(x+3)}.{mimic_tables[x][1]}
             '''
            if(mimic_tables[x][2] == 'SNOMED' and snomed_spot == 0):
                snomed_spot = x+3
            if(mimic_tables[x][2] == 'LOINC' and loinc_spot == 0):
                loinc_spot = x+3
            elif(mimic_tables[x][2] == 'ICD9' and icd9_spot == 0):
                icd9_spot = x+3

            mimic_exec.append(temp_str)

        mimic_exec_str = ''.join(mimic_exec)
        temp_col_names = f'''(CUI VARCHAR(200), RXCUI VARCHAR(200), LOINC_CODE VARCHAR(200), ICD9_CODE VARCHAR(200), SNOMED_CODE VARCHAR(200))'''

        if(loinc_spot != 0 and icd9_spot != 0 and snomed_spot != 0):
            select_str = f'''DISTINCT CUI, RXCUI, t{loinc_spot}.LOINC_CODE as LOINC_CODE, t{icd9_spot}.ICD9_CODE as ICD9_CODE, t{snomed_spot}.SNOMED_CODE as SNOMED_CODE'''

        elif(loinc_spot != 0 and icd9_spot != 0):
            select_str = f'''DISTINCT CUI, RXCUI, t{loinc_spot}.LOINC_CODE as LOINC_CODE, t{icd9_spot}.ICD9_CODE as ICD9_CODE'''

        elif(loinc_spot != 0 and snomed_spot != 0):
            select_str = f'''DISTINCT CUI, RXCUI, t{loinc_spot}.LOINC_CODE as LOINC_CODE, t{icd9_spot}.ICD9_CODE as ICD9_CODE'''

        elif(snomed_spot != 0 and icd9_spot != 0):
            select_str = f'''DISTINCT CUI, RXCUI, t{snomed_spot}.SNOMED_CODE as SNOMED_CODE, t{icd9_spot}.ICD9_CODE as ICD9_CODE'''

        elif(loinc_spot != 0):
            select_str = f'''DISTINCT CUI, RXCUI, t{icd9_spot}.ICD9_CODE as ICD9_CODE'''

        elif(icd9_spot != 0):
            select_str = f'''DISTINCT CUI, RXCUI, t{loinc_spot}.LOINC_CODE as LOINC_CODE'''

        elif(snomed_spot != 0):
            select_str = f'''DISTINCT CUI, RXCUI, t{snomed_spot}.SNOMED_CODE as SNOMED_CODE'''

        else:
            select_str = f'''DISTINCT CUI, RCUI'''

        # create new table
        exec = f''' 
               CREATE TABLE {datab}.{table} {temp_col_names}
               AS SELECT
               {select_str}
               from derived.mrcon as t1 
               left join derived.rxncon as t2 on t1.STR = t2.STR 
               {mimic_exec_str};
               '''


        print(exec)
        self.cond_db.cursor.execute(exec)
        self.cond_db.connection.commit()

        return



    def main(self):

        self.create_table(self,  datab ='derived', table='tableu')

# param = {'user': 'hiic', 'password': 'greenes2018',
#          'host': 'db01.healthcreek.org', 'db': 'derived'}
#
# cp = MappingToUMLS(param);
# if __name__ == "__main__": cp.main()

param = {'user': 'root', 'password': 'star2222',
         'host': 'localhost', 'db': 'derived'}

cp = MappingToUMLS(param);
if __name__ == "__main__": cp.main()
