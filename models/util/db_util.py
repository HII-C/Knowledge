from typing import List, Dict, Tuple
from getpass import getpass
import MySQLdb as sql
import MySQLdb.connections as connections

from models.util.concept_util import ConceptType


class DatabaseHandle:
    connection = connections.Connection
    cursor = connections.cursors.Cursor
    user: str = None
    host: str = None
    db: str = None

    def __init__(self, params: Dict[str, str] = None, handle=None):
        if type(handle) is DatabaseHandle:
            self = handle

        if isinstance(params, dict):
            try:
                self.connection = sql.connect(user=params['user'],
                                              password=params['password'],
                                              db=params['db'], host=params['host'])
                self.cursor = self.connection.cursor()
                self.user = params['user']
                self.host = params['host']
                self.db = params['db']
            except sql._exceptions.DatabaseError:
                # Creating the database that didn't exist, if that was the error above
                connection: sql.connections.Connection
                connection = sql.connect(user=params['user'],
                                         password=params['password'],
                                         db='mysql', host=params['host'])
                cursor = connection.cursor()
                cursor.execute(f'CREATE DATABASE {params["db"]}')
                cursor.commit()
                cursor.close()
                connection.close()
                self.connection = sql.connect(user=params['user'],
                                              password=params['password'],
                                              db=params['db'], host=params['host'])
                self.cursor = self.connection.cursor()
                self.user = params['user']
                self.host = params['host']
                self.db = params['db']

    def lhs_bin(self, subj_id: List[int],
                concept: ConceptType) -> List[int]:
        exec_str = f''' SELECT (
                            SUBJECT_ID, 
                            {concept.get_field()})
                        FROM 
                            {concept.get_table()}
                        WHERE SUBJECT_ID 
                            IN 
                        {tuple(subj_id)}'''
        self.cursor.execute(exec_str)
        return self.cursor.fetchall()

    def lhs_cont(self, subj_id: List[int],
                 concept: ConceptType) -> List[int]:
        exec_str = f''' SELECT (
                            SUBJECT_ID, 
                            {concept.get_field()},
                            {concept.get_value()})
                        FROM 
                            {concept.get_table()}
                        WHERE SUBJECT_ID 
                            IN 
                        {tuple(subj_id)}'''
        self.cursor.execute(exec_str)
        return self.cursor.fetchall()

    def rhs_bin(self, subj_id: List[int],
                concept: ConceptType,
                target: str):
        exec_str = f''' SELECT 
                            (SUBJECT_ID)
                        FROM 
                            {concept.get_table()}
                        WHERE 
                            SUBJECT_ID 
                        IN 
                            {tuple(subj_id)}
                        AND 
                            {concept.get_field()} = {target}'''
        self.cursor.execute(exec_str)
        return self.cursor.fetchall()
