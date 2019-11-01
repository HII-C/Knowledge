
import psutil
import pickle

from collections import defaultdict
from itertools import combinations

from knowledge.model.association.database import AssociationDatabase
from knowledge.struct.fpgrowth import Fpgrowth
from knowledge.util.config import ConfigUtil
from knowledge.util.error import ConfigError, UserExitError
from knowledge.util.print import PrintUtil as pr

class AssociationModel:
    def __init__(self, database):
        self.database = AssociationDatabase(database)

    @staticmethod
    def chunk(arr, n):
        for i in range(0, len(arr), n):
            yield arr[i: i+n]

    @staticmethod
    def validate_config(config):
        '''validates a configuration file for the association module
        
        Paramaters
        ----------
        config: dict
            A dictionary representation of the JSON config file.
            See documentation for specifications of the config file.
        
        Returns
        -------
        cleanded_config: dict
            The cleaned config, which includes all optional paramters
            not spefiied in the input config with thier default values.
            This cleaned config can be used to run the model.

        Throws
        ------
        ConfigError
            A required paramater in the config is missing.
        TypeError
            A parameter in the config is not of the correct type.
        ValueError
            A paramter in the config is out of range of the allowed
            set of values.
        '''

        pass


    def run(self, config, silent=None):
        '''runs the fpgrowth model with specified configurations
        Parameters
        ----------
        config: dict
            A dictionary representation of the JSON config file.
            See documentation for specifications of the config file.

        Throws
        ------
        UserExitError
            When prompted, the user chose to exit rather than procede.
        '''

        force = config['run']['force']
        binsize = config['run']['bin']

        pr.print('Preallocating tables/files for output.', time=True)

        if not force and config['patterns']['save']:
            save = config['patterns']['pickle']
            
            if ConfigUtil.file_exists(save):
                cond = pr.print(f'Patterns tree pickle file "{save}" already '
                    'exists. Delete and continue? [Y/n] ', inquiry=True, 
                    time=True, force=True)
                if not cond:
                    raise UserExitError('User chose to terminate process.')

        self.create_tables(force)

        if config['patterns']['load']:
            load = config['patterns']['pickle']

            pr.print(f'Loading pickled patterns tree from "{load}".', time=True)
            self.fpgrowth = pickle.load(open(load, 'rb'))
            support = self.fpgrowth.support
            popsize = self.fpgrowth.tree.root.count
            items = [(key, val/popsize) for key, val in support.items()]

            trans = self.fpgrowth.tree.root.count
            events = sum(n.count for item in self.fpgrowth.tree.nodes.values()
                for n in item) - trans
            nodes = sum(len(item) for item in self.fpgrowth.tree.nodes.values())
            pr.print(f'Tree complete with {len(items)} items, {trans} transactions, '
                f'{events} events, and {nodes} nodes.', time=True)
            
            pr.print(f'Pushing support for {len(support)} items to '
                'database.', time=True)
            self.database.write_rows(items, 'items')
        
        else:
            size = config['population']['size']
            seed = config['population']['seed']

            pr.print(f'Generating sample population of size {size},', time=True)
            population = self.generate_population(size, seed)
            popsize = len(population)

            min_support = config['items']['min_support']
            max_support = config['items']['max_support']
            source = config['items']['source']

            pr.print('First data scan; calculating support for '
                'population transactions.', time=True)
            support = self.calculate_support(population, source, min_support,
                max_support, binsize)

            pr.print('Second data scan; building frequent patterns tree.', time=True)
            self.fpgrowth = Fpgrowth(support)
            self.build_tree(population, source, binsize)

            items = len(self.fpgrowth.support)
            trans = self.fpgrowth.tree.root.count
            events = sum(n.count for item in self.fpgrowth.tree.nodes.values()
                for n in item) - trans
            nodes = sum(len(item) for item in self.fpgrowth.tree.nodes.values())
            pr.print(f'Tree complete with {items} items, {trans} transactions, '
                f'{events} events, and {nodes} nodes.', time=True)
            

        if config['patterns']['save']:
            save = config['patterns']['pickle']

            pr.print(f'Saving pickled patterns tree to {save}.', time=True)
            pickle.dump(self.fpgrowth, open(save, 'wb'))

        min_support = config['patterns']['min_support']
        max_support = config['patterns']['max_support']
        max_size = config['patterns']['max_size']

        pr.print('Beginning reading frequent patterns from tree.', time=True)
        patterns = self.find_patterns(min_support, max_support, max_size)
        del self.fpgrowth

        pr.print('Analyzing patterns for significant associations.', time=True)
        conditions = config['associations']
        associations = self.find_associations(patterns, conditions, popsize)
        del patterns

        pr.print('Pushing associations to database.', time=True)
        self.database.write_rows(associations, 'associations')
        del associations

        index = config['run']['index']
        if index:
            pr.print('Creating indexes on all new tables.', time=True)
            for table in self.database.tables.keys():
                self.database.create_all_idxs(table)

        pr.print('Assoication model run complete.', time=True)

        
    def generate_population(self, size, seed=None):
        population = self.database.fetch_population(size, seed=seed)
        popsize = len(population)
        if size > popsize:
            pr.print(f'Requested population size of {size} but only '
                f'found a max of {size} admissions.', time=True)
        return population


    def create_tables(self, force=False):
        if not force:
            exists = self.database.table_exists(*list(self.database.tables.keys()))
            tables = '", "'.join(exists)
            if len(exists):
                cond = pr.print(f'Tables "{tables}" already exist in database '
                    f'"{self.database.db}". Drop and continue? [Y/n] ', 
                    inquiry=True, time=True, force=True)
                if not cond:
                    raise UserExitError('User chose to terminate process.')
        for table in self.database.tables.keys():
            self.database.create_table(table)
        

    def calculate_support(self, population, source, min_support, max_support, binsize):
        popsize = len(population)
        min_support = int(min_support * popsize)
        max_support = int(max_support * popsize)

        support = defaultdict(int)
        for subpop in self.chunk(population, binsize):
            subjects, admissions = list(map(list, zip(*subpop)))

            pr.print(f'Fetching events for {len(subpop)} transactions.', time=True)
            events = self.database.fetch_events(source, subjects, admissions)

            pr.print(f'Calculating and merging support for {len(events)} '
                'events.', time=True)
            items = set()
            hadmid = 0
            count = 0
            for event in events:
                if event[0] != hadmid:
                    hadmid = event[0]
                    for item in items:
                        support[item] += 1
                    items = set()
                    count += 1
                items.add(event[1])
            del events

        items = [(key, val/popsize) for key, val in support.items()
            if val >= min_support and val <= max_support]
        support = {key: val for key, val in support.items()
            if val >= min_support and val <= max_support}

        pr.print(f'Found {len(items)} items in target population.', time=True)
        pr.print(f'Pushing support for {len(items)} items to database.', time=True)
        self.database.write_rows(items, 'items')

        return support

        
    def build_tree(self, population, source, bin_size):
        for subpopulation in self.chunk(population, bin_size):
            pr.print(f'Fetching events for {len(subpopulation)}'
                ' transactions.', time=True)

            subjects, admissions = list(map(list, zip(*subpopulation)))
            events = self.database.fetch_events(source, subjects, admissions)

            pr.print(f'Retrieved {len(events)} events; appending them'
                ' to the tree.', time=True)
            
            transactions = []
            items = set()
            hadmid = 0
            for event in events:
                if event[0] != hadmid:
                    hadmid = event[0]
                    if len(items):
                        transactions.append(items)
                    items = set()
                items.add(event[1])
            del events

            matrix, items = Fpgrowth.matrix(transactions)
            del transactions

            self.fpgrowth.build_tree(matrix, items)
            del matrix
            del items


    def find_patterns(self, min_support, max_support, maz_size):
        min_support = int(min_support * self.fpgrowth.tree.root.count)
        max_support = int(max_support * self.fpgrowth.tree.root.count)

        patterns = []
        generator = self.fpgrowth.find_patterns(self.fpgrowth.tree, 
            min_support, max_support, maz_size)

        count, n = 0, 1
        for pattern in generator:
            patterns.append(pattern)
            count += 1
            if count == n:
                pr.print(f'Found pattern {count}.', time=True)
                n = n << 1

        if count != n >> 1:
            pr.print(f'Found pattern {count}.', time=True)

        return patterns


    def find_associations(self, patterns, conds, popsize):
        inf = float('inf')
        metrics = {
            'support':    lambda sAC, sA, sC: sAC,
            'confidence': lambda sAC, sA, sC: sAC/sA,
            'lift':       lambda sAC, sA, sC: sAC/sA/sC,
            'leverage':   lambda sAC, sA, sC: sAC-sA*sC,
            'conviction': lambda sAC, sA, sC: (1-sC)/(1-sAC/sA) if sAC != sA else inf,
            'rpf':        lambda sAC, sA, sC: sAC*sAC/sA
        }

        pattern_dict = {frozenset(p[1]): p[0] / popsize for p in patterns}
        associations = []
        count, n = 0, 1

        for pattern in pattern_dict.keys():
            sAC = pattern_dict[pattern]
            for idx in range(len(pattern)-1,0,-1):
                for subset in combinations(pattern, r=idx):
                    antecedent = frozenset(subset)
                    consequent = pattern - antecedent

                    sA = pattern_dict[antecedent]
                    sC = pattern_dict[consequent]

                    score = all(metrics[metric](sAC, sA, sC) >= cond 
                        for metric, cond in conds.items())

                    if score:
                        associations.append((
                            count,
                            ','.join(sorted(antecedent)),
                            ','.join(sorted(consequent)),
                            metrics['support'](sAC, sA, sC),
                            metrics['confidence'](sAC, sA, sC),
                            metrics['lift'](sAC, sA, sC),
                            metrics['leverage'](sAC, sA, sC),
                            metrics['conviction'](sAC, sA, sC) if sAC != sA else None,
                            metrics['rpf'](sAC, sA, sC)))
                        count += 1

                        if count == n:
                            pr.print(f'Found association {count}.', time=True)
                            n = n << 1

        if count != n >> 1:
            pr.print(f'Found association {count}.', time=True)

        return associations
