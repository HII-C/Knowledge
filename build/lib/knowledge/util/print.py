
import math
import os
import time

from datetime import datetime

class PrintUtil:
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

    @classmethod
    def table(self, tbl, brdr=False, align='l', pad=1):
        if align in ('r', 'l'):
            align = [align] * len(tbl[0])
        if type(pad) is int:
            pad = [pad] * len(tbl[0])
        tbl = [[str(cell) for cell in row] for row in tbl]
        widths = [max([len(cell) for cell in col]) 
            for col in list(map(list, zip(*tbl)))]
        return '\n'.join([''.join([cell.ljust(width) + ' '*p
            if a == 'l' else cell.rjust(width) + ' '*p
            for cell, width, a, p in zip(row, widths, align, pad)]) 
            for row in tbl])
    
    @classmethod
    def time(self, string):
        date = datetime.now()
        return ('[' + date.strftime('%H:%M:%S:') + 
            str(date.microsecond // 1000).zfill(3) +
            '] ' + string)

    @classmethod
    def format(self, string, *frmts):
        codes = tuple(self.FRMTS[frmt] for frmt in frmts if frmt in self.FRMTS)
        return ('\x1b[%sm'*len(codes) % codes) + string + '\x1b[0m'        
    
    @classmethod
    def progress(self, string, prog):
        prog = min(1, max(0, prog))
        perc = 100 * prog
        return ( string + ' [' + 
                '=' * int(perc // 5) + 
                '_' * int(20 - perc // 5) + 
                '] ' + str(round(perc, 1)) + '%')

    @classmethod
    def clear(self, rows=None):
        if rows is None:
            rows, cols = os.popen('stty size', 'r').read().split()
            rows = int(rows)
            cols = int(cols)
        print('\n'*(rows-1) + '\033[F'*rows, end='\r')

    @classmethod
    def delete(self, rows):
        pass

    @classmethod
    def push(self):
        persist = self.persist_str
        self.print('', persist=True, replace=True)
        self.print(persist)

    @classmethod
    def printer(self, *args, **kwargs):
        def custom_print(string, *margs, **mkwarg):
            self.print(string, *args, *margs, **kwargs, **mkwarg)
        return custom_print

    @classmethod
    def print(self, string='', persist=False, replace=False, time=False, 
            progress=None, tbl=False, frmt=None):
        rows, cols = os.popen('stty size', 'r').read().split()
        rows = int(rows)
        cols = int(cols)
        print(('\033[F'+' '*cols)*self.persist_rows, end='\r')
        if tbl:
            string = self.table(string)
        if time:
            string = self.time(string)
        if progress is not None:
            string = self.progress(string, progress)
        if frmt is not None:
            if type(frmt) is list:
                string = self.format(string, *frmt)
            elif type(frmt) is str:
                string = self.format(string, frmt)
        if persist:
            if not replace and self.persist_rows:
                self.persist_str += '\n' + string
            else:
                self.persist_str = string
            self.persist_rows = sum([math.ceil(len(row) / cols)
                for row in string.split('\n')])
        else:
            print(string)
        if self.persist_rows:
            print(self.persist_str)