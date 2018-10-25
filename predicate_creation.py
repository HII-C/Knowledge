from assoc_discovery.process_predicates import PredicateData

params = {'user': 'root', 'password': 'HealthCreekMySQLr00t',
          'db': 'derived', 'host': 'db01.healthcreek.org'}

example = PredicateData(params)
example.create_small_semmed('small_semmed', n=1000)
example.build_tables(tuple(['TREATS']), 'derived',
                     'small_semmed', output_db='semmed_cleaning')
