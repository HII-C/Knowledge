import pandas as pd


class Dataset:
    x: pd.DataFrame = None
    y: pd.Series = None

    def __init__(self):
        self.x = None
        self.y = None

    def drop_ratio(self, ratio=.10):
        ''' Drop all columns in x for which a positive value occurs
            in less the (N_rows * ratio) rows. TO BE IMPLEMENTED'''
        pass

    def drop_lowest_occ(self, n=40):
        ''' Drop columns the occur the least in all rows. 
            For binary this is sum(x[column]). 
            Should end len(x.shape[1]) = len(x.shape[1]) - n'''
        pass

    def drop_least_percent(self, percent=.20):
        ''' Drop columns that occur the least in all rows.
            For binary this is sum(x[column]).
            Should end len(x.shape[1]) = len(x.shape[1]) -
                            (percent * len(x.shape[1]))'''
        pass
