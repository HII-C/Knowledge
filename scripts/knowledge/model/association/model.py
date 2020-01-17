
import pickle
import logging as log

from csv import writer
from itertools import combinations
from multiprocessing import Pool, Manager, Value
from ctypes import c_uint64

from knowledge.struct.fpgrowth import Fpgrowth
from knowledge.util.config import ConfigUtil
from knowledge.util.filesys import FilesysUtil

try:
    from knowledge.struct.population import Population
    mysql = True
except ImportError:
    mysql = False


# globals for multiprocessing
count = None
n = None


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def write_associations(queue, csv, cols):
    '''asynchronous queued association csv write

    Parameters
    ----------
    queue: multiprocessing.Queue
        File write queue as provided by the multiprocessing manager.

    csv: str
        String for the filepath to write associations.

    cols: list[str]
        List of column names for csv output.
    '''
    csvfile = open(csv, 'w', newline='')
    csvwriter = writer(csvfile, delimiter=',', quotechar='"')
    csvwriter.writerow(cols)

    request = queue.get()
    while request != 'kill':
        csvwriter.writerows(request)
        csvfile.flush()
        request = queue.get()
    csvfile.close()


def find_associations(queue, patterns, keys, min_support, min_confidence):
    '''find associations in pattern chucnk and add to write queue

    Parameters
    ----------
    queue: multiprocessing.Queue
        File write queue as provided by the multiprocessing manager.

    patterns: dict{frozenset[str]: float}
        Dictionary of frequent patterns where a frozenset of items map
        to their corresponding support.

    keys: list[frozenset[str]]
        List of frozensets that are keys to the patterns dictionary;
        these patterns will be analyzed for association finding.

    min_support: float

    min_confidence: float

    '''
    inf = float('inf')
    metrics = {
        'support':    lambda sAC, sA, sC: sAC,
        'confidence': lambda sAC, sA, sC: sAC/sA,
        'lift':       lambda sAC, sA, sC: sAC/sA/sC,
        'leverage':   lambda sAC, sA, sC: sAC-sA*sC,
        'rpf':        lambda sAC, sA, sC: sAC*sAC/sA,
        'conviction': lambda sAC, sA, sC: (1-sC)/(1-sAC/sA) \
            if sAC != sA else inf   }
    
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
                        log.info(f'Found association {count.value}.')
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


