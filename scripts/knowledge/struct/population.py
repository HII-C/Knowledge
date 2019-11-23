
from knowledge.util.database import DatabaseUtil
from knowledge.util.print import PrintUtil as pr


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


    def clear_population(self):
        '''delete/reset current population
        '''
        query = 'DROP TABLE IF EXISTS %s'
        tables = ('patients', 'encounters', 'items')
        for tbl in tables:
            self.database.cursor.execute(query % tbl)
            self.database.cursor.commit()

        self.population = False
        self.source = None
        self.patients = None
        self.encounters = None


    def generate_population(self, source, size=None, rand=False, seed=None):
        '''generate a temporary population table

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
            ptbl = 'patients'
            pcol = 'patient'
            etbl = 'encounters'
            ecol = 'encounter'
        elif source == 'mimic':
            db = self.mimic
            ptbl = 'PATIENTS'
            pcol = 'SUBJECT_ID'
            etbl = 'ADMISSIONS'
            ecol = 'HADM_ID'
        else:
            raise ValueError('Population expected source to be "synthea" or '
                f'"mimic" but got "{source}".')
        
        self.source = source
        self.population = True

        query = f'''
            CREATE TEMPORARY TABLE patients
            SELECT
                {pcol} AS patient
            FROM {db}.{ptbl}
            {f"ORDER BY RAND({seed if seed else ''})" if rand else ""}
            {f"LIMIT {size}" if size is not None else ""} '''
        self.database.cursor.execute(query)
        self.database.cursor.commit()

        query = f'''
            CREATE TEMPORARY TABLE encounters
            SELECT
                {pcol} AS patient,
                {ecol} AS encounter
            FROM {db}.{etbl}
            ORDER BY patient
            {f"LIMIT {size}" if size is not None else ""} '''
        self.database.cursor.execute(query)
        self.database.cursor.commit()

        query = f'''
            SELECT COUNT(*)
            FROM patients
            UNION
            SELECT COUNT(*)
            FROM encounters '''
        self.database.cursor.execute(query)
        self.patients, self.encounters = self.database.cursor.fetchall()[0]

    
    def generate_items(self, min_support=0, max_support=1):
        '''generate items table with support

        Parameters
        ----------

        '''
        
        valid_source = ('observations', 'treatments', 'conditions')

        if type(source) is str:
            source = list(source)
        elif type(source) not in (list, tuple):
            raise TypeError()
        if not all(t in valid_source for t in source) or len(source) == 0:
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
                INNER JOIN encounters AS enc
                USING(encounter) 
                GROUP BY item '''
            subquery['conditions'] = f'''
                SELECT
                    CONCAT("C-", cnd.code) AS item,
                    COUNT(*)
                FROM {self.synthea}.conditions AS cnd
                INNER JOIN encounters AS enc
                USING(encounter)
                GROUP BY item '''
            subquery['treatment'] = f'''
                SELECT
                    CONCAT("C-", trt.code) AS item,
                    COUNT(*) AS support
                FROM {self.synthea}.treatments AS trt
                INNER JOIN encounters AS enc
                USING(encounter)
                GROUP BY item '''
        elif self.source == 'mimic':
            subquery = {}
            subquery['observations'] = f'''
                SELECT
                    enc.encounter,
                    CONCAT("O-", itm.LOINC_CODE)
                FROM {self.mimic}.LABEVENTS AS obs
                INNER JOIN encounters AS enc
                USING(encounter)
                INNER JOIN {self.mimic}.D_LABITEMS AS itm
                USING(ITEMID)'''
            subquery['conditions'] = f'''
                SELECT
                    enc.encounter,
                    CONCAT("C-", cnd.ICD9_CODE)
                FROM {self.mimic}.DIAGNOSES_ICD AS cnd
                INNER JOIN encounters AS enc
                USING(encounter) '''
            subquery['treatment'] = f'''
                SELECT
                    encounters.encounter,
                    CONCAT("C-", trt.NDC)
                FROM {self.mimic}.PRESCRIPTIONS AS trt
                INNER JOIN encounters AS enc
                USING(encounter) '''
        else:
            raise ValueError('Population expected source to be "synthea" or '
                f'"mimic" but got "{source}".')

        subquery = {key: val for key, val in subquery.items() 
            if key in source}
        query = '\nUNION\n'.join(subquery.values())
        query += 'ORDER BY support DESC'
        self.database.cursor.execute(query)
        self.database.cursor.commit()

        query = f'''
            SELECT SUM(support)
            FROM items '''
        self.database.cursor.execute(query)
        total = self.database.cursor.fetchall()[0][0]

        query = f'''
            DELETE FROM items
            WHERE support < {min_support * total}
            OR support > {max_support * total} '''
        self.database.cursor.execute(query)
        self.database.cursor.commit()

        query = f'''
            SELECT COUNT(*)
            FROM items '''
        self.database.cursor.execute(query)
        self.items = self.database.cursor.fetchall()[0][0]

    
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
                FROM population
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

        valid_source = ('observations', 'treatments', 'conditions')

        if type(source) is str:
            source = list(source)
        elif type(source) not in (list, tuple):
            raise TypeError()
        if not all(t in valid_source for t in source) or len(source) == 0:
            raise ValueError()
        if not self.population:
            raise RuntimeError('Must generate a population before fetching '
                'events from it.')

        if self.source == 'synthea':
            subquery = {}
            subquery['observations'] = f'''
                SELECT
                    encounters.encounter,
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
                    encounters.encounter,
                    CONCAT("C-", cnd.code)
                FROM {self.synthea}.conditions AS cnd
                INNER JOIN (
                    SELECT encounter
                    FROM encounters
                    LIMIT {offset}, {limit}
                ) AS enc
                USING(encounter) '''
            subquery['treatment'] = f'''
                SELECT
                    encounters.encounter,
                    CONCAT("C-", trt.code)
                FROM {self.synthea}.treatments AS trt
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
                USING(encounter)
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
                USING(encounter) '''
            subquery['treatment'] = f'''
                SELECT
                    encounters.encounter,
                    CONCAT("C-", trt.NDC)
                FROM {self.mimic}.PRESCRIPTIONS AS trt
                INNER JOIN (
                    SELECT encounter
                    FROM encounters
                    LIMIT {offset}, {limit}
                ) AS enc
                USING(encounter) '''
        else:
            raise ValueError('Population expected source to be "synthea" or '
                f'"mimic" but got "{source}".')

        subquery = {key: val for key, val in subquery.items() 
            if key in source}
        query = '\nUNION\n'.join(subquery.values())
        query += '\nORDER BY encounter'
        self.database.cursor.execute(query)
        return self.database.cursor.fetchall()