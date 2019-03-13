from getpass import getpass
from assoc_discovery.create_umls_cui_mapping import CreateUMLSCUIMapping

user = 'root'
password = getpass()

params = {'user': 'root', 'password': password,
          'db': 'derived', 'host': 'db01.healthcreek.org'}

mapping_creation = CreateUMLSCUIMapping(params)

mapping_creation.create_labevents_UMLS_all()
