
import json
import sys

from getpass import getpass
from pkg_resources import resource_filename
from argparse import ArgumentParser

from knowledge.util.print import PrintUtil as pr
from knowledge.util.config import ConfigUtil
from knowledge.model.association.model import AssociationModel

sys.setrecursionlimit(10000)

parser = ArgumentParser(prog='association model runner',
    description='run an association building model')
parser.add_argument('--config', type=str, dest='config',
    default=resource_filename('knowledge', 'model/association/config.json'),
    help=('specify a config file location; default is "config.json" in '
        'this this module\'s build directory'))
parser.add_argument('--log', type=str, dest='log', default=None,
    help='specify a log file location; by default the log will not be saved')
args = parser.parse_args()

config = ConfigUtil.load_config(args.config)
specs = ConfigUtil.load_specs(resource_filename('knowledge', 
    'model/association/specs.json'))

config = ConfigUtil.verify_config(specs, config)

input('Config validated.')

if config['run']['silent']:
    pr.silence()

if args.log is not None:
    pr.log(args.log)
elif config['run']['log']:
    pr.log(config['run']['log'])

database = config['database']
database['password'] = getpass(f'SQL password for {database["user"]}@localhost: ')

model = AssociationModel(database)
model.run(config)