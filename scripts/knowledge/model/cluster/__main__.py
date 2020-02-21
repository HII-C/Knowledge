import sys
import logging

from argparse import ArgumentParser
from getpass import getpass

from knowledge.model.cluster.model import ClusterModel
from knowledge.util.filesys import FilesysUtil

# needed for pickling/unpickling large objects

sys.setrecursionlimit(10000)

# command line argument parsing

parser = ArgumentParser(prog='cluster model runner',
    description='run an cluster building model')
parser.add_argument('--config', type=str, dest='config', default=None,
    help=('specify a config file location; default is "config.json" in '
        'this this module\'s build directory'))
parser.add_argument('--specs', type=str, dest='specs', default=None,
    help=('specify a specs file location; default is "specs.json" in '
        'this this module\'s build directory'))
parser.add_argument('--log', type=str, dest='log', default=None,
    help='specify a log file location; by default the log will not be saved')
parser.add_argument('--debug', action='store_false', dest='debug')
args = parser.parse_args()

# configure logging

handlers = []
handlers.append(logging.StreamHandler())
frmt = '%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s'
level=logging.DEBUG if args.debug else logging.INFO
if args.log is not None:
    handlers.append(logging.FileHandler(args.log, 'w'))

logging.basicConfig(
    format=frmt,
    level=level,
    handlers=handlers)
logging.info('Running cluster model module.')

# check for config and specs files

try:
    if args.config is None:
        args.config = FilesysUtil.package_resource(
            'knowledge.model.cluster', 'config.json')
    if args.specs is None:
        args.specs = FilesysUtil.package_resource(
            'knowledge.model.cluster', 'specs.json')
    if args.config is None or args.specs is None:
        raise FileNotFoundError
except Exception:
    logging.exception('Default config/specs file(s) not found; fix packaging '
        ' or, if not running as a package, specify a config and specs with '
        '"--config" and "--specs" CLI arguments.')
    exit()

# validate config file against specs file

logging.info('Validating configuration with specifications.')
config = ClusterModel.validate_config(args.config, args.specs)

# reconfigure logging (if applicable)

if config['run']['log'] is not None and args.log is None:
    handlers.append(logging.FileHandler(config['run']['log'], 'w'))
    logging.basicConfig(
        format=frmt,
        level=level,
        handlers=handlers)

# database credentials handling

if ClusterModel.mysql():
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
    model = ClusterModel(database)
    model.run(config)
    model.create_indexes(config)
except Exception:
    logging.exception('Fatal error while running cluster model.')
    exit()

logging.info('Cluster model run complete.')