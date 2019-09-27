
from knowledge.util.print import PrintUtil as pr
from knowledge.model.densematrix.database import DensematrixDatabaseUtil

class DensematrixModel:
    def __init__(self, database):
        self.database = DensematrixDatabaseUtil(database)

    @staticmethod
    def validate_config(config):
        pass

    def build_matrix(self, config):
        self.validate_config(config)