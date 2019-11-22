
from knowledge.util.database import DatabaseUtil
from knowledge.util.print import PrintUtil as pr


class Population(DatabaseUtil):
    def __init__(self, database):
        super().__init__(params=database)

        self.mimic = 'mimiciiiv14'
        self.synthea = 'synthea'
        self.umls = 'umls'
        self.rxnorm = 'rxnorm'

        self.population = False
        self.source = None


    def generate_population(self, source, size=None, rand=False, seed=None):
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
        query = f'''
            CREATE TEMPORARY TABLE patients
            SELECT
                {pcol} AS patient
            FROM {db}.{ptbl}
            {f"ORDER BY RAND({seed if seed else ''})" if rand else ""}
            {f"LIMIT {size}" if size is not None else ""} '''
        self.cursor.execute(query)
        self.cursor.commit()
        query = f'''
            CREATE TEMPORARY TABLE encounters
            SELECT
                {pcol} AS patient,
                {ecol} AS encounter
            FROM {db}.{etbl}
            ORDER BY patient
            {f"LIMIT {size}" if size is not None else ""} '''
        self.source = source
        self.cursor.execute(query)
        self.cursor.commit()
        self.population = True

    
    def fetch_patients(self, size=None):
        if self.population:
            query = f'''
                SELECT patient
                FROM population
                {f"LIMIT {size}" if size is not None else ""} '''
        else:
            raise RuntimeError('Must generate a population before fetching '
                'patients from it.')
        self.cursor.execute(query)
        return self.cursor.fetchall()


    def fetch_encounters(self, size=None):
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
        self.cursor.execute(query)
        return self.cursor.fetchall()

    
    def fetch_events(self, source, size=None):
        '''fetch event codes and values from medical dataset

        Parameters
        ----------
        source: str
            The medical dataset source to fetch from. Options are "mimic"
            and "synthea".

        type: list[str]
            A list of strings containing the types of events to fetch.
            Options are "observations", "treatments", and "conditions".
            List can be any nonempty subset of these options.
        
        patients: list[str]
            A list of patients to select events for. Must correspond to
            the unique patient code used to identify patients.

        encounters: list[str]
            A list of encounters to select events for. Must correspond to
            the unique encounter code used to identify encounters.

        size: int
            A maximum number of rows to return; this could possibly (most
            likely) truncate an encounter.

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

        if self.source == 'synthea':
            subquery = {}
            subquery['observations'] = f'''
                SELECT
                    encounters.encounter,
                    CONCAT("O-", obs.code)
                FROM encounters
                INNER JOIN {self.synthea}.observations AS obs
                USING(encounter) '''
            subquery['conditions'] = f'''
                SELECT
                    encounters.encounter,
                    CONCAT("C-", cnd.code)
                FROM encounters
                INNER JOIN {self.synthea}.conditions AS cnd
                USING(encounter) '''
            subquery['treatment'] = f'''
                SELECT
                    encounters.encounter,
                    CONCAT("C-", trt.code)
                FROM encounters
                INNER JOIN {self.synthea}.treatments AS trt
                USING(encounter) '''
        elif source == 'mimic':
            subquery = {}
            subquery['observations'] = f'''
                SELECT
                    encounters.encounter,
                    CONCAT("O-", itm.LOINC_CODE)
                FROM encounters
                INNER JOIN {self.mimic}.LABEVENTS AS obs
                USING(encounter)
                INNER JOIN {self.mimic}.D_LABITEMS AS itm
                USING(ITEMID)'''
            subquery['conditions'] = f'''
                SELECT
                    encounters.encounter,
                    CONCAT("C-", cnd.ICD9_CODE)
                FROM encounters
                INNER JOIN {self.mimic}.DIAGNOSES_ICD AS cnd
                USING(encounter) '''
            subquery['treatment'] = f'''
                SELECT
                    encounters.encounter,
                    CONCAT("C-", trt.NDC)
                FROM encounters
                INNER JOIN {self.mimic}.PRESCRIPTIONS AS trt
                USING(encounter) '''
        else:
            raise ValueError('Population expected source to be "synthea" or '
                f'"mimic" but got "{source}".')

        subquery = {key: val for key, val in subquery.items() 
            if key in source}
        query = '\nUNION\n'.join(subquery.values())
        query += '\nORDER BY encounter'
        query += f'\nLIMIT {size}' if size is not None else ''
        self.cursor.execute(query)
        return self.cursor.fetchall()