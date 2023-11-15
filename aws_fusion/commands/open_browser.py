import os
import pyperclip
import webbrowser
import sys
import logging

from ..aws.session import credentials
from ..aws.api import signin_url

LOG = logging.getLogger(__name__)


def setup(subparsers, parent_parser):
    summary = 'Open a web browser for graphical access to the AWS Console'
    parser = subparsers.add_parser('open-browser', description=summary, help=summary, parents=[parent_parser])
    parser.set_defaults(func=run)

    parser.add_argument('-P', '--profile', default=os.getenv("AWS_PROFILE"), help="The AWS profile to create the pre-signed URL with")
    parser.add_argument('-R', '--region', default=os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION")), help="The AWS Region to send the request to")

    no_browser_group = parser.add_mutually_exclusive_group()
    no_browser_group.add_argument('--clip', action='store_true', help="don't open the web browser, but copy the signin URL to clipboard")
    no_browser_group.add_argument('--stdout', action='store_true', help="don't open the web browser, but echo the signin URL to stdout")


def run(args):
    creds, region_name = credentials(args.profile, args.region)
    url = signin_url(creds, region_name)
    LOG.debug(f'Generated aws console URL: {url}')

    if args.clip:
        pyperclip.copy(url)
    elif args.stdout:
        print(url)
    elif not webbrowser.open_new_tab(url):
        LOG.error('No browser found on the system')
        sys.exit("No browser found. Try --help for other options")
