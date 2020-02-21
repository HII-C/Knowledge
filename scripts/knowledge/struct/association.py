
import pickle
import gzip
import csv
import os
import logging as log

from itertools import combinations
from multiprocessing import Pool, Manager, Value
from ctypes import c_uint64

from knowledge.struct.fpgrowth import Fpgrowth
from knowledge.util.filesys import FilesysUtil


count = None
n = None


def multiopen(filepath, **kwargs):
    'autodetect compressed file'

    if filepath.split('.')[-1] == 'gz':
        data = gzip.open(filepath, **kwargs)
    else:
        data = open(filepath, **kwargs)
    return data


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def write_associations(queue, filepath, cols):
    '''asynchronous queued association csv write

    Parameters
    ----------
    queue: multiprocessing.Queue
        File write queue as provided by the multiprocessing manager.

    csv: str
        String for the filepath to write associations.

    cols: list[str]
        List of column names for csv output.    '''
    
    log.debug(f'Launching association writer on process {os.getpid()}.')
    csvfile = multiopen(filepath, mode='w', newline='')
    csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"')
    csvwriter.writerow(cols)

    request = queue.get()
    while request != 'kill':
        log.debug('Writing associations.')
        csvwriter.writerows(request)
        csvfile.flush()
        request = queue.get()
    csvfile.close()
    log.debug(f'Associations writer finished.')


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

    min_confidence: float   '''

    log.debug(f'Association mining proccess {os.getpid()} starting.')
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
    log.debug(f'Association mining proccess {os.getpid()} finished.')


class Association:
    def __init__(self, patterns):
        self.patterns = patterns


    def get_association(self, consequent, antecedent):
        'get a specific association from patterns'
        
        pass


    def find_associations(self, filepath, min_support=0, min_confidence=0, 
            cores=None):
        'find associations from frequent patterns dictionary'

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
        pool.apply_async(write_associations, (queue, filepath, cols))

        chunksize = max(len(self.patterns) // (cores * 4), 1)
        data = lambda: self.patterns
        jobs = chunks(list(self.patterns.keys()), chunksize)
        tasks = ((queue, self.patterns, keys, min_support, min_confidence) 
            for keys in jobs)

        log.info(f'Finding associations on {cores} cores.')
        pool.starmap(find_associations, tasks)
        queue.put('kill')
        pool.close()
        pool.join()

        if count.value != n.value >> 1:
            log.info(f'Found association {count.value}.')
        