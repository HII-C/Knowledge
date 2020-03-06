
import logging as log
import pandas as pd
import numpy as np


class Transaction:

    def __init__(self):
        self.translations: pd.DataFrame = None
    

    def load_transactions(self, filepath, reverse=False):
        ''
        
        data = pd.read_csv(
            filepath,
            delimiter=',',
            header=0,
            dtype=bool,
            usecols=lambda x: x != 'patient')
            
        return data
        