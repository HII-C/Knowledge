from util.db_util import DatabaseHandle
#import pymysql as sql

class CreateUMLSCUIMapping:
    umls_db: DatabaseHandle = None

    def __init__(self, db_params):
        self.umls_db = DatabaseHandle(**db_params)

    # def __init__(self, user='root', host='localhost', pw_='', db='mimic', table_name="LABEVENTS"):
    #      # the connection to the database only has to occur once therefor, it can occur in the initialization
    #      self.user = user
    #      self.host = host
    #      self.pw_ = pw_
    #      self.db = db
    #      self.table_name = table_name
    #      print("not_connected")
    #      self.connection = sql.connect(user=self.user, host=self.host,
    #                              db=self.db, passwd=self.pw_)
    #      self.cursor = self.connection.cursor()
    #      print("connected")

    def create_labevents_UMLS(
            self, output_table: str = 'labevents_UMLS', n: int =10000, output_db: str='derived',
            mimic_db: str= 'mimic', input_table: str = 'LABEVENTS', mappings_table: str = 'ItemIdToCUI'):

        #deletes the output table (if it exists)
        drop_output_query = f'''
                            DROP TABLE IF EXISTS {output_db}.{output_table}
                            '''
        self.umls_db.cursor.execute(drop_output_query)
        self.umls_db.connection.commit()
        print(drop_output_query)

        #deletes the mapping table (if it exists)
        drop_mappings_query = f'''
                              DROP TABLE IF EXISTS {output_db}.{mappings_table}
                              '''
        self.umls_db.cursor.execute(drop_mappings_query)
        self.umls_db.connection.commit()
        print(drop_mappings_query)

        #creates a new mapping table
        create_mappings_table = f'''
                                CREATE TABLE {output_db}.{mappings_table} AS
                                SELECT DISTINCT ITEMID, CUI FROM {mimic_db}.{mappings_table}
                                '''
        self.umls_db.cursor.execute(create_mappings_table)
        self.umls_db.connection.commit()
        print(create_mappings_table)

        #makes the ItemId the primary key
        alter_mappings_pk = f'''
                            ALTER TABLE {output_db}.{mappings_table}
                            ADD PRIMARY KEY (ITEMID)
                            '''
        self.umls_db.cursor.execute(alter_mappings_pk)
        self.umls_db.connection.commit()
        print(alter_mappings_pk)

        #creates a new output table where ITEMID is replaced by the CUI encoding
        exec_str = f'''
                    CREATE TABLE {output_db}.{output_table} AS 
                    SELECT SUBJECT_ID, HADM_ID, CUI, FLAG
                    FROM {mimic_db}.{input_table}
                    LEFT JOIN {output_db}.{mappings_table}
                    ON {mimic_db}.{input_table}.ITEMID = {output_db}.{mappings_table}.ITEMID limit {n}
                    '''

        self.umls_db.cursor.execute(exec_str)
        self.umls_db.connection.commit()
        print(exec_str)

        # try:
        #     self.cursor.execute(exec_str)
        # except Exception as e:
        #     print(e)

        # self.connection.commit()

    def create_labevents_UMLS_with_ITEMID(
            self, output_table: str = 'labevents_UMLS_ITEMID', n: int =10000, output_db: str='derived',
            mimic_db: str= 'mimic', input_table: str = 'LABEVENTS', mappings_table: str = 'ItemIdToCUI'):

        #deletes the output table (if it exists)
        drop_output_query = f'''
                            DROP TABLE IF EXISTS {output_db}.{output_table}
                            '''
        self.umls_db.cursor.execute(drop_output_query)
        self.umls_db.connection.commit()
        print(drop_output_query)

        #deletes the mapping table (if it exists)
        drop_mappings_query = f'''
                              DROP TABLE IF EXISTS {output_db}.{mappings_table}
                              '''
        self.umls_db.cursor.execute(drop_mappings_query)
        self.umls_db.connection.commit()
        print(drop_mappings_query)

        #creates a new mapping table
        create_mappings_table = f'''
                                CREATE TABLE {output_db}.{mappings_table} AS
                                SELECT DISTINCT ITEMID, CUI FROM {mimic_db}.{mappings_table}
                                '''
        self.umls_db.cursor.execute(create_mappings_table)
        self.umls_db.connection.commit()
        print(create_mappings_table)

        #makes the ItemId the primary key
        alter_mappings_pk = f'''
                            ALTER TABLE {output_db}.{mappings_table}
                            ADD PRIMARY KEY (ITEMID)
                            '''
        self.umls_db.cursor.execute(alter_mappings_pk)
        self.umls_db.connection.commit()
        print(alter_mappings_pk)

        #creates a new output table where ITEMID is replaced by the CUI encoding
        exec_str = f'''
                    CREATE TABLE {output_db}.{output_table} AS 
                    SELECT SUBJECT_ID, HADM_ID, CUI, {mimic_db}.{input_table}.ITEMID, FLAG
                    FROM {mimic_db}.{input_table}
                    LEFT JOIN {output_db}.{mappings_table}
                    ON {mimic_db}.{input_table}.ITEMID = {output_db}.{mappings_table}.ITEMID limit {n}
                    '''

        self.umls_db.cursor.execute(exec_str)
        self.umls_db.connection.commit()
        print(exec_str)

        # try:
        #     self.cursor.execute(exec_str)
        # except Exception as e:
        #     print(e)

        # self.connection.commit()

    def diagnoses_ICD_to_CUI(self, output_table, n=10000, output_db='derived'):
        temp_table = "ICDTOCUI"

        exec_str = f'''
                    CREATE TABLE {output_db}.{temp_table} (CUI CHAR(8), AUI VARCHAR(9), SAB VARCHAR(40), ICD9_CODE VARCHAR(255)) 
                    AS SELECT umls.MRCONSO.CUI as CUI, umls.MRCONSO.AUI as AUI, umls.MRCONSO.SAB as SAB, mimic.D_ICD_DIAGNOSES.ICD9_CODE as ICD9_CODE
                    FROM umls.MRCONSO INNER JOIN
                    mimic.D_ICD_DIAGNOSES ON umls.MRCONSO.STR = mimic.D_ICD_DIAGNOSES.SHORT_TITLE limit {n}'''

        output_table = "diagnoses_UMLS"
        exec_str = f'''
                    CREATE TABLE {output_db}.{output_table} (CUI CHAR(8), ROW_ID INT, SUBJECT_ID INT, HADM_ID INT, SEQ_NUM INT)
                    AS SELECT derived.ICDTOCUI.CUI as CUI, mimic.DIAGNOSES_ICD.ROW_ID as ROW_ID, 
                    mimic.DIAGNOSES_ICD.SUBJECT_ID as SUBJECT_ID, mimic.DIAGNOSES_ICD.HADM_ID as HADM_ID, mimic.DIAGNOSES_ICD.SEQ_NUM as SEQ_NUM 
                    FROM mimic.DIAGNOSES_ICD INNER JOIN
                    derived.ICDTOCUI on mimic.DIAGNOSES_ICD.ICD9_CODE = derived.ICDTOCUI.ICD9_CODE limit {n}'''

    def create_diagnoses_UMLS(self, output_table, n=10000, output_db='derived'):
        output_table = "diagnoses_UMLS"

        exec_str =  f'''
                    CREATE TABLE {output_db}.{output_table}(CUI CHAR(8), ROW_ID INT, SUBJECT_ID INT, HADM_ID INT, CHARTTIME DATETIME, VALUE TEXT, VALUENUM FLOAT, VALUEUOM VARCHAR(255), FLAG VARCHAR(255))
                    AS SELECT mimic.ItemIdToCUI.CUI as CUI, mimic.LABEVENTS.ROW_ID as ROW_ID, 
                    mimic.LABEVENTS.SUBJECT_ID as SUBJECT_ID, mimic.LABEVENTS.HADM_ID as HADM_ID, mimic.LABEVENTS.CHARTTIME as CHARTTIME, 
                    mimic.LABEVENTS.VALUE as VALUE, mimic.LABEVENTS.VALUENUM as VALUENUM, mimic.LABEVENTS.VALUEUOM as VALUEUOM, mimic.LABEVENTS.FLAG as FLAG
                    FROM mimic.LABEVENTS INNER JOIN
                    mimic.ItemIdToCUI ON mimic.LABEVENTS.ITEMID = mimic.ItemIdToCUI.ITEMID limit {n}'''
