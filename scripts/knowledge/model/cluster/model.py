
import pickle
import logging as log

from sklearn.cluster import KMeans
from knowledge.util.config import ConfigUtil
from knowledge.util.filesys import FilesysUtil

try:
    from knowledge.struct.population import Population
    mysql = True
except ImportError:
    mysql = False


class ClusterModel:
    def __init__(self, database=None):
        pass


    @staticmethod
    def mysql():
        return mysql


    @staticmethod
    def validate_config(configpath, specspath):
        'validates a configuration file for the cluster model'

        config = ConfigUtil.load_config(configpath)
        specs = ConfigUtil.load_specs(specspath)
        config = ConfigUtil.verify_config(specs, config)

        return config


    def run(self, config):
        'runs the cluster model with specified configuration'

        concepts = []

        # 

        KMeans()

        

    
    def create_indexes(self, config):
        'create inexes on created mysql tables'


