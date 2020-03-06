
import gzip
import csv
import pandas as pd
import numpy as np
import logging as log

from collections import defaultdict
from itertools import combinations
from multiprocessing import Pool, Value
from ctypes import c_uint64


count = None
n = None


def multiopen(filepath, **kwargs):
    'autodetect compressed file'

    if filepath.split('.')[-1] == 'gz':
        data = gzip.open(filepath, **kwargs)
    else:
        data = open(filepath, **kwargs)
    return data


def find_patterns(tree, min_support, max_support, max_size):
    'pattern finding function for a single thread'

    generator = Fpgrowth.generate_patterns(tree, min_support, 
        max_support, max_size)
    patterns = []
    for pattern in generator:
        patterns.append(pattern)
        if count.value >= n.value:
            with n.get_lock():
                n.value <<= 1
            log.info(f'Found pattern {count.value}.')
        with count.get_lock():
            count.value += 1
    return patterns


class Fpgrowth:
    '''data structure and utilities for running fpgrowth algorithm

    Parameters
    ----------
    support: dict{str: int}
        A dictionary mapping the names of items to their support;
        not the support here is an integer between zero and the 
        number of transactions, not a float between 0 ad 1. '''

    def __init__(self, support):
        self.tree = Tree()
        self.support = support


    @classmethod
    def generate_patterns(self, tree, min_support=0, max_support=1, max_size=0):
        '''recursively generates frequent patterns off of tree
        
        Parameters
        ----------
        tree: Tree
            The tree to read patterns from; this function will continue to
            recursively itself with subtrees until the tree is a path or empty.

        min_support: int
            The minimum support of a pattern for it to be included in the
            list of frequent patterns.

        max_support: int

        max_size: int


        Yields
        ------
        pattern: tuple(float, list[str])    '''

        items = tree.nodes.keys()
        if tree.is_path():
            size_remain = len(items) + 1
            if max_size:
                size_remain = max_size - len(tree.items) + 1
            for i in range(1, size_remain):
                for itemset in combinations(items, i):
                    support = min([tree.nodes[i][0].count for i in itemset])
                    yield support, tree.items + list(itemset)
        elif max_size == 0  or max_size > len(tree.items):            
            for item in items:
                support = sum([node.count for node in tree.nodes[item]])
                yield support, tree.items + [item]
                
            for item in items:
                subtree = tree.conditional_tree(item, min_support, max_support)
                for support, itemset in self.generate_patterns(subtree, 
                        min_support, max_support, max_size):
                    yield support, itemset

        
    @classmethod
    def calculate_support(self, filepath):
        csvfile = multiopen(filepath, mode='r')
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        count = 0
        n = 1

        _, *items = next(csvreader)
        support = [0]*len(items)
        for transaction in csvreader:
            for item, cond in enumerate(transaction[1:]):
                if int(cond):
                    support[item] += 1
                count += 1
                if count == n:
                    log.info(f'Processed code {count}.')
                    n <<= 1
        support = dict(zip(items, support))

        # alterate file format

        # support = defaultdict(int)
        # for transaction in csvreader:
        #     for code in transaction:
        #         support[code] += 1
        #         count += 1
        #         if count == n:
        #             log.info(f'Processed code {count}.')
        #             n <<= 1

        if count != n >> 1:
            log.info(f'Processed code {count}.')
        csvfile.close()

        return support

    
    @classmethod
    def load_patterns(self, filepath):
        csvfile = multiopen(filepath, mode='r')
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        patterns = {}

        for row in csvreader:
            patterns[frozenset(row[:-1])] = int(row[-1])

        csvfile.close()
        return patterns


    @classmethod
    def write_patterns(self, patterns, filepath):
        csvfile = multiopen(filepath, mode='w')
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"')

        for codes, support in patterns.items():
            csvwriter.writerow((*codes, support))

        csvfile.close()


    def load_transactions(self, filepath):
        csvfile = multiopen(filepath, mode='r')
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        count = 0
        n = 1
        
        _, *items = next(csvreader)
        for transaction in csvreader:
            itemset = [item for cond, item in zip(transaction[1:], items) 
                if int(cond) and item in self.support]
            itemset.sort(key=self.support.get, reverse=True)
            self.tree.insert_itemset(itemset)
            count += 1
            if count == n:
                log.info(f'Processed transaction {count}.')
                n <<= 1

        # alternate file format

        # for transaction in csvreader:
        #     self.tree.insert_itemset(transaction)
        #     count += 1
        #     if count == n:
        #         log.info(f'Processed transaction {count}.')
        #         n <<= 1

        if count != n >> 1:
            log.info(f'Processed transaction {count}.')
        csvfile.close()


    def find_patterns(self, tree=None, min_support=0, max_support=1, 
            max_size=0, cores=None):
        '''finds patterns from tree using multiprocessing

        Parameters
        ----------
        tree: Tree
            The tree to read patterns from

        min_support: float
            The minimum support of a pattern for it to be included in the
            list of frequent patterns.

        max_support: float
            
        max_size: int

        cores: int/None
            Number of cores to utilize; default is None, which will auto detect
            the number of cores available to use.

        Returns
        -------
        patterns: list[list[float, list[str]]]
            A list of patterns, where each pattern is a list containing
            the pattern support value and list of items in the pattern. '''
        
        tree = self.tree if tree is None else tree
        min_support = min_support * tree.root.count
        max_support = max_support * tree.root.count
        items = tree.nodes.keys()
        subtrees = []
        patterns = []

        log.info(f'Balancing tree into tasks for {cores} cores.')

        for item in items:
            subtree = tree.conditional_tree(item, min_support, max_support)
            subtrees.append((subtree, min_support, max_support, max_size))
        subtrees.sort(key=lambda tree: tree[0].root.count_descendents(), reverse=True)
        
        global count, n
        count = Value(c_uint64)
        count.value = 0
        n = Value(c_uint64)
        n.value = 1

        log.info(f'Finding patterns from root node.')

        for item in items:
            support = sum([node.count for node in tree.nodes[item]])
            patterns.append((support, (item,)))
            if count.value >= n.value:
                log.info(f'Found pattern {count.value}.')
                n.value <<= 1
            count.value += 1

        log.info(f'Now finding remaining patterns on {cores} cores.')

        pool = Pool(processes=cores)
        for result in pool.starmap(find_patterns, subtrees):
            patterns.extend(result)
        if count.value != n.value >> 1:
            log.info(f'Found pattern {count.value}.')
        pool.close()
        pool.join()

        return {frozenset(pattern[1]): pattern[0] for pattern in patterns}


