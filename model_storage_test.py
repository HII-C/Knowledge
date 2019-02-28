from py_output_creation.model_storage import ModelStorage

params = {'user': 'root', 'password': 'HealthCreekMySQLr00t',
          'db': 'derived', 'host': 'db01.healthcreek.org'}

example = ModelStorage(params)
example.update_storage()
