import MySQLdb as sql
import MySQLdb.connections as connections

from getpass import getpass
from dataclasses import dataclass


class DatabaseHandle:
    connection: connections.Connection = None
    cursor: connections.cursors.Cursor = None
    user: str = None
    host: str = None
    db: str = None

    def __init__(self, user, pw, db, host):
        self.connection = sql.connect(user=user, password=pw, db=db, host=host)
        self.cursor = self.connection.cursor()
        self.user = user
        self.host = host
        self.db = db
