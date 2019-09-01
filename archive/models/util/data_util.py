import pandas as pd


class Dataset:
    x: pd.DataFrame = None
    y: pd.Series = None

    def __init__(self):
        self.x = None
        self.y = None

    def drop_ratio(self, ratio=.10):
        ''' Drop all columns in x for which a positive value occurs
            in less then (N_rows * ratio) rows. TO BE IMPLEMENTED'''
        # Note: 0 - row, 1 - column
        x: pd.DataFrame = None

        dp_ratio = x.shape[1] * ratio
        x.drop(x.columns[x.apply(lambda col: col.value() > 0).sum(axis=0) <= dp_ratio], axis=1)
        pass

    def drop_lowest_occ(self, n=40):
        ''' Drop columns that occur the least in all rows.
            For binary this is sum(x[column]). 
            Should end len(x.shape[1]) = len(x.shape[1]) - n'''
        pass

    def drop_least_percent(self, percent=.20):
        ''' Drop columns that occur the least in all rows.
            For binary this is sum(x[column]).
            Should end len(x.shape[1]) = len(x.shape[1]) -
                            (percent * len(x.shape[1]))'''
        pass
