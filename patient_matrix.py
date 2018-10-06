import pandas as pd
import numpy as np
from typing import Dict
from collections import defaultdict


class PatientMatrix:
    pt_count = None
    pt_data: pd.DataFrame = None

    def __init__(self, pt_data: Dict, pd_args: Dict):
        print(np.array(pt_data.values()))
        self.pt_data = pd.DataFrame(data=np.array(
            list(pt_data.values())), **pd_args)
        print(self.pt_data.head())
        self.pt_count = len(self.pt_data.index)
        print(self.pt_count)

    def occ_threshold(self, cutoff=0.8):
        '''
        Remove codes that occur in less then (len(patient_concept) * cutoff). 
        Enforces that no "rare" conditions are fed to ML model.

        Keyword arguments:
        cutoff -- The ratio of occ we filter at (default = 0.8)
        '''
        # occ_dict = defaultdict(int)
        # for index, row in self.pt_data.:

        #     if row == 1:
        #         occ += 1
