
import sys
import logging

from argparse import ArgumentParser
from getpass import getpass

from knowledge.model.association.basic.model import BasicAssociationModel
from knowledge.util.filesys import FilesysUtil

# needed for pickling/unpickling large objects

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

handlers = []
handlers.append(logging.StreamHandler())
frmt = '%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s'
if args.log is not None:
    handlers.append(logging.FileHandler(args.log, 'w'))
logging.basicConfig(
    format=frmt,
    level=logging.INFO,
    handlers=handlers)
logging.info('Launching association model module.')

# check for config and specs files

try:
    if args.config is None:
        args.config = FilesysUtil.package_resource(
            'knowledge.model.association.basic', 'config.json')
    if args.specs is None:
        args.specs = FilesysUtil.package_resource(
            'knowledge.model.association.basic', 'specs.json')
    if args.config is None or args.specs is None:
        raise FileNotFoundError
except Exception:
    logging.exception('Default config/specs file(s) not found; fix packaging '
        ' or, if not running as a package, specify a config and specs with '
        '"--config" and "--specs" CLI arguments.')
    exit()
    
# validate config file against specs file

logging.info('Validating configuration with specifications.')
config = BasicAssociationModel.configure(args.config, args.specs)

# reconfigure logging (if applicable)

if config['run']['log'] is not None and args.log is None:
    logger = logging.getLogger()
    logger.addHandler(logging.FileHandler(config['run']['log'], 'w'))
    logger.setLevel(getattr(logging, config['run']['verbosity'].upper()))

# run model

try:
    logging.info('Running association model.')
    model = BasicAssociationModel(config)
    model.run()
    logging.info('Assoication model run complete.')
except Exception:
    logging.exception('Fatal error while running association model.')


