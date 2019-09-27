
import pandas as pd
import numpy as np

from knowledge.util.error import ConfigError, UserExitError
from knowledge.util.print import PrintUtil as pr
from knowledge.model.fpgrowth.database import FpgrowthDatabaseUtil

class FpgrowthModel:
    def __init__(self, database):
        self.database = FpgrowthDatabaseUtil(database)

    @staticmethod
    def validate_config(config):
        required = ('min_support', 'min_confidence')
        types = (int, float)

        for param, kind in zip(required, types):
            if param not in config:
                raise ConfigError(f'Paramter "{param}" is required.')
            if type(config[param]) is not kind:
                raise TypeError(f'Parameter "{param}" expected to be of type "'
                    f'{kind.__name__}" but found "{type(config[param]).__name__}".')

        if config['min_support'] < 1:
            raise ValueError('Parameter "min_support" must be n >= 1.')
        if config['min_confidence'] < 0:
            raise ValueError('Parameter "min_confidence" must be n > 0.')

        optional = ('silent', 'create_idxs', 'force')
        types = (bool, bool, bool)
        defaults = (False, True, False)

        for param, kind, default in zip(optional, types, defaults):
            if param not in config:
                config[param] = default
            elif type(config[param]) is not kind:
                raise TypeError(f'Parameter "{param}" expected to be of type "'
                    f'{kind.__name__}" but found "{type(config[param]).__name__}".')

        return config

    def run(self, config, silent=False):
        config = self.validate_config(config)
        silent = config['silent'] or silent

        if not silent:
            pr.print('Beginning fpgrowth model run.', time=True)
            pr.print('Predefining tables on database.', time=True)
        self.create_tables()

        exit()

        if not silent:
            pr.print('Building transaction database dense matrix.', time=True)
        matrix = self.build_matrix(silent)

        if not silent:
            pr.print('Building pattern support binary tree.', time=True)
        patterns = self.count_patterns(matrix, config['min_support'], silent)

        if not silent:
            pr.print('Building assocations table.', time=True)
        associations = self.find_associations(patterns, 
            config['min_confidence'], silent)

        if not silent:
            pr.print('Pushing found associations to database.', time=True)
        self.push_results(associations, silent)

        if config['create_idxs']:
            self.create_idxs(silent)

    def build_matrix(self, silent=False):
        return 0

    def count_patterns(self, matrix, min_support, silent=False):
        return 0

    def find_associations(self, patterns, min_confidence, silent=False):
        return 0

    def push_results(self, results, silent):
        pass

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
        