
import MySQLdb
import warnings

from knowledge.util.print import PrintUtil as pr
from knowledge.util.error import UserExitError

warnings.filterwarnings('ignore', category=MySQLdb._exceptions.Warning)

class DatabaseUtil:
    def __init__(self, params=None, database=None):
        if type(database) is DatabaseUtil:
            self = database
        elif type(params) is dict:
            keys = ('user', 'password', 'db', 'host', 'unix_socket')
            login = {key:params[key] for key in keys if key in params}
            self.user = params['user']
            self.host = params['host']
            self.db = params['db']
            self.tables = params['tables'] if 'tables' in params else {}
            try:
                self.connection = MySQLdb.connect(**login)
                self.cursor = self.connection.cursor()
            except MySQLdb._exceptions.OperationalError as err:
                if err.args[0] == 1049:
                    term = pr.print(f'Database "{self.db}" does not exist. Create',
                        ' and continue? [Y/n] ', time=True, inquiry=True)
                    if term:
                        del login['db']
                        connection = MySQLdb.connect(**login)
                        cursor = connection.cursor()
                        cursor.execute(f'CREATE DATABASE {params["db"]}')
                        connection.commit()
                        cursor.close()
                        connection.close()
                        login['db'] = self.db
                        self.connection = MySQLdb.connect(**login)
                        self.cursor = self.connection.cursor()
                    else:
                        raise UserExitError('User chose to terminate process.')
                else:
                    raise err

    def drop_table(self, table):
        query = f'DROP TABLE IF EXISTS {self.db}.{table}'
        self.cursor.execute(query)
        self.connection.commit()

    def table_exists(self, *tables):
        conditions = f'" or `Tables_in_{self.db}` like "'.join(tables)
        query = f'''
            SHOW TABLES FROM {self.db}
            WHERE `Tables_in_{self.db}` like "{conditions}"'''
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def create_table(self, table):
        table_data = self.tables[table]
        sql_schema = (', ').join(table_data['schema'])
        query = f'DROP TABLE IF EXISTS {self.db}.{table}'
        self.cursor.execute(query)
        self.connection.commit()
        query = f'CREATE TABLE {self.db}.{table} ({sql_schema})'
        self.cursor.execute(query)
        self.connection.commit()

    def create_index(self, table, name):
        columns = (', ').join(self.tables[table]['indexes'][name])
        query = f'''
            CREATE INDEX {name}
            ON {self.db}.{table} ({columns})'''
        self.cursor.execute(query)
        self.connection.commit()

    def create_primary_idx(self, table):
        cols = ', '.join(self.tables[table]['primary_idx'])
        query = f'''
            ALTER TABLE {self.db}.{table}
            ADD PRIMARY KEY ({cols})'''
        self.cursor.execute(query)
        self.connection.commit()

    def create_hash_idx(self, table, name):
        cols = ', '.join(self.tables[table]['hash_idxs'][name])
        query = f'''
            CREATE INDEX {name} USING HASH
            ON {self.db}.{table} ({cols})'''
        self.cursor.execute(query)
        self.connection.commit()        

    def create_btree_idx(self, table, name):
        cols = ', '.join(self.tables[table]['btree_idxs'][name])
        query = f'''
            CREATE INDEX {name}
            ON {self.db}.{table} ({cols})'''
        self.cursor.execute(query)
        self.connection.commit()   
    
    def create_spatial_idx(self, table, name):
        cols = ', '.join(self.tables[table]['spatial_idxs'][name])
        query = f'''
            CREATE SPATIAL INDEX {name}
            ON {self.db}.{table} ({cols})'''
        self.cursor.execute(query)
        self.connection.commit()
    
    def create_all_idxs(self, table, silent=False):
        tbl_data = self.tables[table]
        if 'primary_idx' in tbl_data:
            if not silent:
                pr.print(f'Creating primary index on table "{table}".', time=True)
                self.create_primary_idx(table)
        if 'spatial_idxs' in tbl_data:
            for idx in tbl_data['spatial_idxs']:
                if not silent:
                    pr.print(f'Creating spatial index "{idx}" on table "{table}".', time=True)
                self.create_spatial_idx(table, idx)
        if 'hash_idxs' in tbl_data:
            for idx in tbl_data['hash_idxs']:
                if not silent:
                    pr.print(f'Creating hash index "{idx}" on table "{table}".', time=True)
                self.create_hash_idx(table, idx)
        if 'btree_idxs' in tbl_data:
            for idx in tbl_data['btree_idxs']:
                if not silent:
                    pr.print(f'Creating btree index "{idx}" on table "{table}".', time=True)
                self.create_btree_idx(table, idx)

    def write_rows(self, data, table):
        s_strs = ', '.join(['%s'] * len(self.tables[table]['schema']))
        query = f''' 
            INSERT INTO {self.db}.{table}
            VALUES ({s_strs}) '''
        self.cursor.executemany(query, data)
        self.connection.commit()

    def write_geom_rows(self, data, table, geo=0, srid=0):
        s_strs = ', '.join(['%s'] * (len(self.tables[table]['schema']) - geo))
        s_strs += f', ST_GEOMFROMTEXT(%s, {srid})' * geo
        query = f''' 
            INSERT INTO {self.db}.{table}
            VALUES ({s_strs}) '''
        self.cursor.executemany(query, data)
        self.connection.commit()