class Tree:
    '''a tree structure with variable length, unordered children

    Parameters
    ----------
    root: str/int/float = None
        The value of the root node; default is None.    '''

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

        for item in itemset[idx:]:
            child = Node(item, count=count, parent=node)
            node.children[item] = child
            self.nodes[item].append(child)
            node = child
            

    def conditional_tree(self, cond, min_support, max_support):
        branches = []
        count = defaultdict(int)
        for node in self.nodes[cond]:
            branch = node.itempath()
            branches.append(branch)
            for item in branch:
                count[item] += node.count
                
        items = [item for item in count if count[item] >= min_support
            and count[item] <= max_support]
        items.sort(key=count.get)
        rank = {item: i for i, item in enumerate(items)}

        tree = Tree()
        tree.items = self.items + [cond]
        for idx, branch in enumerate(branches):
            branch = sorted([node for node in branch if node in rank],
                key=rank.get, reverse=True)
            tree.insert_itemset(branch, self.nodes[cond][idx].count)

        return tree


    def is_path(self):
        node = self.root
        while len(node.children) == 1:
            node = list(node.children.values())[0]
        return len(node.children) == 0

    
    def print(self):
        pass


class Node:
    '''an element in a tree structure

    Parameters
    ----------
    item: str/int/float
        A value describing the name of the item the node is associated with.
    
    count: int = 1
        What value to initialize the count of the node on; default is 1.

    parent: Node = None
        The parent node of the node being constructed; default is None type.    '''

    def __init__(self, item, count=1, parent=None):
        self.item = item
        self.count = count
        self.children = {}
        self.parent = parent


    def count_descendents(self):
        return sum(node.count_descendents() + 1 for node in self.children.values())


    def itempath(self):
        path = []
        parent = self.parent
        while parent.item is not None:
            path.append(parent.item)
            parent = parent.parent
        path.reverse()
        return path
