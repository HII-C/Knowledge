
import csv
import re
import math
from argparse import ArgumentParser
from collections import defaultdict

from knowledge.util.config import ConfigUtil
from knowledge.util.print import PrintUtil as pr


class CsvUtil:
    
    @classmethod
    def analyze_csv(self, filepath, skip=0):
        pr.print(f'Analyzing CSV file from {args.csv}.', time=True)
        regexp = re.compile(r'^(?P<int>[+-]?\d+|0)$|^(?P<float>[+-]?\d+\.\d+(?:[Ee]'
            r'[+-]?\d+)?)$|^(?P<date>\d{4}-\d{2}-\d{2})$|^(?P<datetime>'
            r'\d{4}-\d{2}-\d{2}\ \d{2}:\d{2}:\d{2})$')
        with open(filepath, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            cols = reader.__next__()
            for a in range(skip):
                reader.__next__()
            length = len(cols)
            pr.print(f'Found {length} columns in file.', time=True)
            result = {col: {
                'type': 'null',
                'min_width': float('inf'),
                'max_width': 0,
                'min': float('inf'),
                'max': float('-inf')
            } for col in cols }
            count = skip
            n = 2 ** (int(math.log(skip, 2)) + 1) if skip > 0 else 1
            pr.print('Scanning CSV file data.', time=True)
            for row in reader:
                if len(row) != length:
                    pr.print(f'warn: row {count + 1} has {len(row)} columns', time=True)
                    continue
                for col, data in zip(cols, row):
                    if result[col]['type'] != 'str' and data != '':
                        match = regexp.match(data)
                        if match is None:
                            result[col]['type'] = 'str'
                        elif match.group('date') is not None:
                            if result[col]['type'] in ('null', 'date'):
                                result[col]['type'] = 'date'
                            else:
                                result[col]['type'] = 'str'
                        elif match.group('datetime') is not None:
                            if result[col]['type'] in ('null', 'datetime'):
                                result[col]['type'] = 'datetime'
                            else:
                                result[col]['type'] = 'str'
                        elif match.group('int') is not None:
                            if result[col]['type'] != 'float':
                                result[col]['type'] = 'int'
                            result[col]['min'] = min(result[col]['min'], int(data))
                            result[col]['max'] = max(result[col]['max'], int(data))
                        elif match.group('float') is not None:
                            result[col]['type'] = 'float'
                            result[col]['min'] = min(result[col]['min'], float(data))
                            result[col]['max'] = max(result[col]['max'], float(data))
                    result[col]['min_width'] = min(result[col]['min_width'], len(data))
                    result[col]['max_width'] = max(result[col]['max_width'], len(data))

                count += 1
                if count == n:
                    pr.print(f'Found row {count}.', time=True)
                    n = n << 1
        
        if count != n:
            pr.print(f'Found row {count}.', time=True)

        pr.print('Data analysis complete.', time=True)
        pr.print('Analysis results:', time=True)

        lst = [[key] + list(val.values()) for key, val in result.items()]
        lst = [['col', 'type', 'min_width', 'max_width', 'min_value', 'max_value']] + lst
        tbl = pr.table(lst, hrule=1, pad=2)
        pr.print(tbl)


if __name__ == '__main__':
    argparser = ArgumentParser(prog='CsvAnalyzer',
        description='Analyzes CSV files to determine typing and value/width bounds.')
    argparser.add_argument('--csv', type=str, dest='csv', required=True,
        help='File path location of CSV file to analyze.')
    argparser.add_argument('--skip', type=int, dest='skip', required=False,
        default=0, help='Number of lines to skip; header line is already skipped by default.')
    args = argparser.parse_args()
    

    if not ConfigUtil.file_readable(args.csv):
        raise ValueError(f'File at {args.csv} does not exist or is not readable.')

    CsvUtil.analyze_csv(args.csv, skip=args.skip)