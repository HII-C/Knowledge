from typing import List, Dict, Tuple
from collections import defaultdict
from util.db_util import DatabaseHandle
import MySQLdb as sql



class ModelOutput:
    cond_db: DatabaseHandle = None

    def __init__(self, db_params):
        self.cond_db = DatabaseHandle(**db_params)


    #create new table called ModelOutput
        #order it by accuracy

   # def row_to_tuple(self): ????
    def ordered_insert(self, insert_data: Tuple[Tuple[str, str, int]]):
        #if no table named model output, need to make a new table called model output
        exec = """
                SHOW TABLES """
        self.cond_db.execute(exec)
        tbls = self.cond_db.fetchall()

        if("model_output") in tbls[0]:
            #table already exists
            #check to see if new f_importance is higher than the old one

            exec = """ SELECT f_importance 
            FROM model_output LIMIT 1"""
            self.cond_db.execute(exec)
            tmp_f_im = self.cond_db.fetchall()

            if tmp_f_im[0][0] < insert_data[2][0]:
                exec = """ DROP TABLE model_output"""

                # create new table with input data
                exec = """ CREATE TABLE model_output (
                                    concept1 VARCHAR(20), concept2 VARCHAR(20), f_importance DOUBLE)
                                """
                self.cond_db.execute(exec)
                ordered_list: list[Tuple] = [row for row in insert_data]
                ordered_list = ordered_list.sort(key=lambda tup: tup[2])

                for row in ordered_list:
                    exec = f""" INSERT INTO model_output (concept1, concept2, f_importance) VALUES
                                                ({row[0]}, {row[1]}, {row[2]})"""
                    self.cond_db.execute(exec)
        else:
            #create new table with input data
            exec = """ CREATE TABLE model_output (
                    concept1 VARCHAR(20), concept2 VARCHAR(20), f_importance DOUBLE)
                """
            self.cond_db.execute(exec)
            ordered_list: list[Tuple] = [row for row in  insert_data]
            ordered_list = ordered_list.sort(key = lambda tup: tup[2])

            for row in ordered_list:
                exec = f""" INSERT INTO model_output (concept1, concept2, f_importance) VALUES
                                ({row[0]}, {row[1]}, {row[2]})"""
                self.cond_db.execute(exec)