class AssociationModel:
    def __init__(self, database=None):
        if mysql and database is not None:
            self.population = Population(database)
            self.database = self.population.database
        self.fpgrowth = None


    @staticmethod
    def mysql():
        return mysql

    
    @staticmethod
    def validate_config(configpath, specspath):
        'validates a configuration file for the association model'
        config = ConfigUtil.load_config(configpath)
        specs = ConfigUtil.load_specs(specspath)
        config = ConfigUtil.verify_config(specs, config)

        tree = config['tree']
        association = config['associations']
        run = config['run']

        warn = False

        if tree['load'] and tree['save']:
            log.error('Does not make sense to both load and save tree.')
            warn = True
        if tree['load']:
            if tree['pickle'] is None:
                log.error('Pickled tree path must be given to '
                    'load pickled tree.')
                raise FileNotFoundError
            if not FilesysUtil.file_readable(tree['pickle']):
                log.error('Pickled tree path must be a path to '
                    'a readable file.')
                raise FileNotFoundError
        if tree['save']:
            if tree['pickle'] is None:
                log.error('Pickled tree path must be given to '
                    'save pickled tree.')
                raise FileNotFoundError
            if not FilesysUtil.file_writable(tree['pickle']):
                log.error('Pickled tree path must be a '
                    'path to a writable file.')
                raise FileNotFoundError

        if association['load'] and association['save']:
            log.error('Does not make sense to both load and save associations.')
            warn = True
        if association['load'] and not association['mysql']:
            log.error('Does not make sense to load associations without '
                'saving them to mysql database.')
            warn = True
        if association['load']:
            if association['csv'] is None:
                log.error('A csv path must be given to '
                    'save associations as csv.')
            if not FilesysUtil.file_readable(association['csv']):
                log.error('Association csv path must be a '
                    'path to a readable file.')
                raise FileNotFoundError
        if association['save'] :
            if association['csv'] is None:
                log.error('A csv path must be given to '
                    'save associations as csv.')
                raise FileNotFoundError
            if not FilesysUtil.file_writable(association['csv']):
                log.error('Association csv path must be a '
                    'path to a writable file.')
                raise FileNotFoundError

        if not mysql:
            if not tree['load']:
                log.error('No mysql detected; cannot generate population '
                    'without mysql environment.')
                raise RuntimeError
            if association['mysql']:
                log.error('No mysql detected; cannot save associations '
                    'without mysql environment.')
                log.debug('See "association.mysql" config parameter.')
                raise RuntimeError

        if run['goal'] == 'tree' and not tree['save']:
            log.warning('Goal is to generate tree but nothing is ever saved.')
            warn = True
        if run['goal'] == 'associations' and not association['mysql'] \
                and not association['save']:
            log.warning('Goal is to generate associations but nothing is ever saved.')
            warn = True

        if warn:
            log.warning('Continue given config validation warnings? [Y/n]')
            if input().lower() not in ('y', 'yes'):
                log.error('User chose to terminate process.')
                raise RuntimeError

        return config


    def run(self, config):
        '''runs the association model with specified configuration

        Parameters
        ----------
        config: dict
            A dictionary representation of the JSON config file.
            See documentation for specifications of the config file.
        '''

        force = config['run']['force']
        goal = config['run']['goal']

        log.info('Preallocating output tables/files.')
        if not force and config['tree']['save']:
            save = config['tree']['pickle']
            if FilesysUtil.file_exists(save):
                log.warning(f'Patterns tree pickle file "{save}" already '
                    'exists. Delete and continue? [Y/n]')
                if input().lower() not in ('y', 'yes'):
                    log.error('User chose to terminate process.')
                    raise RuntimeError
        if not force and config['associations']['save']:
            save = config['associations']['csv']
            if FilesysUtil.file_exists(save):
                log.warning(f'Association output file "{save}" already '
                    'exists. Delete and continue? [Y/n]')
                if input().lower() not in ('y', 'yes'):
                    log.error('User chose to terminate process.')
                    raise RuntimeError
        if mysql:
            if config['associations']['mysql']:
                self.create_tables(force)
            if not config['tree']['load']:
                self.population.create_tables(force)

        if config['tree']['load']:
            load = config['tree']['pickle']

            log.info(f'Loading pickled patterns tree from {load}.')
            self.fpgrowth = pickle.load(open(load, 'rb'))
            support = self.fpgrowth.support
            popsize = self.fpgrowth.tree.root.count
            items = [(key, val/popsize) for key, val in support.items()]

            trans = self.fpgrowth.tree.root.count
            events = sum(n.count for item in self.fpgrowth.tree.nodes.values()
                for n in item) - trans
            nodes = sum(len(item) for item in self.fpgrowth.tree.nodes.values())
            log.info(f'Tree complete with {len(items)} items, {trans} encounters, '
                f'{events} events, and {nodes} nodes.')
        
        else:
            size = config['population']['size']

            log.info(f'Generating sample population of size {size}.')
            self.generate_population(**config['population'])

            log.info('First data scan; calculating support for population items.')
            support = self.calculate_support(**config['items'])

            log.info('Second data scan; building frequent patterns tree.')
            self.fpgrowth = Fpgrowth(support)
            self.build_tree(config['items']['source'], config['run']['bin'])

            items = self.population.items
            trans = self.fpgrowth.tree.root.count
            events = sum(n.count for item in self.fpgrowth.tree.nodes.values()
                for n in item) - trans
            nodes = sum(len(item) for item in self.fpgrowth.tree.nodes.values())
            log.info(f'Tree complete with {items} items, {trans} encounters, '
                f'{events} events, and {nodes} nodes.')

        if config['tree']['save']:
            save = config['tree']['pickle']
            log.info(f'Saving pickled patterns tree to {save}.')
            pickle.dump(self.fpgrowth, open(save, 'wb'))

        if goal == 'tree':
            log.info('Model achieved goal to build tree.')
            return
            
        log.info('Beginning reading frequent patterns from tree.')
        patterns = self.find_patterns(**config['patterns'], 
            cores=config['run']['cores'])
        del self.fpgrowth

        if goal == 'patterns':
            log.info('Model achieved goal to find patterns.')
            return

        log.info('Analyzing patterns for significant associations.')
        self.find_associations(patterns, **config['associations'],
            cores=config['run']['cores'])
        del patterns

        if config['run']['index']:
            log.info('Creating indexes on all new tables.')
            for table in self.database.tables.keys():
                self.database.create_all_idxs(table)

        if goal == 'associations':
            log.info('Model achieved goal to find associations.')
            return

        
    def generate_population(self, source, size, rand=True, seed=None):
        self.population.generate_population(source, size=size, rand=rand, seed=seed)
        if size > self.population.encounters:
            log.warning(f'Requested population size of {size} but only found '
                f' {self.population.encounters} encounters.')


    def create_tables(self, force=False):
        if not force:
            exists = self.database.table_exists(*list(self.database.tables.keys()))
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
        

    def calculate_support(self, source, min_support, max_support):
        'calculate support for itemset; constrain itemset by support bounds'
        
        self.population.generate_items(source, min_support, max_support)
        items = self.population.fetch_items()

        support = {key: val for key, val in items}

        log.info(f'Found {self.population.items} items in target population '
            f'on support interval [{min_support}, {max_support}].')

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

            log.info(f'Fetching events for {lmt} encounters.')
            events = self.population.fetch_events(source, offset, bin_size)
            log.info(f'Retrieved {len(events)} events; inserting them'
                ' into the fpgrowth tree.')
            
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


    def find_patterns(self, min_support, max_support, max_size, cores=None):
        '''read patterns of of frequent patterns tree
        '''
        encounters = self.fpgrowth.tree.root.count
        min_support = int(min_support * encounters)
        max_support = int(max_support * encounters)

        patterns_array = self.fpgrowth.find_patterns(self.fpgrowth.tree, min_support, 
            max_support, max_size, cores)
        
        patterns_dict = {frozenset(p[1]): p[0] / encounters for p in patterns_array}

        return patterns_dict


    def find_associations(self, patterns, min_support=0, min_confidence=0,
            csv=None, save=False, cores=None):
        '''find associations from frequent patterns dictionary
        '''
        if csv is None:
            csvfile = FilesysUtil.create_tempfile(suffix='csv', delete=False)
            csv = csvfile.name
            csvfile.close()
            temp = True
        else:
            temp = False

        log.info(f'Balancing patterns into tasks for {cores} cores.')

        global count, n
        count = Value(c_uint64)
        count.value = 0
        n = Value(c_uint64)
        n.value = 1

        manager = Manager()
        queue = manager.Queue(maxsize=10)
        pool = Pool(processes=cores)

        cols = ('antecedent', 'consequent', 'support', 'confidence', 'lift',
            'leverage', 'conviction', 'rpf')
        pool.apply_async(write_associations, (queue, csv, cols))

        chunksize = len(patterns) // (cores * 4)
        tasks = [(queue, patterns, keys, min_support, min_confidence) for keys in 
            chunks(list(patterns.keys()), chunksize)]

        log.info(f'Finding associations and writing them to "{csv}".')
        pool.starmap(find_associations, tasks)
        queue.put('kill')
        pool.close()
        pool.join()

        if count.value != n.value >> 1:
            log.info(f'Found association {count.value}.')

        if mysql:
            log.info('Loading associations into mysql database.')
            self.load_associations(csv)

        if temp:
            log.info(f'Deleting temporary associations file "{csv}".')
            FilesysUtil.delete_file(csv)

        
    def load_associations(self, csv):
        query = 'ALTER TABLE associations DISABLE KEYS'
        self.database.cursor.execute(query)
        self.database.connection.commit()
        query = f'''
            LOAD DATA LOCAL INFILE {csv} INTO TABLE associations
            FIELDS 
                TERMINATED BY \',\'
                ESCAPED BY \'\\\' 
                OPTIONALLY ENCLOSED BY \'"\'
            LINES 
                TERMINATED BY \'\n\'
            IGNORE 1 LINES (
                @antecedent,
                @consequent,
                @support,
                @confidence,
                @lift,
                @leverage,
                @conviction,
                @rpf    )
            SET
                antecedent = @antecedent,
                consequent = @consequent,
                support = @support,
                confidence = @confidence,
                lift = @lift,
                leverage = @leverage,
                conviction = @conviction,
                rpf = @rpf  '''
        self.database.cursor.execute(query)
        self.database.connection.commit()
        query = 'ALTER TABLE associations ENABLE KEYS'
        self.database.cursor.execute(query)
        self.database.connection.commit()
        query = 'OPTIMIZE TABLE associations'
        self.database.cursor.execute(query)
        self.database.connection.commit()
        