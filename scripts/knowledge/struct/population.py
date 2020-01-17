
import logging as log

from knowledge.util.database import DatabaseUtil
from knowledge.util.error import UserExitError


class Population:
    '''population managing class

    must call `generate_population` to create population before
    fetching patients, encounters or events
    '''
    def __init__(self, database):
        self.database = DatabaseUtil(params=database)

        self.mimic = 'mimiciiiv14'
        self.synthea = 'synthea'
        self.umls = 'umls'
        self.rxnorm = 'rxnorm'

        self.population = False
        self.source = None
        self.patients = None
        self.encounters = None
        self.items = None


    def create_tables(self, force=False):
        tables = ('patients', 'encounters', 'items')
        if not force:
            exists = self.database.table_exists(*tables)
            tables = '", "'.join(exists)
            if len(exists):
                log.warning(f'Table{"s" if len(tables) > 1 else ""} '
                    f'"{tables}" already exist in database '
                    f'"{self.database.db}". Drop and continue? [Y/n] ')
                if input().lower() not in ('y', 'yes'):
                    log.error('User chose to terminate process.')
                    raise RuntimeError
        for table in self.database.tables.keys():
            self.database.create_table(table)


    def delete_tables(self, tables=[]):
        '''delete/reset current population
        '''
        query = 'DROP TABLE IF EXISTS %s'
        if len(tables) == 0:
            tables = ('patients', 'encounters', 'items')
        for tbl in tables:
            self.database.cursor.execute(query % tbl)
            self.database.connection.commit()

        self.population = False
        self.source = None
        self.patients = None
        self.encounters = None


    def generate_population(self, source, size=None, rand=False, seed=None):
        '''generate a population tables

        Parameters
        ----------
        source: str
            The source database to generate population from, options are
            "mimic" and "synthea".
        size: int
            A maximum number of patients in population.
        rand: bool
            Specify whether or not to randomly sort the population; default
            is false.
        seed: int
            Specify a seed for the random sorting, which can make populations
            reproducable; default is null.
        '''
        if source == 'synthea':
            db = self.synthea
            tbl = 'patients'
            col = 'id'
        elif source == 'mimic':
            db = self.mimic
            tbl = 'PATIENTS'
            col = 'SUBJECT_ID'
        else:
            raise ValueError('Population expected source to be "synthea" or '
                f'"mimic" but got "{source}".')
        
        self.source = source
        self.population = True

        log.info('Generating population patients.')
        query = f'''
            CREATE TABLE patients
            SELECT
                {col} AS patient
            FROM {db}.{tbl}
            {f"ORDER BY RAND({seed if seed else ''})" if rand else ""}
            {f"LIMIT {size}" if size is not None else ""} '''
        self.database.cursor.execute(query)
        self.database.connection.commit()

        if source == 'synthea':
            db = self.synthea
            tbl = 'encounters'
            col1 = 'id'
            col2 = 'patient'
        elif source == 'mimic':
            db = self.mimic
            tbl = 'ADMISSIONS'
            col1 = 'HADM_ID'
            col2 = 'SUBJECT_ID'

        log.info('Generating population encounters.', time=True)
        query = f'''
            CREATE TABLE encounters
            SELECT
                enc.{col2} AS patient,
                enc.{col1} AS encounter
            FROM {db}.{tbl} AS enc
            INNER JOIN patients
            ON enc.{col2} = patients.patient
            ORDER BY patient '''
        self.database.cursor.execute(query)
        self.database.connection.commit()

        query = f'''
            CREATE INDEX encounter
            USING HASH
            ON encounters(encounter) '''
        self.database.cursor.execute(query)
        self.database.connection.commit()

        query = f'''
            SELECT COUNT(*)
            FROM patients
            UNION
            SELECT COUNT(*)
            FROM encounters '''
        self.database.cursor.execute(query)
        self.patients, self.encounters = [int(row[0])
            for row in self.database.cursor.fetchall()]

    
    def generate_items(self, source, min_support=0, max_support=1):
        '''generate items table with support

        Parameters
        ----------

        '''
        source = set(source)
        if not source.issubset(('observations', 'treatments', 'conditions')):
            raise ValueError()
        if not self.population:
            raise RuntimeError('Must generate a population before generating '
                'items from it.')

        if self.source == 'synthea':
            subquery = {}
            subquery['observations'] = f'''
                SELECT
                    CONCAT("O-", obs.code)  AS item,
                    COUNT(*) AS support
                FROM {self.synthea}.observations AS obs
                INNER JOIN encounters
                USING(encounter) 
                GROUP BY item '''
            subquery['conditions'] = f'''
                SELECT
                    CONCAT("C-", cnd.code) AS item,
                    COUNT(*)
                FROM {self.synthea}.conditions AS cnd
                INNER JOIN encounters
                USING(encounter)
                GROUP BY item '''
            subquery['treatments'] = f'''
                SELECT
                    CONCAT("C-", trt.code) AS item,
                    COUNT(*) AS support
                FROM {self.synthea}.medications AS trt
                INNER JOIN encounters
                USING(encounter)
                GROUP BY item '''
        elif self.source == 'mimic':
            subquery = {}
            subquery['observations'] = f'''
                SELECT
                    CONCAT("O-", itm.LOINC_CODE)  AS item,
                    COUNT(*) AS support
                FROM {self.mimic}.LABEVENTS AS obs
                INNER JOIN encounters AS enc
                ON enc.encounter = obs.HADM_ID
                INNER JOIN {self.mimic}.D_LABITEMS AS itm
                ON obs.ITEMID = itm.ITEMID
                WHERE itm.LOINC_CODE IS NOT NULL
                GROUP BY item '''
            subquery['conditions'] = f'''
                SELECT
                    CONCAT("C-", cnd.ICD9_CODE) AS item,
                    COUNT(*)
                FROM {self.mimic}.DIAGNOSES_ICD AS cnd
                INNER JOIN encounters AS enc
                ON enc.encounter = cnd.HADM_ID
                WHERE cnd.ICD9_CODE IS NOT NULL
                GROUP BY item '''
            subquery['treatments'] = f'''
                SELECT
                    CONCAT("T-", trt.NDC) AS item,
                    COUNT(*)
                FROM {self.mimic}.PRESCRIPTIONS AS trt
                INNER JOIN encounters AS enc
                ON enc.encounter = trt.HADM_ID
                WHERE trt.NDC IS NOT NULL
                GROUP BY item '''
        else:
            raise ValueError('Population expected source to be "synthea" or '
                f'"mimic" but got "{source}".')

        subquery = [val for key, val in subquery.items() if key in source]
        query = '''
            CREATE TABLE items (
                item VARCHAR(255),
                support INT UNSIGNED )
            SELECT *
            FROM ( '''
        query += '\nUNION\n'.join(subquery)
        query += f'''
            ) AS subquery
            WHERE support >= {min_support * self.encounters}
            AND support <= {max_support * self.encounters} '''
        self.database.cursor.execute(query)
        self.database.connection.commit()

        query = f'''
            SELECT COUNT(*)
            FROM items '''
        self.database.cursor.execute(query)
        self.items = int(self.database.cursor.fetchall()[0][0])

    
    def fetch_patients(self, size=None):
        '''fetch patients from population

        Parameters
        ----------
        size: int
            A maximum number of rows to return.

        Returns
        -------
        result: list[list[str]]
            A list of lists containing the patient codes.
        '''
        if self.population:
            query = f'''
                SELECT patient
                FROM patients
                {f"LIMIT {size}" if size is not None else ""} '''
        else:
            raise RuntimeError('Must generate a population before fetching '
                'patients from it.')

        self.database.cursor.execute(query)
        return self.database.cursor.fetchall()


    def fetch_encounters(self, size=None):
        '''fetch encounters from population

        Parameters
        ----------
        size: int
            A maximum number of rows to return.

        Returns
        -------
        result: list[list[str]]
            A list of lists containing the patient and encounter codes
            respectively. The table is sorted by the encounter code.
        '''
        if self.population:
            query = f'''
                SELECT
                    patient,
                    encounter
                FROM encounters
                {f"LIMIT {size}" if size is not None else ""} '''
        else:
            raise RuntimeError('Must generate a population before fetching '
                'encounters from it.')

        self.database.cursor.execute(query)
        return self.database.cursor.fetchall()


    def fetch_items(self):
        '''fetch support from items
        '''
        if self.items is None:
            raise RuntimeError('Must generate items before fetching '
                'support from it.')

        query = f'''
            SELECT
                item,
                support
            FROM items '''
        self.database.cursor.execute(query)
        return self.database.cursor.fetchall()

    
    def fetch_events(self, source, offset=None, limit=None):
        '''fetch events from population

        Parameters
        ----------
        source: str
            A list of strings containing the types of events to fetch.
            Options are "observations", "treatments", and "conditions".
            List can be any nonempty subset of these options.

        offset: int

        limit: int

        Returns
        -------
        result: list[list[str]]
            A list of lists containing the encounter and event codes
            respectively. The table is sorted by the encounter code.
        '''
        source = set(source)
        if not source.issubset(('observations', 'treatments', 'conditions')):
            raise ValueError()
        if not self.population:
            raise RuntimeError('Must generate a population before fetching '
                'events from it.')

        if self.source == 'synthea':
            subquery = {}
            subquery['observations'] = f'''
                SELECT
                    enc.encounter,
                    CONCAT("O-", obs.code)
                FROM {self.synthea}.observations AS obs
                INNER JOIN (
                    SELECT encounter
                    FROM encounters
                    LIMIT {offset}, {limit}
                ) AS enc
                USING(encounter) '''
            subquery['conditions'] = f'''
                SELECT
                    enc.encounter,
                    CONCAT("C-", cnd.code)
                FROM {self.synthea}.conditions AS cnd
                INNER JOIN (
                    SELECT encounter
                    FROM encounters
                    LIMIT {offset}, {limit}
                ) AS enc
                USING(encounter) '''
            subquery['treatments'] = f'''
                SELECT
                    enc.encounter,
                    CONCAT("C-", trt.code)
                FROM {self.synthea}.medications AS trt
                INNER JOIN (
                    SELECT encounter
                    FROM encounters
                    LIMIT {offset}, {limit}
                ) AS enc
                USING(encounter) '''
        elif self.source == 'mimic':
            subquery = {}
            subquery['observations'] = f'''
                SELECT
                    enc.encounter,
                    CONCAT("O-", itm.LOINC_CODE)
                FROM {self.mimic}.LABEVENTS AS obs
                INNER JOIN (
                    SELECT encounter
                    FROM encounters
                    LIMIT {offset}, {limit}
                ) AS enc
                ON enc.encounter = obs.HADM_ID
                INNER JOIN {self.mimic}.D_LABITEMS AS itm
                USING(ITEMID)'''
            subquery['conditions'] = f'''
                SELECT
                    enc.encounter,
                    CONCAT("C-", cnd.ICD9_CODE)
                FROM {self.mimic}.DIAGNOSES_ICD AS cnd
                INNER JOIN (
                    SELECT encounter
                    FROM encounters
                    LIMIT {offset}, {limit}
                ) AS enc
                ON enc.encounter = cnd.HADM_ID '''
            subquery['treatments'] = f'''
                SELECT
                    enc.encounter,
                    CONCAT("C-", trt.NDC)
                FROM {self.mimic}.PRESCRIPTIONS AS trt
                INNER JOIN (
                    SELECT encounter
                    FROM encounters
                    LIMIT {offset}, {limit}
                ) AS enc
                ON enc.encounter = trt.HADM_ID '''
        else:
            raise ValueError('Population expected source to be "synthea" or '
                f'"mimic" but got "{source}".')

        subquery = {key: val for key, val in subquery.items() 
            if key in source}
        query = '\nUNION\n'.join(subquery.values())
        query += '\nORDER BY encounter'
        self.database.cursor.execute(query)
        return self.database.cursor.fetchall()