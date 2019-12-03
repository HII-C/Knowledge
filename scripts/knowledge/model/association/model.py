
import psutil
import pickle

from csv import writer
from collections import defaultdict
from itertools import combinations
from pkg_resources import resource_filename
from multiprocessing import Pool, Manager, Value
from ctypes import c_uint64

from knowledge.struct.fpgrowth import Fpgrowth
from knowledge.util.config import ConfigUtil
from knowledge.util.error import ConfigError, UserExitError
from knowledge.util.print import PrintUtil as pr

try:
    from knowledge.struct.population import Population
    mysql = True
except:
    mysql = False


count = None
n = None


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def write_associations(queue, csv, cols):
    '''asynchronous queued association csv write
    '''
    csvfile = open(csv, 'w', newline='')
    csvwriter = writer(csvfile, delimiter=',', quotechar='"')
    csvwriter.writerow(cols)
    while True:
        request = queue.get()
        if request == 'kill':
            csvfile.close()
            break
        else:
            csvwriter.writerows(request)
            csvfile.flush()


def find_associations(queue, patterns, keys, min_support, min_confidence):
    '''find associations in pattern chucnk and add to write queue
    '''
    inf = float('inf')
    metrics = {
        'support':    lambda sAC, sA, sC: sAC,
        'confidence': lambda sAC, sA, sC: sAC/sA,
        'lift':       lambda sAC, sA, sC: sAC/sA/sC,
        'leverage':   lambda sAC, sA, sC: sAC-sA*sC,
        'conviction': lambda sAC, sA, sC: (1-sC)/(1-sAC/sA) if sAC != sA else inf,
        'rpf':        lambda sAC, sA, sC: sAC*sAC/sA    }
    
    associations = []
    local_count = 0
    for pattern in keys:
        sAC = patterns[pattern]
        for idx in range(len(pattern)-1,0,-1):
            for subset in combinations(pattern, r=idx):
                antecedent = frozenset(subset)
                consequent = pattern - antecedent

                sA = patterns[antecedent]
                sC = patterns[consequent]

                score = (metrics['support'](sAC, sA, sC) >= min_support and
                    metrics['confidence'](sAC, sA, sC) >= min_confidence)

                if score:
                    if count.value >= n.value:
                        pr.print(f'Found association {count.value}.', time=True)
                        with n.get_lock():
                            n.value <<= 1
                    
                    if local_count >= 100000:
                        queue.put(associations)
                        associations = []
                        local_count = 0 
                        
                    associations.append((
                        ','.join(sorted(antecedent)),
                        ','.join(sorted(consequent)),
                        metrics['support'](sAC, sA, sC),
                        metrics['confidence'](sAC, sA, sC),
                        metrics['lift'](sAC, sA, sC),
                        metrics['leverage'](sAC, sA, sC),
                        metrics['conviction'](sAC, sA, sC) if sAC != sA else None,
                        metrics['rpf'](sAC, sA, sC)))

                    local_count += 1
                    with count.get_lock():
                        count.value += 1

    queue.put(associations)
    associations = []


