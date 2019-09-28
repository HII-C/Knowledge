
import pandas as pd

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules

from knowledge.util.print import PrintUtil as pr
from knowledge.util.error import ConfigError, UserExitError
from knowledge.model.fpgrowth.database import FpgrowthDatabaseUtil

class FpgrowthModel:
    def __init__(self, database):
        self.database = FpgrowthDatabaseUtil(database)

    @staticmethod
    def validate_config(config):
        required = ('min_support', 'min_confidence')
        types = (float, float)

        for param, kind in zip(required, types):
            if param not in config:
                raise ConfigError(f'Paramter "{param}" is required.')
            if type(config[param]) is not kind:
                raise TypeError(f'Parameter "{param}" expected to be of type "'
                    f'{kind.__name__}" but found "{type(config[param]).__name__}".')

        if config['min_support'] <= 0:
            raise ValueError('Parameter "min_support" must be n > 0.')
        if config['min_confidence'] <= 0:
            raise ValueError('Parameter "min_confidence" must be n > 0.')

        optional = ('silent', 'create_idxs', 'force', 'max_events')
        types = (bool, bool, bool, int)
        defaults = (False, True, False, 0)

        for param, kind, default in zip(optional, types, defaults):
            if param not in config:
                config[param] = default
            elif type(config[param]) is not kind:
                raise TypeError(f'Parameter "{param}" expected to be of type "'
                    f'{kind.__name__}" but found "{type(config[param]).__name__}".')

        if config['max_events'] < 0:
            raise ValueError('Parameter "max_events" must be n >= 0.')

        return config

    def run(self, config, silent=False):
        config = self.validate_config(config)
        silent = config['silent'] or silent

        if not silent:
            pr.print('Beginning fpgrowth model run.', time=True)
            pr.print('Predefining tables on database.', time=True)
        self.create_tables()

        if not silent:
            pr.print('Fetching transaction database to dense matrix.', time=True)
        matrix = self.build_matrix(config['max_events'])

        if not silent:
            pr.print(f'Fetched {len(matrix)} transactions.', time=True)
            pr.print('Finding frequent itemsets in dense matrix.', time=True)
        itemsets = self.frequent_itemsets(matrix, config['min_support'])

        if not silent:
            pr.print(f'Found {len(itemsets)} frequent itemsets.', time=True)
            pr.print('Building assocations rules table.', time=True)
        associations = self.association_rules(itemsets, config['min_confidence'])

        if not silent:
            pr.print('Pushing found associations to database.', time=True)
        self.push_results(associations, silent)

        if config['create_idxs']:
            self.create_idxs(silent)

    def build_matrix(self, max_events):
        events = self.database.get_events(max_events)

        transactions = []
        hadm = []
        hadmid = 0
        for event in events:
            if event[0] != hadmid:
                hadmid = event[0]
                if len(hadm):
                    transactions.append(hadm)
                hadm = []
            hadm.append(event[1])
        del events

        encoder = TransactionEncoder()
        array = encoder.fit(transactions).transform(transactions)
        return pd.DataFrame(array, columns=encoder.columns_)

    def frequent_itemsets(self, matrix, min_support):
        return fpgrowth(matrix, min_support=min_support)

    def association_rules(self, itemsets, min_confidence):
        return association_rules(itemsets, metric="confidence", 
            min_threshold=min_confidence)

    def push_results(self, results, silent):
        inf = float('inf')
        associations = []
        antecedents = []
        consequents = []
        assoc_id = 0
        antec_id = 0
        conse_id = 0
        for idx, row in results.iterrows():
            associations.append((
                assoc_id,
                row['support'],
                row['confidence'],
                row['lift'],
                row['leverage'],
                row['conviction'] if row['conviction'] != inf else None))
            antecs = row['antecedents']
            for idx, antec in zip(range(len(antecs)), antecs):
                antecedents.append((
                    antec_id,
                    assoc_id,
                    idx,
                    antec))
                antec_id += 1
            conses = row['consequents']
            for idx, conse in zip(range(len(conses)), conses):
                consequents.append((
                    conse_id,
                    assoc_id,
                    idx,
                    conse))
                conse_id += 1
            assoc_id += 1

        self.database.write_rows(associations, 'associations')
        self.database.write_rows(antecedents, 'antecedents')
        self.database.write_rows(consequents, 'consequents')

    def create_tables(self, force=False):
        if not force:
            exists = self.database.table_exists(*list(self.database.tables.keys()))
            tables = '", "'.join(exists)
            if len(exists):
                force = pr.print(f'Tables "{tables}" already exist in '
                    f'"{self.database.db}". Drop and continue? [Y/n] ', 
                    inquiry=True, time=True)
            else:
                force = True
        if force:
            for table in self.database.tables.keys():
                self.database.create_table(table)
        else:
            raise UserExitError('User chose to terminate process.')

    def create_idxs(self, silent=False):
        if not silent:
            pr.print(f'Creating all indexes in database "{self.database.db}".',
                time=True)
        for tbl in self.database.tables:
            self.database.create_all_idxs(tbl)
        if not silent:
            pr.print(f'Index creation complete.', time=True)
        