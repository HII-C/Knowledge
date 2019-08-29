
import math
import os
import time

from datetime import datetime

class Printer:

    persist_str = ''
    persist_rows = 0

    # https://en.wikipedia.org/wiki/ANSI_escape_code

    FRMTS = {
        'bold': 1,
        'faint': 2,
        'italic': 3,
        'underline': 4,
        'strikethrough': 9
    }

    @staticmethod
    def table(tbl, brdr=False, align='r', pad=1):
        if align in ('r', 'l'):
            align = [align] * len(tbl[0])
        if isinstance(pad, int):
            pad = [pad] * len(tbl[0])
        tbl = [[str(cell) for cell in row] for row in tbl]
        widths = [max([len(cell) for cell in col]) 
            for col in list(map(list, zip(*tbl)))]
        return '\n'.join([''.join([cell.ljust(width) + ' '*p
            if a == 'l' else cell.rjust(width) + ' '*p
            for cell, width, a, p in zip(row, widths, align, pad)]) 
            for row in tbl])
    
    @staticmethod
    def time(string):
        date = datetime.now()
        return ('[' + date.strftime('%H:%M:%S:') + 
            str(date.microsecond // 1000).zfill(3) +
            '] ' + string)

    @staticmethod
    def format(string, *frmts):
        codes = tuple(Printer.FRMTS[frmt] for frmt in frmts if frmt in Printer.FRMTS)
        return ('\x1b[%sm'*len(codes) % codes) + string + '\x1b[0m'        
    
    @staticmethod
    def progress(string, prog):
        prog = min(1, max(0, prog))
        perc = 100 * prog
        return ( string + ' [' + 
                '=' * int(perc // 5) + 
                '_' * int(20 - perc // 5) + 
                '] ' + str(round(perc, 1)) + '%')

    @staticmethod
    def clear(rows=None):
        if rows is None:
            rows, cols = os.popen('stty size', 'r').read().split()
            rows = int(rows)
        print('\n'*(rows-1) + '\033[F'*rows, end='\r')

    @staticmethod
    def delete(rows):
        pass

    @staticmethod
    def push():
        persist = Printer.persist_str
        Printer.print('', persist=True, replace=True)
        Printer.print(persist)

    @staticmethod
    def printer(*args, **kwargs):
        def custom_print(string, *margs, **mkwarg):
            Printer.print(string, *args, *margs, **kwargs, **mkwarg)
        return custom_print

    @staticmethod
    def print(string, persist=False, replace=False, time=False, progress=None,
            tbl=False, frmt=None):
        rows, cols = os.popen('stty size', 'r').read().split()
        rows = int(rows)
        cols = int(cols)
        print(('\033[F'+' '*cols)*Printer.persist_rows, end='\r')
        if tbl:
            string = Printer.table(string)
        if time:
            string = Printer.time(string)
        if progress is not None:
            string = Printer.progress(string, progress)
        if frmt is not None:
            if isinstance(frmt, list):
                string = Printer.format(string, *frmt)
            elif isinstance(frmt, str):
                string = Printer.format(string, frmt)
        if persist:
            if not replace and Printer.persist_rows:
                Printer.persist_str += '\n' + string
            else:
                Printer.persist_str = string
            Printer.persist_rows = sum([math.ceil(len(row) / cols)
                for row in string.split('\n')])
        else:
            print(string)
        if Printer.persist_rows:
            print(Printer.persist_str)