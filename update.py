from launchpadlib.launchpad import Launchpad
from oauth2client.service_account import ServiceAccountCredentials
import gspread

from pprint import pprint

TABLE_MILESTONE = [
    {
        'name': '6.1-mu-7',
        'spreadsheet': '1h14uuug33MS6nDirQFt36Ri4yVu9PTWiCaUlsDeI7YI',
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
    'information_type': 'Info Type',
    'private': 'Private (T/F)',
}

MAX_INVALID_ROWS_IN_SEQ = 3  # how many invalid rows to detect end of table

GOOGLE_SERVICE_ACCOUNT_CREDS_JSON_FILE = 'google-creds.json'


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

    def bug_get_task_for_mu(self, tasks, mu):
        # TODO: improve (8.0-updates must be like 8.0-mu7)
        for task in tasks:
            if task['milestone_link'].endswith(mu):
                return task
        return None

    def update_table_row(self, mu_name, worksheet, irow, table_assoc):
        bugid = worksheet.cell(irow, table_assoc['id']).value
        if bugid.isdigit():
            bug = self.bug_get_info(int(bugid))

            if bug is not None:
                print '[{0}] info fetched'.format(bugid)

                # process strings
                for key in ['web_link', 'title', 'information_type']:
                    if key in table_assoc:
                        worksheet.update_cell(irow, table_assoc[key],
                                              getattr(bug, key))

                # process booleans
                for key in ['private']:
                    if key in table_assoc:
                        worksheet.update_cell(irow, table_assoc[key],
                                              str(getattr(bug, key)).upper())

                task = self.bug_get_task_for_mu(bug.bug_tasks.entries, mu_name)
                if task is not None:
                    # task assignee link to name
                    task['assignee'] = self.user_link_to_name(
                        task['assignee_link'])

                    # process task arguments
                    for key in ['importance', 'status', 'assignee']:
                        if key in table_assoc:
                            worksheet.update_cell(irow, table_assoc[key],
                                                  task[key])
                else:
                    print '[{0}] cannot detect mu task'.format(bugid)
            else:
                print '[{0}] cannot fetch, probably private'.format(bugid)

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


def main():
    updater = LaunpadUpdater(
        Launchpad.login_anonymously(
            'just testing', 'production', version='devel'),
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
