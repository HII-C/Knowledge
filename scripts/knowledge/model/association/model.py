
import psutil
import pickle

from collections import defaultdict

from knowledge.model.association.database import AssociationDatabase
from knowledge.struct.fpgrowth import Fpgrowth
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

        required = ('min_support', 'min_confidence', 'population', )
        types = (float, float, int)

        for param, kind in zip(required, types):
            if param not in config:
                raise ConfigError(f'Paramter "{param}" is required.')
            elif config[param] is None:
                raise ConfigError(f'Paramter "{param}" is required.')
            if type(config[param]) is not kind:
                raise TypeError(f'Parameter "{param}" expected to be of type "'
                    f'{kind.__name__}" but found "{type(config[param]).__name__}".')

        if config['min_support'] < 0:
            raise ValueError('Parameter "min_support" must be n >= 0.')
        if config['min_confidence'] < 0:
            raise ValueError('Parameter "min_confidence" must be n >= 0.')

        optional = ('silent', 'create_idxs', 'force', 'bin_size')
        types = (bool, bool, bool, int)
        defaults = (False, True, False, 100)

        for param, kind, default in zip(optional, types, defaults):
            if param not in config:
                config[param] = default
            elif config[param] is None:
                config[param] = default
            elif type(config[param]) is not kind:
                raise TypeError(f'Parameter "{param}" expected to be of type "'
                    f'{kind.__name__}" but found "{type(config[param]).__name__}".')

        if config['bin_size'] <= 0:
            raise ValueError('Parameter "bin_size" must be n > 0.')

        return config


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

        silent = silent if silent is not None else config['silent']

        if config['cached_support'] not in ('', None):
            del self.database.tables[config['cached_support']]

        if config['tree_load_path'] not in ('', None):
            if not silent:
                pr.print('Loading and unpickling tree from '
                    f'{config["tree_load_path"]}.', time=True)
            self.fpgrowth = pickle.load(open(config['tree_load_path'], 'rb'))

        else:
            if not silent:
                pr.print('Defining tables to be populated.', time=True)
            self.create_tables(config['force'], silent)

            if not silent:
                pr.print(f'Generating population of {config["population"]} '
                    'patients.', time=True)
            population = self.generate_population(config['population'], 
                config['seed'], silent)

            if config['cached_support'] not in ('', None):
                if not silent:
                    pr.print(f'Calculating itemset support for patient '
                        'transactions.', time=True)
                support = self.database.fetch_support(config['cached_support'])
                
            else:
                if not silent:
                    pr.print(f'Fetching cahced itemset support for patient '
                        'transactions.', time=True)
                support = self.calculate_support(population, config['bin_size'], 
                    silent)

            if not silent:
                pr.print('Starting frequent patterns tree building.', time=True)
            self.fpgrowth = Fpgrowth(support)
            self.build_tree(population, config['bin_size'], silent)

        if config['tree_save_path'] not in ('', None):
            if not silent:
                pr.print('Pickling and saving tree to '
                    f'{config["tree_save_path"]}.', time=True)
            pickle.dump(self.fpgrowth, open(config['tree_save_path'], 'wb'))

        if not silent:
            pr.print('Beginning reading frequent patterns from tree.', time=True)

        min_support = int(config['min_support'] * self.fpgrowth.tree.root.count)
        patterns = self.fpgrowth.find_patterns(min_support, config['max_size'])
        for pattern in patterns:
            pass

        
    def generate_population(self, pop_size, seed=None, silent=False):
        return self.database.fetch_population(pop_size, seed=seed)


    def create_tables(self, force=False, silent=False):
        if not force:
            exists = self.database.table_exists(*list(self.database.tables.keys()))
            tables = '", "'.join(exists)
            if len(exists):
                term = pr.print(f'Tables "{tables}" already exist in database '
                    f'"{self.database.db}". Drop and continue? [Y/n] ', 
                    inquiry=True, time=True)
                if not term:
                    raise UserExitError('User chose to terminate process.')
        for table in self.database.tables.keys():
            self.database.create_table(table)
        

    def calculate_support(self, population, bin_size, silent=False):
        support = defaultdict(int)

        for subpopulation in self.chunk(population, bin_size):
            subjects, admissions = list(map(list, zip(*subpopulation)))

            if not silent:
                pr.print(f'Fetching events for {len(subpopulation)}'
                    ' transactions.', time=True)

            events = self.database.fetch_events(subjects, admissions)

            if not silent:
                pr.print(f'Calculating and merging support for {len(events)}'
                    ' events.', time=True)

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

        items = [(key, val/len(population)) for key, val in support.items()]

        if not silent:
            pr.print(f'Found {len(items)} items in target population.', time=True)
            pr.print(f'Pushing support for {len(support)} items to '
                'database.', time=True)

        self.database.write_rows(items, 'support')

        return support

        
    def build_tree(self, population, bin_size, silent=False):
        for subpopulation in self.chunk(population, bin_size):
            if not silent:
                pr.print(f'Fetching events for {len(subpopulation)}'
                    ' transactions.', time=True)

            subjects, admissions = list(map(list, zip(*subpopulation)))
            events = self.database.fetch_events(subjects, admissions)

            if not silent:
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

            self.fpgrowth.build_tree(matrix, items, silent)
            del matrix
            del items

            if not silent:
                mem = psutil.virtual_memory().percent
                size = sum(len(n) for n in self.fpgrowth.tree.nodes.values())
                pr.print(f'Nodes in tree: {size}.', time=True)
                pr.print(f'Memory usage: {mem}%.', time=True)

    def find_associations(self, min_confidence):
        pass
    

    

