
import sys

from pkg_resources import resource_filename
from argparse import ArgumentParser

from knowledge.util.print import PrintUtil as pr
from knowledge.util.config import ConfigUtil
from knowledge.model.association.model import AssociationModel

# needed for pickling/unpickling large trees
sys.setrecursionlimit(10000)

# command line argumetn parsing
parser = ArgumentParser(prog='association model runner',
    description='run an association building model')
parser.add_argument('--config', type=str, dest='config', default=None,
    help=('specify a config file location; default is "config.json" in '
        'this this module\'s build directory'))
parser.add_argument('--specs', type=str, dest='specs', default=None,
    help=('specify a specs file location; default is "specs.json" in '
        'this this module\'s build directory'))
parser.add_argument('--pkg', type=bool, dest='pkg', default=True,
    help=('specify whether or not script is being run as package; '
        'without package mode, MySQL connections cannot be used '
        'and --config and --specs arguments are required'))
parser.add_argument('--log', type=str, dest='log', default=None,
    help='specify a log file location; by default the log will not be saved')
args = parser.parse_args()

# load default config/specs files if not passed via command line arguments
# when running without package, default config/specs will not load
if args.pkg is False and (args.config is None or args.specs is None):
    pr.print('warn: When running as standalone, --config and --specs ' 
        'are required.', time=True)
try:
    if args.config is None:
        args.config = resource_filename('knowledge', 'model/association/config.json')
    if args.specs is None:
        args.specs = resource_filename('knowledge', 'model/association/specs.json')
except:
    pr.print('Default config/specs file not found; fix packaging or, if'
        'not running as a package, specify a config and specs with '
        '--config and --specs.', time=True)
    quit()
    
# validate config file against specs file
config = AssociationModel.validate_config(args.config, args.specs)

if config['run']['silent']:
    pr.silence()

# add log if in arguments or config
if args.log is not None:
    pr.log(args.log)
elif config['run']['log'] not in (None, ''):
    pr.log(config['run']['log'])

# prompt for SQL password if running as package
if args.pkg:
    database = config['database']
    database['password'] = pr.getpass(f'SQL password for {database["user"]}'
        '@localhost: ', time=True)
else:
    database = None

# run model
model = AssociationModel(database)
model.run(config)