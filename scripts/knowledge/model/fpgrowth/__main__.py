
import json

from getpass import getpass
from pkg_resources import resource_filename
from argparse import ArgumentParser

from knowledge.util.print import PrintUtil as pr
from knowledge.model.fpgrowth.model import FpgrowthModel

parser = ArgumentParser(prog='fpgrowth model runner',
    description='Run an fpgrowth association building model.')
parser.add_argument('--config', type=str, dest='config',
    default=resource_filename('knowledge', 'model/fpgrowth/config.json'),
    help=('Specify a config file location; default is "config.json" in '
        'this this module\'s build directory.'))
parser.add_argument('--log', type=str, dest='log', default=None,
    help='specify a log file location; by default the log will not be saved')
args = parser.parse_args()

if args.log is not None:
    pr.log(args.log)

try:
    with open(args.config) as handle:
        config = json.load(handle)
    database = config['database']
    database['password'] = getpass(
        f'SQL password for {database["user"]}@localhost: ')
except FileExistsError as err:
    pr.print(f'ERROR: Config file {args.config} does not exist.', time=True)
    raise err
except json.JSONDecodeError as err:
    pr.print(f'ERROR: Config file {args.config} is not valid json.', time=True)
    raise err
except KeyError as err:
    pr.print(f'ERROR: config file {args.config} missing database info.', time=True)
except Exception as err:
    raise err

model = FpgrowthModel(database)
model.run(config)