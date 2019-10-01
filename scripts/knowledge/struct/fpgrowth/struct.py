
import pandas as pd
import numpy as np

from collections import defaultdict

from knowledge.util.print import PrintUtil as pr

class Fpgrowth:
    def __init__(self, support):
        self.tree = Tree()
        self.support = support

    @staticmethod

    @staticmethod
    def matrix(transactions):
        '''converts list of transactions into a sparse matrix

        Paramaters
        ----------
        transactions: list[list]
            A list of transactions, which are each a list of items.

            For example,
            [[a, b, c, d],
             [b, d],
             [d, a, c],
             [c, e, a]]

        Returns
        -------
        matrix: numpy.ndarray
            A numpy array representing the bool matrix of the transactions.

            For example,
            [[True,  True,  True,  True,  False],
             [False, True,  False, True,  False],
             [True,  False, True,  True,  False],
             [False, False, True,  False, True ]]

        items: list
            A list containing the items names for the  matrix.

            For example,
            [a, b, c, d, e]
        '''

        unique = set()
        for trans in transactions:
            for item in trans:
                unique.add(item)

        matrix = np.zeros((len(transactions),len(unique)), dtype=bool)
        items = {key: val for val, key in enumerate(unique)}

        for idx, trans in enumerate(transactions):
            for item in trans:
                matrix[idx, items[item]] = True

        return matrix, list(unique)

    def build_tree(self, matrix, items):
        '''

        '''
        items = np.array(item for item in self.support if item in items)
        
        
        # for row in matrix:
            # np.array(item for item in )





    def find_patterns(self, bin_size=None):
        if bin_size is None:
            return
        else:
            yield

class Tree:
    def __init__(self, root=None):
        self.root = Node(root)

class Node:
    def __init__(self, item, parent=None):
        self.item = item
        self.count = 1
        self.children = defaultdict(Node)
        self.parent = parent
