
import os
import tempfile
import subprocess
import logging as log

from knowledge.util.print import PrintUtil

class FilesysUtil:
    @classmethod
    def file_readable(self, filepath):
        'check that file can be read'
        return os.access(filepath, os.R_OK)


    @classmethod
    def file_exists(self, filepath):
        'check that file exists'
        return os.path.exists(filepath)
    

    @classmethod
    def file_writable(self, filepath):
        'check that file can be written to'
        if self.file_exists(filepath):
            if os.path.isfile(filepath):
                return os.access(filepath, os.W_OK)
            else:
                return False 
        
        pdir = os.path.dirname(filepath)
        if not pdir: 
            pdir = '.'
        return os.access(pdir, os.W_OK)


    @classmethod
    def create_tempfile(self, suffix=None, delete=True):
        return tempfile.NamedTemporaryFile(suffix=suffix, delete=delete)

    
    @classmethod
    def delete_file(self, filepath):
        os.remove(filepath)


    @classmethod
    def format_xml(self, source, target=None):
        'format an xml file'
        if target is None:
            targetfile = self.create_tempfile(suffix='xml', delete=False)
            target = targetfile.name
            targetfile.close()
            result = subprocess.run(f'xmllint --format {source} > {target}', shell=True)
            if result:
                log.error(f'Failed to format XML on {target}.')
            else:
                subprocess.run(('mv', target, source), shell=False)
        else:
            result = subprocess.run(f'xmllint --format {source} > {target}', shell=True)
            if result:
                log.error(f'Failed to format XML from {source} to {target}.')
        
        return not bool(result)


    @classmethod
    def decompress(self, source, target=None, keep=False):
        'decompress a gz file'
        keep = '--keep' if keep else ''
        if target is None:
            targetfile = self.create_tempfile(
                suffix=source.split('.')[-2], delete=False)
            target = targetfile.name
            targetfile.close()
        subprocess.run(f'gunzip --stdout {keep} {source} > {target}', shell=True)

        return target


    @classmethod
    def compress(self, source, target=None, keep=False):
        pass