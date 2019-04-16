from getpass import getpass
from associations.create_umls_mappings import MappingToUMLS

user = 'root'
password = getpass(f'Password for {user}: ')

params = {'user': user, 'password': password,
          'db': 'derived', 'host': 'db01.healthcreek.org'}

example = MappingToUMLS(**params)

example.create_table('derived', 'UMLS_mappings')