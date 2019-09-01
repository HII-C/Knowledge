from getpass import getpass
from models.output.storage import Storage

user = 'root'
password = getpass(f'Password for {user}: ')

params = {'user': user, 'password': password,
          'db': 'derived', 'host': 'db01.healthcreek.org'}

example = Storage(params)
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
example.update_storage(storage_input=my_storage_input)
