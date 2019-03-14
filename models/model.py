import pandas as pd
import numpy as np


from models.patient_population import PatientPopulation
from models.config import Config


class Model:
    # Object holding the instance of random patient ID's being used
    config: Config = None
    x: pd.DataFrame = None
    y: pd.Series = None

    def __init__(self, config_file):
        self.config = Config()
        self.config.load(config_file)

    def retrieve_patients(self):
        self.config.get_patients()
        print(f'''Retrieved {self.config.patients.patient_count} patients
                with LHS ConceptType = {self.config.params["lefthand_side"]["concept"]},
                RHS ConceptType = {self.config.params["righthand_side"]["concept"]},
                Evaluation = {self.config.params["righthand_side"]["evaluation"]},
                and Logic = {self.config.params["righthand_side"]["logic"]}''')
        self.x = self.config.lhs
        self.y = self.config.rhs

    def split_patients(self, train_test_split=.5):
        pass
