from typing import List, Dict, Tuple
from collections import defaultdict
from util.db_util import DatabaseHandle
import pymysql as sql



class ModelOutput:
    cond_db: DatabaseHandle = None

    def __init__(self):
        self.user = "root"
        self.pw_ = "star2222"
        self.db = "derived"
        self.conn = sql.connect(user=self.user,
                                db=self.db, passwd=self.pw_)
        self.cursor = self.conn.cursor()


    #create new table called ModelOutput
        #order it by accuracy

   # def row_to_tuple(self): ????
    def ordered_insert(self, insert_data: Tuple[Tuple[str, str, int],...]):
        print("hi")
        #if no table named model output, need to make a new table called model output
        exec = """
                SHOW TABLES """
        self.cursor.execute(exec)
        tbls = self.cursor.fetchall()

        if any(("model_output") in row for row in tbls):
            #table already exists
            #check to see if new f_importance is higher than the old one
            print("table already exists")

            exec = """ SELECT f_importance 
            FROM model_output LIMIT 1"""
            self.cursor.execute(exec)
            tmp_f_im = self.cursor.fetchall()
            print(tmp_f_im)
            print(insert_data)
            print(insert_data[0][2])

            if tmp_f_im[0][0] < insert_data[0][2]:
                exec = """ DROP TABLE model_output"""
                self.cursor.execute(exec)

                # create new table with input data
                exec = """ CREATE TABLE model_output (
                                    concept1 VARCHAR(20), concept2 VARCHAR(20), f_importance DOUBLE)
                                """
                self.cursor.execute(exec)

                exec = """ SELECT * FROM model_output """
                output_check = self.cursor.fetchall()

                print(output_check)

                ordered_data: list(Tuple[str, str, int],...) = [row for row in insert_data]
                print(ordered_data)
                ordered_data = sorted(ordered_data, key=lambda f_imp: f_imp[1], reverse=True)
                for row in ordered_data:
                    exec = f""" INSERT INTO model_output (concept1, concept2, f_importance) VALUES
                                ({row[0]}, {row[1]}, {row[2]})"""
                    self.cursor.execute(exec)
                    self.conn.commit()
                self.cursor.execute(exec)
        else:
            #create new table with input data
            print("table doesn't exist")
            exec = """ CREATE TABLE model_output (
                    concept1 VARCHAR(20), concept2 VARCHAR(20), f_importance DOUBLE)
                """
            self.cursor.execute(exec)
            ordered_data : list(Tuple[str,str,int]) = [row for row in insert_data]
            print(ordered_data)
            print(ordered_data[0][2])
            ordered_data.sort(key=lambda x: x[2], reverse = True)
            print(ordered_data)
            for row in ordered_data:
                try:
                    exec = f"""INSERT INTO model_output (concept1, concept2, f_importance) 
                    VALUES('{row[0]}', '{row[1]}', {row[2]})"""
                    print(exec)
                    self.cursor.execute(exec)
                    self.conn.commit()
                except sql.err.Error as e:
                    print(e)

    def main(self):
        temp_data: Tuple[Tuple[str, str, int],...] = [["a", "b", 3], ["a", "c", 4]]
        ModelOutput.ordered_insert(self, temp_data)


cp = ModelOutput()
if __name__ == "__main__": cp.main()