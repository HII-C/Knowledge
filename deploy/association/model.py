
import pickle
import csv
import sys
import json

from collections import defaultdict
from itertools import combinations
from argparse import ArgumentParser

from association.fpgrowth import Fpgrowth
from association.config import ConfigUtil
from association.error import ConfigError, UserExitError
from association.print import PrintUtil as pr

class AssociationModel:
    def __init__(self):
        self.fpgrowth = None

    @staticmethod
    def chunk(arr, n):
        for i in range(0, len(arr), n):
            yield arr[i: i+n]

    @staticmethod
    def validate_config(filepath):
        'validates a configuration file for the association model'

        config = ConfigUtil.load_config(filepath)
        specs = ConfigUtil.load_specs('specs.json')
        config = ConfigUtil.verify_config(specs, config)

        patterns = config['patterns']
        if patterns['pickle'] is None:
            raise ConfigError('Pickled tree path must be given to'
                'load pickled tree.')
        if not ConfigUtil.file_readable(patterns['pickle']):
            raise FileNotFoundError('Pickled tree path must be a '
                'path to a readable file.')

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

        force = config['run']['force']
        count = config['run']['count']
        assoc_file = config['run']['associations_file']
        items_file = config['run']['items_file']

        pr.print('Preallocating tables/files for output.', time=True)

        if not force and ConfigUtil.file_exists(assoc_file):
            cond = pr.print(f'Associations csv file "{assoc_file}" already '
                'exists. Delete and continue? [Y/n] ', inquiry=True, 
                time=True, force=True)
            if not cond:
                raise UserExitError('User chose to terminate process.')

        if not force and ConfigUtil.file_exists(items_file):
            cond = pr.print(f'Associations csv file "{items_file}" already '
                'exists. Delete and continue? [Y/n] ', inquiry=True, 
                time=True, force=True)
            if not cond:
                raise UserExitError('User chose to terminate process.')

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
        
        if count is not None:
            pr.print(f'Writing support for {len(support)} items to '
                'csv file.', time=True)
            with open(items_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                writer.writerows(items)

        min_support = config['patterns']['min_support']
        max_support = config['patterns']['max_support']
        max_size = config['patterns']['max_size']

        pr.print('Beginning reading frequent patterns from tree.', time=True)
        patterns = self.find_patterns(min_support, max_support, max_size, 
            count_only=(count == 'patterns'))
        del self.fpgrowth

        pr.print('Analyzing patterns for significant associations.', time=True)
        conditions = config['associations']
        self.find_associations(patterns, conditions, popsize, assoc_file,
            count_only=(count == 'associations'))
        del patterns

        pr.print('Assoication model run complete.', time=True)


    def find_patterns(self, min_support, max_support, max_size, count_only=False):
        min_support = int(min_support * self.fpgrowth.tree.root.count)
        max_support = int(max_support * self.fpgrowth.tree.root.count)

        patterns = []
        generator = self.fpgrowth.find_patterns(self.fpgrowth.tree, 
            min_support, max_support, max_size)

        count, n = 0, 1
        for pattern in generator:
            if count_only:
                count += 1
                continue
            patterns.append(pattern)
            count += 1
            if count == n:
                pr.print(f'Found pattern {count}.', time=True)
                n = n << 1

        if count != n >> 1:
            pr.print(f'Found pattern {count}.', time=True)

        return patterns


    def find_associations(self, patterns, conds, popsize, 
            assoc_file, count_only=False):
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

        csvfile = open(assoc_file, 'w', newline='')
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

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

                    if score and count_only:
                        count += 1
                        continue

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
                        if count % 100000 == 0:
                            writer.writerows(associations)
                            assoc_file.flush()
                            associations = []                    

        if count != n >> 1:
            pr.print(f'Found association {count}.', time=True)
        writer.writerows(associations)
        assoc_file.close()


# main runner

if __name__ == '__main__':
    sys.setrecursionlimit(10000)

    parser = ArgumentParser(prog='association model runner',
        description='run an association building model')
    parser.add_argument('--config', type=str, dest='config',
        default='config.json',
        help=('specify a config file location; default is "config.json" in '
            'this this module\'s build directory'))
    parser.add_argument('--log', type=str, dest='log', default=None,
        help='specify a log file location; by default the log will not be saved')
    args = parser.parse_args()

    config = AssociationModel.validate_config(args.config)

    if config['run']['silent']:
        pr.silence()

    if args.log is not None:
        pr.log(args.log)
    elif config['run']['log'] is not None:
        pr.log(config['run']['log'])

    model = AssociationModel()
    model.run(config)
