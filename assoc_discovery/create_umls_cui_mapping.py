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

    def create_labevents_UMLS(self, output_table, n=10000, output_db='derived'):
        output_table = "labevents_UMLS"

        exec_str = f'''
                    CREATE TABLE {output_db}.{output_table}(CUI CHAR(8), ROW_ID INT, SUBJECT_ID INT, HADM_ID INT, CHARTTIME DATETIME, VALUE TEXT, VALUENUM FLOAT, VALUEUOM VARCHAR(255), FLAG VARCHAR(255))
                    AS SELECT mimic.ItemIdToCUI.CUI as CUI, mimic.LABEVENTS.ROW_ID as ROW_ID, 
                    mimic.LABEVENTS.SUBJECT_ID as SUBJECT_ID, mimic.LABEVENTS.HADM_ID as HADM_ID, mimic.LABEVENTS.CHARTTIME as CHARTTIME, 
                    mimic.LABEVENTS.VALUE as VALUE, mimic.LABEVENTS.VALUENUM as VALUENUM, mimic.LABEVENTS.VALUEUOM as VALUEUOM, mimic.LABEVENTS.FLAG as FLAG
                    FROM mimic.LABEVENTS INNER JOIN
                    mimic.ItemIdToCUI on mimic.LABEVENTS.ITEMID = mimic.D_LABITEMS.ITEMID limit {n}'''

        self.umls_db.cursor.execute(exec_str)
        self.umls_db.connection.commit()

        # try:
        #     self.cursor.execute(exec_str)
        # except Exception as e:
        #     print(e)

        # self.connection.commit()

    #def create_diagnoses_UMLS(self):


    #def icd9_to_umls_cui(self):

#     def main(self):
#         CreateUMLSCUIMapping.get_occurences(self, output_table="labevents_UMLS", n=10, output_db="derived")
#
# ucm = CreateUMLSCUIMapping()
# if __name__ == "__main__": ucm.main()