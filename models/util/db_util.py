from typing import List, Dict, Tuple
from getpass import getpass
import MySQLdb as sql

from models.util.concept_util import ConceptType


class DatabaseHandle:
    connection: sql.connections.Connection = None
    cursor: sql.cursors.BaseCursor = None
    user: str = None
    host: str = None
    db: str = None

    def __init__(self, params: Dict[str, str] = None,
                 handle: DatabaseHandle = None):
        if handle is not None:
            self = handle

        if params is not None:
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
