from getpass import getpass
from associations.labevents_itemid_to_cui import LabeventConversion

user = 'root'
password = getpass(f'Password for {user}: ')

params = {'user': user, 'password': password,
          'db': 'derived', 'host': 'db01.healthcreek.org'}

mapping_creation = LabeventConversion(params)

mapping_creation.create_labevents_UMLS_all()
