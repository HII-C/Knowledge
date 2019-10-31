
import json
import re
import os

from knowledge.util.error import ConfigError
from knowledge.util.print import PrintUtil as pr


class ConfigUtil:
    '''

    '''

    @staticmethod
    def file_readable(filepath):
        return os.access(filepath, os.R_OK)

    @staticmethod
    def file_exists(filepath):
        return os.path.exists(filepath)

    @staticmethod
    def file_writable(filepath):
        if os.path.exists(filepath):
            if os.path.isfile(filepath):
                return os.access(filepath, os.W_OK)
            else:
                return False 
        
        pdir = os.path.dirname(filepath)
        if not pdir: 
            pdir = '.'
        return os.access(pdir, os.W_OK)


    @staticmethod
    def load_config(filepath):
        try:
            with open(filepath) as handle:
                return json.load(handle)
        except FileExistsError as err:
            pr.print(f'Config file "{filepath}" does not exist; '
                'terminating model run.', time=True)
            raise err
        except json.JSONDecodeError as err:
            pr.print(f'Config file "{filepath}" is not valid json; '
                'terminating model run.', time=True)
            raise err


    @classmethod
    def verify_config(self, config, specspath, convert=False):
        with open(specspath) as handle:
            specs = json.load(handle)
        
        for name, spec in specs.values():
            config[name] = self.verify_spec(config, spec, name)

        return config
    
    
    @classmethod
    def verify_spec(self, config, spec, name):
        if name in config:
            attr = config[name]
            all_types = {'dict': str, 'int': int, 'bool': bool, 'float': float}
            valid_types = [all_types[a] for a in spec['type'].split(',')]

            if type(attr) not in valid_types:
                raise TypeError(f'Parameter "{name}" expected to be of type "'
                    f'{spec["type"]}" but found "{type(attr).__name__}".')

            if 'options' in spec and len(spec['options']) and attr not in spec['options']:
                options = ', '.join([f'"{str(opt)}"' for opt in spec['options']])
                raise ValueError(f'Parameter "{name}" expected to be {options} '
                    f'but found "{attr}".')

            if 'min' in spec and attr < spec['min']:
                raise ValueError(f'Parameter "{name}" expected to be greater than '
                    f'{spec["min"]} but found {attr}.')

            if 'max' in spec and attr > spec['max']:
                raise ValueError(f'Parameter "{name}" expected to be less than '
                    f'{spec["max"]} but found {attr}.')

            if 'regex' in spec and not re.search(spec['regex'], attr):
                raise ValueError (f'Parameter "{name}" expected to match pattern '
                    f'{spec["regex"]} but found "{attr}".')
            
            if 'special' in spec and len(spec['special']):
                for prop in spec['special']:
                    if prop == 'checkFileReadable' and not self.file_readable(attr):
                        raise FileNotFoundError(f'Parameter "{name}" needs to be a '
                            f'path to a readable file; "{attr}" was not.')
                    elif prop == 'checkFileWritable' and not self.file_writable(attr):
                        raise FileNotFoundError(f'Parameter "{name}" needs to be a '
                            f'path to a writable file; "{attr}" was not.')

            return attr

        elif 'required' not in spec or not spec['required']:
            if 'default' in spec:
                return spec['default']
            else:
                return None
        else:
            raise ConfigError(f'Parameter "{name}" is required.')
