import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


from models.core.config import Config
from models.core.patient_population import PatientPopulation


class Model:
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

    def load_patients(self, pickle_base='models/data/patients/static'):
        self.x = pd.DataFrame.from_pickle(f'{pickle_base}_x.pickle')
        self.y = pd.Series.from_pickle(f'{pickle_base}_y.pickle')

    def dump_patients(self, pickle_base='models/data/patients/static'):
        self.x.to_pickle(f'{pickle_base}_x.pickle')
        self.y.to_pickle(f'{pickle_base}_y.pickle')

    def split_patients(self, test_size=.5, random_state=42):
        x_train, x_test, y_train, y_test = train_test_split(
            self.x, self.y, test_size=test_size, random_state=random_state)
