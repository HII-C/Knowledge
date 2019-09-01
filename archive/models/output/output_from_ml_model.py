from getpass import getpass
from operator import itemgetter
from collections import defaultdict
from typing import List, Dict, Tuple
import MySQLdb as sql

from models.util.db_util import DatabaseHandle


class ModelOutput:
    cond_db: DatabaseHandle = None

    def __init__(self, db_params=None):
        if db_params is not None:
            self.cond_db = DatabaseHandle(**db_params)
        else:
            self.cond_db = None

    # create new table called ModelOutput
        # order it by accuracy

    def ordered_insert(self, table, insert_data: List[Tuple[str, str, float]], model_acc):
        # if no table named model output, need to make a new table called model output
        exec = """
                SHOW TABLES """
        self.cond_db.cursor.execute(exec)
        tbls = [x[0] for x in self.cond_db.cursor.fetchall()]

        if table not in tbls:
            # create new table with input data
            exec = f""" CREATE TABLE {table} (
                    concept1 VARCHAR(20), concept2 VARCHAR(20), f_importance DOUBLE, model_acc DOUBLE)
                """
            self.cond_db.cursor.execute(exec)
            self.cond_db.connection.commit()

        insert_data.sort(key=itemgetter(2), reverse=True)
        c1_list = tuple([x[0] for x in insert_data])
        c2_list = tuple([x[1] for x in insert_data])

        exec_str = f'''
                        DELETE FROM {table}
                        WHERE concept1 IN {c1_list}
                        AND concept2 IN {c2_list}
                        AND model_acc <= {model_acc}'''
        self.cond_db.cursor.execute(exec_str)
        self.cond_db.connection.commit()

        tmp = [tuple([x[0], x[1], x[2], model_acc]) for x in insert_data]
        exec_str = f""" INSERT INTO {table} (concept1, concept2, f_importance, model_acc) 
                        VALUES (%s, %s, %s, %s)"""
        self.cond_db.cursor.executemany(exec_str, tmp)
        self.cond_db.connection.commit()
