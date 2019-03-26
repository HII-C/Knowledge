from getpass import getpass
from associations.create_umls_cui_mapping import CreateUMLSCUIMapping

user = 'root'
password = getpass(f'Password for {user}: ')

params = {'user': user, 'password': password,
          'db': 'derived', 'host': 'db01.healthcreek.org'}

mapping_creation = CreateUMLSCUIMapping(params)

mapping_creation.create_labevents_UMLS_all()
