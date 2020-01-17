
import sys
import logging

from pkgutil import get_data
from argparse import ArgumentParser
from getpass import getpass

from knowledge.model.association.model import AssociationModel

# needed for pickling/unpickling large trees
sys.setrecursionlimit(10000)

# command line argument parsing
parser = ArgumentParser(prog='association model runner',
    description='run an association building model')
parser.add_argument('--config', type=str, dest='config', default=None,
    help=('specify a config file location; default is "config.json" in '
        'this this module\'s build directory'))
parser.add_argument('--specs', type=str, dest='specs', default=None,
    help=('specify a specs file location; default is "specs.json" in '
        'this this module\'s build directory'))
parser.add_argument('--log', type=str, dest='log', default=None,
    help='specify a log file location; by default the log will not be saved')
args = parser.parse_args()

# configure logging
hanlders = []
hanlders.append(logging.StreamHandler())
if args.log is not None:
    hanlders.append(logging.FileHandler(args.log, 'w'))
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s',
    level=logging.INFO,
    handlers=hanlders)
logging.info('Running association model module.')

# check for config and specs files
try:
    if args.config is None:
        args.config = get_data('knowledge', 'model/association/config.json')
    if args.specs is None:
        args.specs = get_data('knowledge', 'model/association/specs.json')
    if args.config is None or args.specs is None:
        raise FileNotFoundError
except Exception:
    logging.exception('Default config/specs file(s) not found; fix packaging '
        ' or, if not running as a package, specify a config and specs with '
        '"--config" and "--specs" CLI arguments.')
    exit()
    
# validate config file against specs file
logging.info('Validating configuration with specifications.')
config = AssociationModel.validate_config(args.config, args.specs)

# database credentials handling
if AssociationModel.mysql():
    database = config['database']
    if database['user'] is None:
        database['user'] = input('SQL username for localhost: ')
    if database['user'] is None or database['password'] is None:
        logging.info(f'SQL password for {database["user"]}@localhost: ')
        database['password'] = getpass('')
else:
    logging.info('Model running without SQL environment.')

# run model
try:
    model = AssociationModel(database)
    model.run(config)
except Exception:
    logging.exception('Fatal error while running association model.')
    exit()

logging.info('Assoication model run complete.')
