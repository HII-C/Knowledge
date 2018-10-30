from typing import List, Tuple
from util.db_util import DatabaseHandle
#import pymysql as sql

class SumRelation:
    rel_db: DatabaseHandle = None
    conc_list: List

    def __init__(self, db_params):
        self.rel_db = DatabaseHandle(**db_params)

    # def __init__(self, user='root', host='localhost', pw_='', db='semmed', table_name="PREDICATION"):
    #     # the connection to the database only has to occur once therefor, it can occur in the initialization
    #     self.user = user
    #     self.host = host
    #     self.pw_ = pw_
    #     self.db = db
    #     self.table_name = table_name
    #     print("not_connected")
    #     self.connection = sql.connect(user=self.user, host=self.host,
    #                             db=self.db, passwd=self.pw_)
    #     self.cursor = self.connection.cursor()
    #     print("connected")

    def get_occurences(self, output_table, n=10000, semmed_db='semmed', output_db='derived'):
        exec_str = f'''DROP TABLE IF EXISTS {output_db}.{output_table}'''
        self.rel_db.cursor.execute(exec_str)
        self.rel_db.connection.commit()
        # self.cursor.execute(exec_str)
        # self.connection.commit()

        exec_str = f'''
                    CREATE TABLE {output_db}.{output_table}(SUBJECT_CUI VARCHAR(9), OBJECT_CUI VARCHAR(9), COUNT INT)
                    AS SELECT pred.SUBJECT_CUI, pred.OBJECT_CUI, COUNT(*) AS COUNT
                    FROM {semmed_db}.PREDICATION AS pred
                    GROUP BY pred.SUBJECT_CUI, pred.OBJECT_CUI limit {n}'''

        self.rel_db.cursor.execute(exec_str)
        self.rel_db.connection.commit()


        # try:
        #     self.cursor.execute(exec_str)
        # except Exception as e:
        #     print(e)
        #
        # self.connection.commit()

#     def main(self):
# 
#         SumRelation.get_occurences(self, output_table="output", n=10, semmed_db="semmed", output_db="derived")
#
# sr = SumRelation()
# if __name__ == "__main__": sr.main()