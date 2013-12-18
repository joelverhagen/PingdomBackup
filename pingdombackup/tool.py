import argparse
import sys
import logging
import pkg_resources
from . import __version__
from .PingdomBackup import PingdomBackup

def tool_main():
    # this is done without ArgumentParser so required args are not enforced
    if '-v' in sys.argv or '--version' in sys.argv:
        print(__version__)
        sys.exit(0)

    # initialize the parser
    parser = argparse.ArgumentParser(
        prog='pingdombackup',
        description='Backup Pingdom result logs to a SQLite database.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS)

    # meta arguments
    parser.add_argument('-v', '--version',
        dest='version', action='store_true', default=False,
        help='show the version and exit')

    # required arguments
    parser.add_argument('-e', '--email',
        dest='email', required=True,
        help='your Pingdom email address (used for logging in)')
    parser.add_argument('-p', '--password',
        dest='password', required=True,
        help='your Pingdom password (used for logging in)')
    parser.add_argument('-a', '--app-key',
        dest='app_key', required=True,
        help='a valid Pingdom API application key, see: https://my.pingdom.com/account/appkeys')
    parser.add_argument('-d', '--db-path',
        dest='db_path', default='pingdom.db',
        help='a path to the SQLite database used for storage')

    # conditionally required arguments
    parser.add_argument('-n', '--check-name',
        dest='check_name', default=None,
        help='the name of the check to update')

    # optional arguments
    parser.add_argument('--offine-check',
        dest='offline_check', action='store_true', default=False,
        help='get the check ID by name from the database, instead of the Pingdom API')
    parser.add_argument('--no-update-results',
        dest='no_update_results', action='store_true', default=False,
        help='do not update the results for the specified check')
    parser.add_argument('--update-probes',
        dest='update_probes', action='store_true', default=False,
        help='update the probes')
    parser.add_argument('--update-checks',
        dest='update_checks', action='store_true', default=False,
        help='update the checks for your account')
    parser.add_argument('--verbose',
        dest='verbose', action='store_true', default=False,
        help='trace progress')

    # parse
    args = parser.parse_args()

    if not args.no_update_results and args.check_name is None:
        parser.error('-n/--check-name is required when updating results')

    if args.verbose:
        logger = logging.getLogger('PingdomBackup')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.INFO)

    pb = PingdomBackup(args.email, args.password, args.app_key, args.db_path)

    if args.update_probes:
        pb.update_probes()

    if args.update_checks or (not args.no_update_results and not args.offline_check):
        pb.update_checks()

    if not args.no_update_results:
        check = pb.get_check_by_name(args.check_name)
        if check is None:
            parser.error('no check with name "{0}" was found'.format(args.check_name))
        pb.update_results(check)

if __name__ == '__main__':
    tool_main()
