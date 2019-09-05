
import dropbox
import sys
import os

from argparse import ArgumentParser
from collections import defaultdict

from knowledge.util.print import PrintUtil as pr

class DropboxUtil:
    team = {}
    local_dir = '~'
    drop_dir = '/home/benjamin'
        
    @classmethod
    def connect(self, key):
        self.dbx = dropbox.Dropbox(key)

    @classmethod
    def shell(self):
        while self.read_command():
            pass

    @classmethod
    def format_ls(self, data):
        output = []
        for entry in data:
            output.append((
                self.decode_user(entry.sharing_info.modified_by) \
                    if hasattr(entry.sharing_info, 'modified_by') else 'folder',
                *self.decode_size(entry.size \
                    if hasattr(entry, 'size') else 4096),
                self.decode_time(entry.server_modified) \
                    if hasattr(entry, 'server_modified') else '',
                entry.name))
        align = ['l', 'r', 'l', 'r', 'l']
        pad = [2, 0, 2, 2, 2]
        return pr.table(output, align=align, pad=pad)

    @staticmethod
    def format_lls(data):
        pass

    @classmethod
    def decode_dir(self, dir1, dir2):
        str1 = dir1.split('/')
        str2 = dir2.split('/')
        if str2[0] == '':
            return '/'.join(str2)
        while str2[0] == '..':
            str2.pop(0)
            str1.pop(-1)
        while str2[0] == '.':
            str2.pop(0)
        while len(str1) > 1 and str1[-1] == '':
            str1.pop(-1)
        return '/'.join(str1 + str2)

    @classmethod
    def decode_user(self, user):
        if not hasattr(self.team, user):
            self.team[user] = self.dbx.users_get_account(user).name.given_name
        return self.team[user]

    @classmethod
    def decode_time(self, time):
        months = ('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
            'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
        return (str(time.day).zfill(2) + ' ' + months[time.month] + ' ' +
            str(time.hour).zfill(2) + ':' + str(time.minute).zfill(2))

    @classmethod
    def decode_size(self, value):
        if value >= 10000000000:
            value /= 1000000000
            unit = 'GB'
        elif value >= 10000000:
            value /= 1000000
            unit = 'MB'
        elif value >= 10000:
            value /= 1000
            unit = 'KB'
        else:
            unit = ''
        return str(int(value)), unit        

    @classmethod
    def parse_command(self, string):
        args = string.split(' ')
        args = [arg for arg in args if arg != '']
        cmd = args[0] if len(args) else ''
        return cmd, args[1:]

    @classmethod
    def read_command(self):
        cmd = input('dropbox> ')
        cmd, args = self.parse_command(cmd)

        if cmd == 'exit':
            pr.print('goodbye')
            return False
        elif cmd == 'help':
            pr.print((
                ('cd', 'changes Dropbox directory to specified directory'),
                ('dir', 'displays working directories'),
                ('exit', 'exits the dropbox API shell'),
                ('help', 'lists all valid commands and their usage'),
                ('lcd', 'changes local directory to specified directory'),                
                ('lls', 'lists all the files and folders in working local directory'),
                ('ls', 'lists all the files and folders in working Dropbox directory')),
                tbl=True)
        elif cmd == 'ls':
            try:
                target = self.drop_dir if len(args) == 0 \
                    else self.decode_dir(self.drop_dir, args[0])
                pr.print(target)
                files = self.dbx.files_list_folder(target).entries
                pr.print(self.format_ls(files))
            except Exception:
                pr.print('invalid target directory')
        elif cmd == 'lls':
            target = self.local_dir if len(args) == 0 \
                else self.decode_dir(self.local_dir, args[0])
            if os.path.isdir(target):
                with os.scandir() as dir_entries:
                    for entry in dir_entries:
                        pass
            else:
                pr.print('invalid target directory')
        elif cmd == 'cd':
            try:
                target = self.decode_dir(self.drop_dir, args[0])
                self.dbx.files_get_metadata(target)
                self.drop_dir = target
            except Exception:
                pr.print('invalid target directory')
        elif cmd == 'lcd':
            target = self.decode_dir(self.drop_dir, args[0])
            if os.path.isdir(target):
                self.local_dir = target
            else:
                pr.print('invalid target directory')
        elif cmd == 'dir':
            pr.print(f'drop:  {self.drop_dir}')
            pr.print(f'local: {self.local_dir}')
        elif cmd == 'put':
            pass
        elif cmd == 'get':
            pass
        else:
            pr.print('invalid command; type "help" for list of valid commands')
        return True

if __name__ == '__main__':
    argparser = ArgumentParser(prog='DropboxShell',
        description='Creates a bash interface for using a Dropbox API.')
    argparser.add_argument('--key', type=str, dest='key',
        default='',
        help=('Specify a Dropbox API key to connect to an account '
            'or folder; default is the key for the HII-C folder.'))
    args = argparser.parse_args()

    DropboxUtil.connect(args.key[0])
    DropboxUtil.shell()
