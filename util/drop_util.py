
import dropbox
import sys
import os

from argparse import ArgumentParser
from collections import defaultdict

if __name__ == '__main__':
    sys.path.insert(1, os.path.join(sys.path[0], '..'))

from util.print_util import Printer as pr

class DropboxShell:
    team = {}
    local_dir = '~'
    drop_dir = '/home/benjamin'
        
    @staticmethod
    def connect(key):
        DropboxShell.dbx = dropbox.Dropbox(key)

    @staticmethod
    def shell():
        while DropboxShell.read_command():
            pass

    @staticmethod
    def format_ls(data):
        shell = DropboxShell
        output = []
        for entry in data:
            output.append((
                shell.decode_user(entry.sharing_info.modified_by) \
                    if hasattr(entry.sharing_info, 'modified_by') else 'folder',
                *shell.decode_size(entry.size \
                    if hasattr(entry, 'size') else 4096),
                shell.decode_time(entry.server_modified) \
                    if hasattr(entry, 'server_modified') else '',
                entry.name))
        align = ['l', 'r', 'l', 'r', 'l']
        pad = [2, 0, 2, 2, 2]
        return pr.table(output, align=align, pad=pad)

    @staticmethod
    def format_lls(data):
        pass

    @staticmethod
    def decode_dir(dir1, dir2):
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

    @staticmethod
    def decode_user(user):
        shell = DropboxShell
        if not hasattr(shell.team, user):
            shell.team[user] = shell.dbx.users_get_account(user).name.given_name
        return shell.team[user]

    @staticmethod
    def decode_time(time):
        months = ('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
            'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
        return (str(time.day).zfill(2) + ' ' + months[time.month] + ' ' +
            str(time.hour).zfill(2) + ':' + str(time.minute).zfill(2))

    @staticmethod
    def decode_size(value):
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

    @staticmethod
    def parse_command(string):
        args = string.split(' ')
        args = [arg for arg in args if arg != '']
        cmd = args[0] if len(args) else ''
        return cmd, args[1:]

    @staticmethod
    def read_command():
        shell = DropboxShell
        cmd = input('dropbox> ')
        cmd, args = shell.parse_command(cmd)

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
                target = shell.drop_dir if len(args) == 0 \
                    else shell.decode_dir(shell.drop_dir, args[0])
                print(target)
                files = shell.dbx.files_list_folder(target).entries
                pr.print(shell.format_ls(files))
            except Exception:
                print('invalid target directory')
        elif cmd == 'lls':
            target = shell.local_dir if len(args) == 0 \
                else shell.decode_dir(shell.local_dir, args[0])
            if os.path.isdir(target):
                with os.scandir() as dir_entries:
                    for entry in dir_entries:
                        pass
            else:
                print('invalid target directory')
        elif cmd == 'cd':
            try:
                target = shell.decode_dir(shell.drop_dir, args[0])
                shell.dbx.files_get_metadata(target)
                shell.drop_dir = target
            except Exception:
                print('invalid target directory')
        elif cmd == 'lcd':
            target = shell.decode_dir(shell.drop_dir, args[0])
            if os.path.isdir(target):
                shell.local_dir = target
            else:
                print('invalid target directory')
        elif cmd == 'dir':
            pr.print(f'drop:  {DropboxShell.drop_dir}')
            pr.print(f'local: {DropboxShell.local_dir}')
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
    argparser.add_argument('--key', type=str, dest='key', nargs=1,
        default='',
        help=('Specify a Dropbox API key to connect to an account '
            'or folder; default is the key for the HII-C folder.'))
    args = argparser.parse_args()

    DropboxShell.connect(args.key[0])
    DropboxShell.shell()