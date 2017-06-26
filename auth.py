from lazr.restfulclient.errors import HTTPError
from launchpadlib.credentials import RequestTokenAuthorizationEngine
from launchpadlib.credentials import EndUserDeclinedAuthorization
from launchpadlib.launchpad import Launchpad
from oauth2client.service_account import ServiceAccountCredentials

import gspread
import time


class AuthorizeRequestTokenCli(RequestTokenAuthorizationEngine):
    def __init__(self, service_root, consumer_name):
        super(AuthorizeRequestTokenCli, self).__init__(
              service_root, consumer_name=consumer_name)

    def make_end_user_authorize_token(self, credentials, request_token):
        auth_url = credentials.get_request_token(web_root=self.web_root)
        print 'Launchpad need auth using url:'
        print auth_url
        print 'Waiting until you allow reading anything'
        while True:
            time.sleep(2)
            try:
                credentials.exchange_request_token_for_access_token(self.web_root)
                break
            except HTTPError, ex:
                if ex.response.status == 403:
                    # The user decided not to authorize this
                    # application.
                    raise EndUserDeclinedAuthorization(ex.content)
                elif ex.response.status == 401:
                    # The user has not made a decision yet.
                    pass
                else:
                    # There was an error accessing the server.
                    print "Unexpected response from Launchpad:"
                    print ex


def credentials_save_fail():
    print '> warn: fail when saving credentials'


def launchpad_login(service_root, consumer_name, credentials_file=None, version='devel'):
    auth_engine =\
        AuthorizeRequestTokenCli(service_root, consumer_name)
    lp = Launchpad.login_with(
        service_root=service_root,
        authorization_engine=auth_engine,
        credentials_file=credentials_file,
        credential_save_failed=credentials_save_fail,
        version=version)

    return lp


def gspread_login(filename):
    try:
        return gspread.authorize(
            ServiceAccountCredentials.from_json_keyfile_name(
                filename, ['https://spreadsheets.google.com/feeds']))
    except:
        print '> Problem when open google api key "{0}"'.format(filename)
        print '> For getting a new key follow steps described in:'
        print '> http://gspread.readthedocs.io/en/latest/oauth2.html'
        print '> Do not forget share documents with key owner service account!'
    return None

