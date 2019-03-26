from getpass import getpass

from assoc_discovery.process_predicates import PredicateData

user = 'root'
password = getpass(f'Password for {user}: ')

params = {'user': user, 'password': password,
          'db': 'derived', 'host': 'db01.healthcreek.org'}

example = PredicateData(params)
example.create_small_semmed('small_semmed', n=1000)
example.build_tables(tuple(['TREATS']), 'derived',
                     'small_semmed', output_db='semmed_cleaning')
