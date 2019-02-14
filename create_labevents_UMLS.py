from assoc_discovery.create_umls_cui_mapping import CreateUMLSCUIMapping

params = {'user': 'root', 'password': 'HealthCreekMySQLr00t',
          'db': 'derived', 'host': 'db01.healthcreek.org'}

cucm = CreateUMLSCUIMapping(params)

cucm.create_labevents_UMLS_with_ITEMID()