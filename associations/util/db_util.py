from typing import List, Dict, Tuple
import MySQLdb as sql
import MySQLdb.connections as connections
from getpass import getpass
from dataclasses import dataclass

import associations.util.concept_util as concept_util
#from associations.util.concept_util import ConceptType

class DatabaseHandle:
    connection: connections.Connection = None
    cursor: connections.cursors.Cursor = None
    user: str = None
    host: str = None
    db: str = None

    def __init__(self, user, password, db, host):
        self.connection = sql.connect(
            user=user, password=password, db=db, host=host)
        self.cursor = self.connection.cursor()
        self.user = user
        self.host = host
        self.db = db

    def lhs_bin(self, subj_id: List[int],
                concept: concept_util.ConceptType) -> List[int]:
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
                 concept: concept_util.ConceptType) -> List[int]:
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
                concept: concept_util.ConceptType,
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
