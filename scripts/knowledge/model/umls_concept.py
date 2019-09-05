
import json
import xgboost as xgb
import numpy as np

from pkg_resources import resource_filename
from argparse import ArgumentParser

from knowledge.model.umls_concept import UmlsConceptDatabase
from knowledge.util.print import PrintUtil as pr


class UmlsConceptModel:
    def __init__(self, database=None):
        self.database = UmlsConceptDatabase(database)

    @staticmethod
    def validate_config(config):
        pass

    def run(self, config=None, silent=False):
        pass

    def fetch_population(self, agents=None, size=None, silent=False):
        pass

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
        default=resource_filename('knowledge', 'model/concept_util_config.json'))
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