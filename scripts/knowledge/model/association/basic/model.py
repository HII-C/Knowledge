
import gzip
import pickle
import logging as log

from enum import IntEnum
from typing import Dict

from knowledge.struct.association import Association
from knowledge.struct.fpgrowth import Fpgrowth
from knowledge.struct.transaction import Transaction
from knowledge.struct.dimension import Dimension
from knowledge.util.config import ConfigUtil
from knowledge.util.filesys import FilesysUtil


def mulitopen(filepath, **kwargs):
    'autodetect compressed file'

    if filepath.split('.')[-1] == 'gz':
        data = gzip.open(filepath, **kwargs)
    else:
        data = open(filepath, **kwargs)
    return data


class Activity(IntEnum):
    TRANSACTIONS = 0
    TREE = 1
    PATTERNS = 2
    ASSOCIATIONS = 3
    
    @classmethod
    def decode(self, string):
        return getattr(self, string.upper())


class BasicAssociationModel:
    def __init__(self, config):
        self.config = config


    @classmethod
    def configure(self, config_file, specs_file, validate=True):
        config = ConfigUtil.load_config(config_file)
        specs = ConfigUtil.load_specs(specs_file)

        if validate:
            config = self.validate(config)

        return ConfigUtil.verify_config(specs, config)


    @classmethod
    def validate(self, config):
        warn = 0
        fail = 0

        source = Activity.decode(config['run']['source'])
        goal = Activity.decode(config['run']['goal'])
        load = config[source.name.lower()]['file']
        save = config[goal.name.lower()]['file']

        if source > goal:
            fail += 1
            log.error(f'Does not make sense to try to find/make {goal.name.lower()} '
                f'from {source.name.lower()}; consider swapping goal and source.')
        elif source == goal:
            warn += 1
            log.error(f'Does not make sense to have source and goal be '
                'the same; nothing will be done.')

        if load is None:
            fail += 1
            log.error(f'Property "file" needs to defined on source concpet ('
                f'{source.name.lower()}) so data can be loaded.')
        if save is None:
            fail += 1
            log.error(f'Property "file" needs to defined on goal concpet ('
                f'{goal.name.lower()}) so data can be saved.')
        
        for act in Activity:
            if act > source and act < goal:
                name = act.name.lower()
                if config[name]['save']:
                    if FilesysUtil.file_exists(config[name]['file']):
                        warn += 1
                        log.warning(f'The file specified to save {name} '
                            'already exists; it will be overwritten if model is run.')
                        log.warning(config[name]["file"])

        # TODO: more error handling

        if fail:
            log.error(f'{fail} critical and {warn} potential issues found in model '
                'configuration (see above errors). Check config file and rerun.')
            raise ValueError

        if warn:
            log.warning(f'{warn} potential issues found in model configuration '
                '(see above warnings). Would you like to continue model run? [Y/n]')
            if not input().lower() in (1, 'y', 'yes', 'yeet'):
                log.error('User chose to terminate process.')
                raise RuntimeError

        return config


    def run(self):
        source = Activity.decode(self.config['run']['source'])
        goal = Activity.decode(self.config['run']['goal'])

        support: Dict[str, int] = None
        fpgrowth: Fpgrowth = None
        patterns: Dict[frozenset, int] = None
        association: Association = None

        if source == Activity.TRANSACTIONS:
            filepath = self.config['transactions']['file']
            log.info(f'Loading transactions from {filepath}.')
            log.info('First transaction data scan; calculating support.')
            support = Fpgrowth.calculate_support(filepath)
            fpgrowth = Fpgrowth(support)
            log.info('Second transaction data scan; building frequent pattern tree.')
            fpgrowth.load_transactions(filepath)
        
        if source == Activity.TREE:
            filepath = self.config['tree']['file']
            log.info(f'Loading frequent patterns tree from {filepath}.')
            data = mulitopen(filepath, mode='rb')
            fpgrowth = pickle.load(data)
            data.close()

        if source <= Activity.TREE:
            items = len(fpgrowth.support)
            trans = fpgrowth.tree.root.count
            events = sum(n.count for item in fpgrowth.tree.nodes.values()
                for n in item) - trans
            nodes = sum(len(item) for item in fpgrowth.tree.nodes.values())
            log.info(f'Tree loaded with {items} items, {trans} encounters, '
                f'{events} events, and {nodes} nodes.')

        if source < Activity.TREE and goal >= Activity.TREE:
            if self.config['tree']['save']:
                log.info(f'Saving frequent patterns tree to {filepath}.')
                filepath = self.config['tree']['file']
                data = mulitopen(filepath, mode='wb')
                pickle.dump(fpgrowth, data)
                data.close()

        if source == Activity.PATTERNS:
            filepath = self.config['patterns']['file']
            log.info(f'Loading patterns from {filepath}.')
            patterns = Fpgrowth.load_patterns(filepath)

        if source < Activity.PATTERNS and goal >= Activity.PATTERNS:
            patterns = fpgrowth.find_patterns(
                min_support=self.config['patterns']['min_support'],
                max_support=self.config['patterns']['max_support'],
                max_size=self.config['patterns']['max_size'],
                cores=self.config['run']['cores'])
            if self.config['patterns']['save']:
                filepath = self.config['patterns']['file']
                log.info(f'Saving patterns to {filepath}.')
                Fpgrowth.write_patterns(patterns, filepath)

        if goal == Activity.ASSOCIATIONS:
            filepath = self.config['associations']['file']
            log.info(f'Finding associations and dumping into {filepath}.')
            association = Association(patterns)
            association.find_associations(filepath,
                min_support=self.config['associations']['min_support'],
                min_confidence=self.config['associations']['min_confidence'],
                cores=self.config['run']['cores'])
            
