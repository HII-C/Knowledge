import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict


class PatientMatrix:
    causal: pd.DataFrame = None
    causal_codes: List[str] = list()
    result: List[int] = None
    result_detail: Dict[int, Dict] = None
    result_codes: Tuple[str] = None
    pt_ids: List[str] = list()

    def __init__(self, causal: Dict, result: List[int], result_detail: Dict[int, Dict], args: Dict):
        conv_2d = np.array(list(causal.values()))
        self.causal = pd.DataFrame(data=conv_2d, **args)
        self.result = result
        self.result_detail = result_detail
        self.__update__()

    def occ_threshold(self, threshold=float(0.3), __print__=False):
        '''
        Remove codes that occur in less then (len(patient_concept) * cutoff). 
        Enforces that no "rare" conditions are fed to ML model.

        Keyword arguments:
        cutoff -- The ratio of occ we filter at (default = 0.8)
        '''

        col_sum = self.causal.sum().tolist()
        occ_by_code = dict(zip(self.causal_codes, col_sum))
        drop_list = list()

        if __print__:
            print(f'There are {len(self.causal_codes)} codes before dropping ' +
                  f'those in less than {threshold * 100.0}% of records.')
        for code, occ in list(occ_by_code.items()):
            if (occ / len(self.pt_ids)) < threshold:
                drop_list.append(code)

        self.causal.drop(drop_list, axis=1, inplace=True)
        self.__update__()

        if __print__:
            print(f'There are now {len(list(self.causal))} codes.')

    def __update__(self):
        self.pt_ids = list(self.causal.index)
        self.causal_codes = list(self.causal)
