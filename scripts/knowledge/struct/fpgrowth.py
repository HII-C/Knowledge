
import pandas as pd
import numpy as np

from collections import defaultdict
from itertools import combinations

from knowledge.util.print import PrintUtil as pr

class Fpgrowth:
    '''data structure and utilities for running fpgrowth algorithm

    Parameters
    ----------
    support: dict
        A dictionary mapping the names of items to their support.
    '''

    def __init__(self, support):
        self.tree = Tree()
        self.pointer = None
        self.support = support
    

    @staticmethod
    def matrix(transactions):
        '''converts list of transactions into a sparse matrix

        Parameters
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

        items: tuple
            A list containing the items names for the matrix, which 
            correspond to the columns of the matrix.

            For example,
            (a, b, c, d, e)
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

        return matrix, tuple(unique)


    def build_tree(self, matrix, items, silent=False):
        '''appends transactions to tree

        Parameters
        ----------
        matrix: numpy.ndarray
            A numpy array representing the bool matrix of the transactions.

            For example,
            [[True,  True,  True,  True,  False],
             [False, True,  False, True,  False],
             [True,  False, True,  True,  False],
             [False, False, True,  False, True ]]

        items: tuple
            A list containing the items names for the matrix, which 
            correspond to the columns of the matrix. This set of items must be 
            a subset of the support attribute.

            For example,
            (a, b, c, d, e)

        silent: bool = False
            If true, this process will not print algorithm progress messages;
            default is false.
        '''

        for i in range(len(matrix)):
            itemset = [item for cond, item in zip(matrix[i], items) if cond 
                and item in self.support]
            itemset.sort(key=self.support.get, reverse=True)
            self.tree.insert_itemset(itemset)


    def find_patterns(self, tree, min_support, max_size=0):
        '''recursively reads frequent patterns off of tree
        
        Parameters
        ----------
        tree: Tree
            The tree to read patterns from; this function will continue to
            recursively itself with subtrees until the tree is a path or empty.

        min_support: float
            The minimum support of a pattern for it to be included in the
            list of frequent patterns.

        Returns
        -------


        '''
        
        items = tree.nodes.keys()
        if tree.is_path():
            size_remain = len(items) + 1
            if max_size:
                size_remain = max_size - len(tree.items) + 1
            for i in range(1, size_remain):
                for itemset in combinations(items, i):
                    support = min([tree.nodes[i][0].count for i in itemset])
                    yield support, tree.items + list(itemset)
        elif not max_size or max_size > len(tree.items):
            for item in items:
                support = sum([node.count for node in tree.nodes[item]])
                yield support, tree.items + [item]
        else:
            for item in items:
                subtree = tree.conditional_tree(item, min_support)
                
                input('Press Enter to continue.')
                self.find_patterns(subtree, min_support)
                # for support, itemset in self.find_patterns(subtree, min_support):
                #     yield support, itemset



class Tree:
    '''a tree structure with variable length, unordered children

    Parameters
    ----------
    root: str/int/float = None
        The value of the root node; default is None.

    '''

    def __init__(self, root=None):
        self.root = Node(root)
        self.nodes = defaultdict(list)
        self.items = []
    

    def insert_itemset(self, itemset, count=1):
        node = self.root
        node.count += count

        idx = 0
        for item in itemset:
            if item in node.children:
                node = node.children[item]
                node.count += count
                idx += 1
            else:
                break

        for item in itemset[:idx]:
            child = Node(item, count=count, parent=node)
            node.children.append(child)
            self.nodes[item].append(child)
            node = child
            

    def conditional_tree(self, item, min_support):
        branches = []
        count = defaultdict(int)
        for node in self.nodes[item]:
            branch = node.itempath()
            branches.append(branch)
            for item in branch:
                count[item] += node.count
        
        items = [item for item in count if count[item] >= min_support]
        items.sort(key=count.get)
        rank = {item: i for i, item in enumerate(items)}

        tree = Tree()
        tree.items = self.items + [item]
        for idx, branch in enumerate(branches):
            branch = sorted([node for node in branch if node in rank],
                key=rank.get, reverse=True)
            tree.insert_itemset(branch, self.nodes[item][idx].count)

        return tree


    def is_path(self):
        node = self.root
        while len(node.children) == 1:
            node = list(node.children.values())[0]
        return len(node.children) == 0



class Node:
    '''an element in a tree structure

    Parameters
    ----------
    item: str/int/float
        A value describing the name of the item the node is associated with.
    
    count: int = 1
        What value to initializ the count of the node on; default is 1.

    parent: Node = None
        The parent node of the node being constructed; default is None type.

    '''

    def __init__(self, item, count=1, parent=None):
        self.item = item
        self.count = count
        self.children = {}
        self.parent = parent


    def itempath(self):
        path = []
        parent = self.parent
        while parent is not None:
            path.append(parent.item)
            parent = self.parent
        path.reverse()
        return path