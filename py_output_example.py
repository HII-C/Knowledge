from py_output_creation.output_from_ml_model import ModelOutput
from getpass import getpass

password = getpass()
param = {'user': 'root', 'password': password,
         'host': 'localhost', 'db': 'derived'}

mod_out = ModelOutput(param)

example = [('aids', 'cancer', .8), ('fat', 'skinny', .025)]
mod_out.ordered_insert('tmp_model_test', example, .91)
