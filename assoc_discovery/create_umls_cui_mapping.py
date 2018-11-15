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

    def create_temp_loinc(self, output_table, n=10000, output_db='derived'):

        exec_str = f'''
                    CREATE TABLE {output_db}.{output_table}(LOINC_CODE VARCHAR(255))
                    AS SELECT mimic.D_LABITEMS.LOINC_CODE
                    FROM mimic.LABEVENTS INNER JOIN
                    mimic.D_LABITEMS on mimic.LABEVENTS.ITEMID = mimic.D_LABITEMS.ITEMID limit {n}'''

        self.rel_db.cursor.execute(exec_str)
        self.rel_db.connection.commit()

        # try:
        #     self.cursor.execute(exec_str)
        # except Exception as e:
        #     print(e)

        # self.connection.commit()

    #def item_id_to_umls_cui(self):


    #def icd9_to_umls_cui(self):

#     def main(self):
#         CreateUMLSCUIMapping.get_occurences(self, output_table="output", n=10, semmed_db="semmed", output_db="derived")
#
# sr = SumRelation()
# if __name__ == "__main__": sr.main()