class AssociationModel:
    def __init__(self, database=None):
        if mysql and database is not None:
            self.population = Population(database)
            self.database = self.population.database
        self.fpgrowth = None
    

    @staticmethod
    def validate_config(configpath, specspath):
        '''validates a configuration file for the association model
        '''
        config = ConfigUtil.load_config(configpath)
        specs = ConfigUtil.load_specs(specspath)
        config = ConfigUtil.verify_config(specs, config)

        tree = config['tree']
        association = config['associations']        
        if tree['load']:
            if tree['pickle'] is None:
                raise ConfigError('Pickled tree path must be given to'
                    'load pickled tree.')
            if not ConfigUtil.file_readable(tree['pickle']):
                raise FileNotFoundError('Pickled tree path must be a '
                    'path to a readable file.')
        if tree['save']:
            if tree['pickle'] is None:
                raise ConfigError('Pickled tree path must be given to'
                    'save pickled tree.')
            if not ConfigUtil.file_writable(tree['pickle']):
                raise FileNotFoundError('Pickled tree path must be a '
                    'path to a writable file or directory.')
        if association['csv']:
            if not ConfigUtil.file_writable(association['csv']):
                raise FileNotFoundError('Association csv path must be a '
                    'path to a writable file or directory.')

        if not mysql and not tree['load']:
            raise ConfigError('No MySQL detected; cannot build tree without'
                'MySQL environment.')

        if (not mysql and association['csv'] is None 
                and not association['count_only']):
            raise ConfigError('No MySQL detected; must specify csv location '
                'to save associations instead of table.')

        return config


    def run(self, config, silent=None):
        '''runs the fpgrowth model with specified configurations
        Parameters
        ----------
        config: dict
            A dictionary representation of the JSON config file.
            See documentation for specifications of the config file.
        silent: bool


        Throws
        ------
        UserExitError
            When prompted, the user chose to exit rather than procede.
        '''

        force = config['run']['force']
        write = not (config['items']['count_only'] or
            config['patterns']['count_only'] or
            config['associations']['count_only'])

        if not write:
            del self.database.tables['items']
            del self.database.tables['associations']

        pr.print('Preallocating tables and files for output.', time=True)
        if not force and config['tree']['save']:
            save = config['tree']['pickle']
            if ConfigUtil.file_exists(save):
                cond = pr.print(f'Patterns tree pickle file "{save}" already '
                    'exists. Delete and continue? [Y/n] ', inquiry=True, 
                    time=True, force=True)
                if not cond:
                    raise UserExitError('User chose to terminate process.')

        if mysql:
            self.create_tables(force)
            if not config['tree']['load']:
                self.population.create_tables(force)

        if config['tree']['load']:
            load = config['tree']['pickle']

            pr.print(f'Loading pickled patterns tree from "{load}".', time=True)
            self.fpgrowth = pickle.load(open(load, 'rb'))
            support = self.fpgrowth.support
            popsize = self.fpgrowth.tree.root.count
            items = [(key, val/popsize) for key, val in support.items()]

            trans = self.fpgrowth.tree.root.count
            events = sum(n.count for item in self.fpgrowth.tree.nodes.values()
                for n in item) - trans
            nodes = sum(len(item) for item in self.fpgrowth.tree.nodes.values())
            pr.print(f'Tree complete with {len(items)} items, {trans} encounters, '
                f'{events} events, and {nodes} nodes.', time=True)
            
            # if write and mysql:
            #     pr.print(f'Pushing support for {len(support)} items to '
            #         'database.', time=True)
            #     self.database.write_rows(items, 'items')
        
        else:
            size = config['population']['size']

            pr.print(f'Generating sample population of size {size}.', time=True)
            self.generate_population(**config['population'])

            pr.print('First data scan; calculating support for '
                'population items.', time=True)
            support = self.calculate_support(**config['items'])

            pr.print('Second data scan; building frequent patterns tree.', time=True)
            self.fpgrowth = Fpgrowth(support)
            self.build_tree(config['items']['source'], config['run']['bin'])

            items = self.population.items
            trans = self.fpgrowth.tree.root.count
            events = sum(n.count for item in self.fpgrowth.tree.nodes.values()
                for n in item) - trans
            nodes = sum(len(item) for item in self.fpgrowth.tree.nodes.values())
            pr.print(f'Tree complete with {items} items, {trans} encounters, '
                f'{events} events, and {nodes} nodes.', time=True)

        if config['tree']['save']:
            save = config['tree']['pickle']
            pr.print(f'Saving pickled patterns tree to {save}.', time=True)
            pickle.dump(self.fpgrowth, open(save, 'wb'))
            
        pr.print('Beginning reading frequent patterns from tree.', time=True)
        patterns = self.find_patterns(**config['patterns'], 
            cores=config['run']['cores'])
        del self.fpgrowth

        if config['patterns']['count_only']:
            pr.print('Assoication model run complete.', time=True)
            return

        pr.print('Analyzing patterns for significant associations.', time=True)
        self.find_associations(patterns, **config['associations'])
        del patterns

        if config['associations']['count_only']:
            pr.print('Assoication model run complete.', time=True)
            return

        if config['run']['index']:
            pr.print('Creating indexes on all new tables.', time=True)
            for table in self.database.tables.keys():
                self.database.create_all_idxs(table)

        pr.print('Assoication model run complete.', time=True)

        
    def generate_population(self, source, size, rand=True, seed=None):
        self.population.generate_population(source, size=size, rand=rand, seed=seed)
        if size > self.population.encounters:
            pr.print(f'Requested population size of {size} but only found a max '
                f'of {self.population.encounters} encounters.', time=True)


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
        

    def calculate_support(self, source, min_support, max_support, count_only=False):
        '''calculate support for itemset; constrain itemset by support bounds
        '''
        self.population.generate_items(source, min_support, max_support)
        items = self.population.fetch_items()

        support = {key: val for key, val in items}

        pr.print(f'Found {self.population.items} items in target population '
            f'on support interval [{min_support}, {max_support}].', time=True)

        return support

        
    def build_tree(self, source, bin_size=100000):
        '''iteratively build frequent patterns tree

        Parameters
        ----------
        source: list[str]

        bin_size: int
        '''

        for offset in range(0, self.population.encounters, bin_size):
            lmt = min(bin_size, self.population.encounters)
            pr.print(f'Fetching events for {lmt} encounters.', time=True)

            events = self.population.fetch_events(source, offset, bin_size)

            pr.print(f'Retrieved {len(events)} events; inserting them'
                ' into the fpgrowth tree.', time=True)
            
            encounters = []
            items = set()
            hadmid = 0
            for event in events:
                if event[0] != hadmid:
                    hadmid = event[0]
                    if len(items):
                        encounters.append(items)
                    items = set()
                items.add(event[1])
            del events

            matrix, items = Fpgrowth.matrix(encounters)
            del encounters

            self.fpgrowth.build_tree(matrix, items)
            del matrix
            del items


    def find_patterns(self, min_support, max_support, max_size,
            count_only=False, cores=None):
        '''read patterns of of frequent patterns tree
        '''
        encounters = self.fpgrowth.tree.root.count
        min_support = int(min_support * encounters)
        max_support = int(max_support * encounters)

        patterns_array = self.fpgrowth.find_patterns(self.fpgrowth.tree, min_support, 
            max_support, max_size, cores)
        
        patterns_dict = {frozenset(p[1]): p[0] / encounters for p in patterns_array}

        return patterns_dict


    def find_associations(self, patterns, count_only=False, min_support=0,
            min_confidence=0, csv=None, save=False, cores=None):
        '''
        '''
        pr.print(f'Balancing patterns into tasks for {cores} cores.', time=True)
        manager = Manager()
        queue = manager.Queue(maxsize=10)
        pool = Pool(processes=cores)

        cols = ('antecedent', 'consequent', 'support', 'confidence', 'lift',
            'leverage', 'conviction', 'rpf')
        pool.apply_async(write_associations, (queue, csv, cols))

        global count, n
        count = Value(c_uint64)
        count.value = 0
        n = Value(c_uint64)
        n.value = 1
        chunksize = len(patterns) / cores / 4

        tasks = [(queue, patterns, keys, min_support, min_confidence) for keys in 
            chunks(patterns.keys(), chunksize)]

        pr.print(f'Finding associations on {cores} cores.', time=True)
        pool.starmap(find_associations, tasks)
        queue.put('kill')
        pool.close()
        pool.join()

        if count.value != n.value >> 1:
            pr.print(f'Found association {count.value}.', time=True)

        