from launchpad import launchpad_login
from oauth2client.service_account import ServiceAccountCredentials
import settings
import gspread


class CategorizationTable:
    def _generate_assoc_table(self):
        table_assoc_columns = dict()
        header = self.worksheet.row_values(self.header_row)
        for icol in xrange(len(header)):
            column_title = header[icol].strip().lower()
            if column_title != '':
                for key, column_text in self.columns_names.iteritems():
                    if column_text.strip().lower() == column_title:
                        if key in table_assoc_columns:
                            raise Exception('Probably incorrect header row')
                        else:
                            table_assoc_columns[key] = icol
                            break

        return table_assoc_columns

    def __init__(self, gspread_client, milestone):
        self.worksheet =\
            gspread_client.open_by_key(milestone['spreadsheet']).sheet1

        self.names = milestone['names']
        self.header_row = milestone['header_row']
        self.columns_names = milestone['columns_names']

        self.table_assoc_columns = self._generate_assoc_table()
        print 'Assoc table generated for {0}'.format(self.names)
        print self.table_assoc_columns

    def _get_raw_row(self, irow, icol_end):
        """start_cell = self.worksheet.get_addr_int(irow, 1)
        end_cell = self.worksheet.get_addr_int(irow, icol_end)
        row_cells = self.worksheet.range('%s:%s' % (start_cell, end_cell))
        return [cell.value for cell in row_cells]
        """
        for row in range(min_row, max_row + 1):
            yield tuple(self.cell(row=row, column=column)
                        for column in range(min_col, max_col + 1))
        from pprint import pprint
        pprint(dir(self.worksheet))

    @staticmethod
    def _bug_id_is_valid(bug_id):
        return bug_id.isdigit()

    def bug_deserialize(self, row):
        bug = dict()
        for name, icol in self.table_assoc_columns.iteritems():
            bug[name] = row[icol]
        return bug

    def get_bugs_rows(self):
        irow = self.header_row
        max_cols = max([i for i in self.table_assoc_columns.itervalues()]) + 1

        empty_rows_in_seq = 0
        while empty_rows_in_seq < settings.MAX_INVALID_ROWS_IN_SEQ:
            irow += 1
            bug_row = self._get_raw_row(irow, max_cols)
            bug = self.bug_deserialize(bug_row)
            if self._bug_id_is_valid(bug['id']):
                yield irow, bug
                empty_rows_in_seq = 0
            else:
                empty_rows_in_seq += 1

    #def update_bug(self, bug):


class CategorizationUpdater:
    def __init__(self, launchpad_client, gspread_client):
        self._lp = launchpad_client
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

    def update_table(self, milestone_dict):
        table = CategorizationTable(self._gc, milestone_dict)

        for irow, row in table.get_bugs_rows():
            bug = self.bug_get_info(row['id'])
            print row
            if bug is None:
                print '[{0}] Cannot fetch. Probably private.'.format(row['id'])
                continue

            print '[{0}] Fetched.'.format(row['id'])

            for key in ['title', 'information_type', 'web_link', 'private']:
                self.row_set(row, key, getattr(bug, key))

            task = self.bug_get_task_for_mu(bug.bug_tasks.entries, milestone_dict['names'])
            if task is not None:
                self.row_set(row, 'assignee', self.user_link_to_name(task['assignee_link']))

                for key in ['importance', 'status']:
                    self.row_set(row, key, task[key])
            else:
                print '[{0}] Cannot detect mu of bug'.format(row['id'])

    @staticmethod
    def row_set(row, key, value):
        if key in row:
            if key == 'web_link':
                # do not change link, if we already have one
                if row[key] != '':
                    return
            elif key == 'private':
                value = str(value).upper()
            row[key] = value
        else:
            print 'warn: missed "{0}" field'.format(key)

    @staticmethod
    def bug_get_task_for_mu(tasks, mus):
        for task in tasks:
            for mu in mus:
                link = task['milestone_link']
                if link is not None and link.endswith(mu):
                    print 'mu detected from link {0}'.format(task['milestone_link'])
                    return task
        return None


def main():
    lp = launchpad_login('production', 'mirantis qa table updater',
                         settings.LAUNCHPAD_SERVICE_ACCOUNT_CREDS_FILE)

    gs = gspread.authorize(
        ServiceAccountCredentials.from_json_keyfile_name(
            settings.GOOGLE_SERVICE_ACCOUNT_CREDS_JSON_FILE,
            ['https://spreadsheets.google.com/feeds']
        )
    )

    updater = CategorizationUpdater(lp, gs)
    updater.update_table(settings.MILESTONES[0])

if __name__ == '__main__':
    main()
