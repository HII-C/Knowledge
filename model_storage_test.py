from py_output_creation.model_storage import ModelStorage

params = {'user': 'root', 'password': 'HealthCreekMySQLr00t',
          'db': 'derived', 'host': 'db01.healthcreek.org'}

example = ModelStorage(params)
my_storage_input = [['testA', 'testB', 2, 6.2],
                    ['testA', 'testC', 2, 3.9],
                    ['testB', 'testA', 2, 1.2],
                    ['testB', 'testC', 2, 0.2],
                    ['testA1', 'testB1', 2, 6.2],
                    ['testA1', 'testC1', 2, 3.9],
                    ['testB1', 'testA1', 2, 1.2],
                    ['testB1', 'testC1', 2, 0.2],
                    ['testA2', 'testB2', 2, 6.2],
                    ['testA2', 'testC2', 2, 3.9],
                    ['testB2', 'testA2', 2, 1.2],
                    ['testB2', 'testC2', 2, 0.2]]
example.update_storage(my_storage_input = my_storage_input)
