#!/usr/bin/env python
from launchpad import launchpad_login
from oauth2client.service_account import ServiceAccountCredentials
import settings
import gspread
import argparse


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
        self.spreadsheet_name = milestone['spreadsheet']
        self.name = milestone['name']
        self.targets = milestone['targets']
        self.header_row = milestone['header_row']
        self.columns_names = milestone['columns_names']
        self.update_queue = []

        self.worksheet = gspread_client.open_by_key(self.spreadsheet_name).sheet1

        self.table_assoc_columns = self._generate_assoc_table()
        print 'Assoc table generated for {0}'.format(self.name)
        print self.table_assoc_columns

    def _raw_row_cells(self, irow, count):
        start_cell = self.worksheet.get_addr_int(irow, 1)
        end_cell = self.worksheet.get_addr_int(irow, count + 1)
        return self.worksheet.range('%s:%s' % (start_cell, end_cell))

    @staticmethod
    def _bug_id_is_valid(bug_id):
        return bug_id.isdigit()

    def get_bugs_rows(self):
        irow = self.header_row
        need_cols = max([i for i in self.table_assoc_columns.itervalues()])

        empty_rows_in_seq = 0
        while empty_rows_in_seq < settings.MAX_INVALID_ROWS_IN_SEQ:
            irow += 1

            bug_cells = self._raw_row_cells(irow, need_cols)

            bug = {'_raw_': bug_cells}
            for name, icol in self.table_assoc_columns.iteritems():
                bug[name] = bug_cells[icol].value

            if self._bug_id_is_valid(bug['id']):
                yield bug
                empty_rows_in_seq = 0
            else:
                empty_rows_in_seq += 1

    def queue_bug_update(self, bug):
        cells = bug['_raw_']
        for name, icol in self.table_assoc_columns.iteritems():
            if name in bug:
                cell = cells[icol]
                if cell.value != bug[name]:
                    cell.value = bug[name]
                    self.update_queue.append(cells[icol])

    def flush_updates(self):
        print 'Flushing {0} changes to spreadsheet "{1}"'.format(len(self.update_queue), self.spreadsheet_name)
        if len(self.update_queue) > 0:
            self.worksheet.update_cells(self.update_queue)


class CategorizationUpdater:
    def __init__(self, launchpad_client, gspread_client):
        self._lp = launchpad_client
        self._gc = gspread_client

    def bug_get_info(self, bug_id):
        try:
            ret = self._lp.bugs[bug_id]
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

        for row in table.get_bugs_rows():
            bug = self.bug_get_info(row['id'])
            if bug is None:
                print '[{0}] Cannot fetch. Probably private.'.format(row['id'])
                continue

            print '[{0}] Fetched.'.format(row['id'])

            for key in ['title', 'information_type', 'web_link', 'private']:
                self.row_set(row, key, getattr(bug, key))

            task = self.bug_get_task_for_mu(bug.bug_tasks.entries, milestone_dict['targets'])
            if task is not None:
                self.row_set(row, 'assignee', self.user_link_to_name(task['assignee_link']))

                for key in ['importance', 'status']:
                    self.row_set(row, key, task[key])
            else:
                print '[{0}] Cannot detect mu of bug'.format(row['id'])
            table.queue_bug_update(row)

        table.flush_updates()

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
    def bug_get_task_for_mu(tasks, targets):
        for task in tasks:
            for target in targets:
                link = task['milestone_link']
                if link is not None and link.endswith(target):
                    return task
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--milestone', help='categorization table milestone to update')
    parser.add_argument('-l', '--list', help='list available milestones', action='store_true')
    args = parser.parse_args()

    if args.list:
        for milestone in settings.MILESTONES:
            print milestone['name']
        return

    mu = None
    if args.milestone is None:
        mu = settings.MILESTONES[0]
    else:
        for milestone in settings.MILESTONES:
            if args.milestone == milestone['name']:
                mu = milestone
                break
        if mu is None:
            print 'Cannot find milestone {0}'.format(args.milestone)
            return

    print 'Updating {0} categorization table'.format(mu['name'])

    lp = launchpad_login('production', 'mirantis qa table updater',
                         settings.LAUNCHPAD_SERVICE_ACCOUNT_CREDS_FILE)

    gs = gspread.authorize(
        ServiceAccountCredentials.from_json_keyfile_name(
            settings.GOOGLE_SERVICE_ACCOUNT_CREDS_JSON_FILE,
            ['https://spreadsheets.google.com/feeds']
        )
    )

    updater = CategorizationUpdater(lp, gs)
    updater.update_table(mu)

if __name__ == '__main__':
    main()

