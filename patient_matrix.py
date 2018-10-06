import pandas as pd
import numpy as np
from typing import Dict
from collections import defaultdict


class PatientMatrix:
    pt_count = None
    pt_data: pd.DataFrame = None

    def __init__(self, pt_data: Dict, pd_args: Dict):
        self.pt_data = pd.DataFrame(data=np.array(
            list(pt_data.values())), **pd_args)
        self.pt_count = len(self.pt_data.index)

    def occ_threshold(self, threshold=float(0.3), __print__=False):
        '''
        Remove codes that occur in less then (len(patient_concept) * cutoff). 
        Enforces that no "rare" conditions are fed to ML model.

        Keyword arguments:
        cutoff -- The ratio of occ we filter at (default = 0.8)
        '''

        columns = list(self.pt_data)
        pd_sum = self.pt_data.sum().tolist()
        occ_by_code = dict(zip(columns, pd_sum))
        drop_list = list()

        if __print__:
            print(f'There are {len(list(self.pt_data))} codes before dropping ' +
                  f'those in less than {threshold * 100.0}% of records.')
        for code, occ in list(occ_by_code.items()):
            if (occ / self.pt_count) < threshold:
                drop_list.append(code)

        self.pt_data.drop(drop_list, axis=1, inplace=True)
        if __print__:
            print(f'There are now {len(list(self.pt_data))} codes.')
