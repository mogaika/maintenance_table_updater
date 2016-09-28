from lazr.restfulclient.errors import HTTPError
from launchpadlib.launchpad import Launchpad
from launchpadlib.credentials import (
    Credentials,
    AuthorizeRequestTokenWithBrowser,
    EndUserDeclinedAuthorization
)
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import time
from pprint import pprint

TABLE_MILESTONE = [
    {
        'name': ('6.1-mu-7', '6.1-updates'),
        'spreadsheet': '1h14uuug33MS6nDirQFt36Ri4yVu9PTWiCaUlsDeI7YI',
        #'name': ('7.0-mu-6', '7.0-updates'),
        #'spreadsheet': '1QefXrUy80WAoTY4OHwUlqqJEvj_D96WF7lZxFpaCefI',
        'header_row': 4  # top row with colmuns names
    }
]

TABLE_COLUMNS = {
    'id': 'Id',
    'web_link': 'Web link',
    'status': 'Status',
    'title': 'Title',
    'importance': 'Importance',
    'assignee': 'Assignee',
    'information_type': 'Type',
    'private': 'Private (T/F)',
    'notes': 'Notes',
}

# how many invalid rows can by in row.
# used to detect end of table
MAX_INVALID_ROWS_IN_SEQ = 3


# auth token caching
GOOGLE_SERVICE_ACCOUNT_CREDS_JSON_FILE = 'google-creds.json'
LAUNCHPAD_SERVICE_ACCOUNT_CREDS_FILE = 'launchpad-creds.ini'


class LaunpadUpdater:
    def __init__(self, launchpad, gspread_client):
        self._lp = launchpad
        self._gc = gspread_client

    def bug_get_info(self, bugid):
        try:
            ret = self._lp.bugs[bugid]
        except KeyError:
            ret = None
        return ret

    def user_link_to_name(self, lp_user_link):
        login = lp_user_link.split('/')[-1][1:]
        for user in self._lp.people.find(text=login).entries:
            if user['self_link'] == lp_user_link:
                return '{0} ({1})'.format(user['display_name'], login)
        return login

    @staticmethod
    def bug_get_task_for_mu(tasks, mus):
        # TODO: improve (8.0-updates must be like 8.0-mu7)
        for task in tasks:
            for mu in mus:
                try:
                    if task['milestone_link'].endswith(mu):
                        print 'mu detected from link {0}'.format(task['milestone_link'])
                        return task
                except Exception, ex:
                    from pprint import pprint
                    pprint(task)
                    print ex
        return None

    @staticmethod
    def update_table_row_key(worksheet, irow, table_assoc, key, val):
        if key in table_assoc:
            worksheet.update_cell(irow, table_assoc[key], val)
        else:
            print 'warn: assoc table not contain {0} key'.format(key)

    def update_table_row(self, mu_name, worksheet, irow, table_assoc):
        bugid = worksheet.cell(irow, table_assoc['id']).value
        if bugid.isdigit():
            original_notes = worksheet.cell(irow, table_assoc['notes']).value
            try:
                worksheet.update_cell(irow, table_assoc['notes'], ' *** updating *** |' + original_notes)
                bug = self.bug_get_info(int(bugid))
                if bug is not None:
                    print '[{0}] info fetched'.format(bugid)
    
                    # process strings
                    for key in ['title', 'information_type']:
                        self.update_table_row_key(worksheet, irow, table_assoc, key, getattr(bug, key))
                    
                    # if link is present, not update
                    for key in ['web_link']:
                        if worksheet.cell(irow, table_assoc[key]).value == '':
                            self.update_table_row_key(worksheet, irow, table_assoc, key, getattr(bug, key))
    
                    # process booleans
                    for key in ['private']:
                        self.update_table_row_key(worksheet, irow, table_assoc, key, str(getattr(bug, key)).upper())
    
                    task = self.bug_get_task_for_mu(bug.bug_tasks.entries, mu_name)
                    if task is not None:
                        # task assignee link to name
                        task['assignee'] = self.user_link_to_name(task['assignee_link'])
    
                        # process task arguments
                        for key in ['importance', 'status', 'assignee']:
                            self.update_table_row_key(worksheet, irow, table_assoc, key, task[key])
                    else:
                        print '[{0}] cannot detect mu of bug'.format(bugid)
                else:
                    print '[{0}] cannot fetch, probably private'.format(bugid)
            finally:
                worksheet.update_cell(irow, table_assoc['notes'], original_notes)
            return True
        else:
            return False

    def update_table(self, mu_name, spreadsheet, header_row):
        wks = self._gc.open_by_key(spreadsheet).sheet1
        print 'Processing {0} categorization table'.format(mu_name)
        header = wks.row_values(header_row)

        table_assoc_columns = dict()
        for icol in xrange(len(header)):
            column_title = header[icol].strip().lower()
            if column_title != '':
                for key, column_text in TABLE_COLUMNS.iteritems():
                    if column_text.strip().lower() == column_title:
                        if key in table_assoc_columns:
                            raise Exception('Probably incorrect header row')
                        else:
                            table_assoc_columns[key] = icol + 1
                            break

        print 'Columns association:', table_assoc_columns
        print 'Steping over table rows...'

        irow = header_row + 1
        empty_rows_in_seq = 0
        while empty_rows_in_seq < MAX_INVALID_ROWS_IN_SEQ:
            if self.update_table_row(mu_name, wks, irow, table_assoc_columns):
                empty_rows_in_seq = 0
            else:
                empty_rows_in_seq += 1
            irow += 1

    def update_tables(self, milestone_tables):
        for millestone in milestone_tables:
            self.update_table(
                millestone['name'],
                millestone['spreadsheet'],
                millestone['header_row'])


class AuthorizeRequestTokenWithoutBrowser(AuthorizeRequestTokenWithBrowser):
    def __init__(self, service_root, application_name, consumer_name=None,
                 credential_save_failed=None, allow_access_levels=None):
        super(AuthorizeRequestTokenWithoutBrowser, self).__init__(
              service_root, application_name, None,
              credential_save_failed)

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
    print 'warn: fail when saving credentials'


def main():
    updater = LaunpadUpdater(
        Launchpad.login_with(
            service_root='production',
            authorization_engine=AuthorizeRequestTokenWithoutBrowser(
                service_root='production',
                application_name='mirantis qa table updater'
            ),
            credentials_file=LAUNCHPAD_SERVICE_ACCOUNT_CREDS_FILE,
            credential_save_failed=credentials_save_fail
        ),
        gspread.authorize(
            ServiceAccountCredentials.from_json_keyfile_name(
                GOOGLE_SERVICE_ACCOUNT_CREDS_JSON_FILE,
                ['https://spreadsheets.google.com/feeds']
            )
        )
    )

    updater.update_tables(TABLE_MILESTONE)

if __name__ == '__main__':
    main()
