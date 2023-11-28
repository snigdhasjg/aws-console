import boto3
import logging
import os

from botocore.utils import JSONFileCache

LOG = logging.getLogger(__name__)


class TokenGenerationException(Exception):
    """Exception for credential not having token"""
    pass


def credentials(profile_name, region_name):
    LOG.debug(f'Creating boto3 session for profile {profile_name} and region {region_name}')
    session = boto3.Session(profile_name=profile_name, region_name=region_name)

    __update_credential_provider_cache(session)

    creds = session.get_credentials()
    if creds.token is None:
        LOG.error("No session credential found")
        raise TokenGenerationException()

    return creds, session.region_name


def __update_credential_provider_cache(session):
    """Setting up a custom cache implementation like aws cli"""
    cache_dir = os.path.expanduser(os.path.join('~', '.aws', 'cli', 'cache'))

    cred_chain = session._session.get_component('credential_provider')
    json_file_cache = JSONFileCache(cache_dir)

    def _update(provider_name):
        cred_chain.get_provider(provider_name).cache = json_file_cache

    provider_for_cache = [
        'assume-role',
        'assume-role-with-web-identity',
        'sso'
    ]

    [_update(each_provider) for each_provider in provider_for_cache]
