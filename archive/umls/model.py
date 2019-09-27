
import json
import xgboost as xgb
import numpy as np

from pkg_resources import resource_filename
from argparse import ArgumentParser

from knowledge.model.umls.database import UmlsConceptDatabase
from knowledge.util.print import PrintUtil as pr


class UmlsConceptModel:
    def __init__(self, database=None):
        self.database = UmlsConceptDatabase(database)

    @staticmethod
    def default_config():
        configpath = resource_filename('knowledge', 'model/umls/config.json')
        with open(configpath, 'r') as configfile:
            config = json.load(configfile)
        return config

    @classmethod
    def merge_config(self, primary, default):
        pass

    @classmethod
    def validate_config(self, config):
        return True

    def run(self, config=None, silent=False):
        self.fetch_population(size=config['population_size'], silent=silent)
        self.fetch_concepts(concepts=config['concepts'], silent=silent)
        self.train_model(silent=silent)
        self.test_model(silent=silent)
        if config['save_model']:
            self.save_model(config['model_path'])
        if config['save_results']:
            self.save_results(config['result_path'])

    def fetch_population(self, agents=None, size=None, silent=False):
        if not silent:
            pr.print('Fetching model population.')

        

    def fetch_concepts(self, concepts=None, silent=False):
        pass

    def train_model(self, silent=False):
        pass

    def test_model(self, silent=False):
        pass

    def save_model(self, savepath, silent=False):
        pass

    def save_results(self, savepath, silent=False):
        pass
    
if __name__ == '__main__':
    parser = ArgumentParser(prog='UmlsConceptModel',
        description='model used to build an association between a set of UMLS '
            'concepts and a target UMLS concept')
    parser.add_argument('--config', type=str, dest='config',
        help='specify a config file location; default is the "umls_concept_config'
            '.json" file found in this module',
        default=resource_filename('knowledge', 'model/umls/config.json'))
    parser.add_argument('--log', type=str, dest='log',
        help='specify a log file location; by default the log will not be saved',
        default=None)
    args = parser.parse_args()

    if args.log is not None:
        pr.log(args.log)

    with open(args.config) as configfile:
        config = json.load(configfile)

    if UmlsConceptModel.validate_config(config):
        model = UmlsConceptModel(database=config['database'])
        model.run(config=config)
    else:
        raise Exception('passed config file is invalid; check syntax')