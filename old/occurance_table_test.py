from getpass import getpass
from associations.sum_relation_occurences import SumRelation

user = 'root'
password = getpass(f'Password for {user}: ')

params = {'user': user, 'password': password,
          'db': 'derived', 'host': 'db01.healthcreek.org'}

mapping_creation = SumRelation(params)

mapping_creation.get_occurences(output_table='occurance_test')
