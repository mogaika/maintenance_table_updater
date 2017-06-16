#!/usr/bin/env python
from auth import launchpad_login
from auth import gspread_login
from gspread.exceptions import SpreadsheetNotFound
from time import gmtime, strftime

import settings
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
        self.last_empty_row = None

        try:
            self.worksheet = gspread_client.open_by_key(self.spreadsheet_name).sheet1
        except SpreadsheetNotFound, ex:
            print '> Cannot open worksheet "{0}"'.format(self.spreadsheet_name)
            print '> Probably you need share worksheet with key owner'
            raise ex

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
                if empty_rows_in_seq == 0:
                    self.last_empty_row = irow
                empty_rows_in_seq += 1

    def get_new_bug_row(self):
        need_cols = max([i for i in self.table_assoc_columns.itervalues()])
        bug_cells = self._raw_row_cells(self.last_empty_row, need_cols)
        bug = {'_raw_': bug_cells}
        self.last_empty_row += 1
        return bug

    def queue_bug_update(self, bug):
        cells = bug['_raw_']
        changes = {}
        for name, icol in self.table_assoc_columns.iteritems():
            if name in bug:
                cell = cells[icol]
                if cell.value != bug[name]:
                    changes[name] = (cell.value, bug[name])
                    cell.value = bug[name]
                    self.update_queue.append(cells[icol])
        return changes

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

    @staticmethod
    def _assignee_to_string(assignee):
        return '{0} ({1})'.format(assignee.display_name, assignee.name)

    def bug_update_row(self, bugid, table, row, milestone_dict):
        self.row_set(row, 'id', bugid)
        bug = self.bug_get_info(bugid)
        if bug is None:
            print '[{0}] Cannot fetch. Probably private.'.format(bugid)
        else:
            for key in ['title', 'information_type', 'web_link', 'private']:
                self.row_set(row, key, getattr(bug, key))
    
            task, mu_id = self.bug_get_task_for_mu(bug.bug_tasks, milestone_dict['targets'])
            if task is not None:
                if mu_id != 0:
                    self.row_add_note(row, 'targeted on "{0}"'.format(milestone_dict['targets'][mu_id]))
                if task.assignee is not None:
                    self.row_set(row, 'assignee', self._assignee_to_string(task.assignee))
    
                for key in ['importance', 'status']:
                    self.row_set(row, key, getattr(task, key))
            else:
                self.row_add_note(row, 'missed target')
        
        changes = table.queue_bug_update(row)
        if bug is not None:
            print '[{0}] Changes: {1}'.format(bugid, changes if task else "Cannot detect mu")
        return

    def update_table(self, milestone_dict):
        table = CategorizationTable(self._gc, milestone_dict)

        bugs_ids_processed = []

        for row in table.get_bugs_rows():
            changed_row = self.bug_update_row(row['id'], table, row, milestone_dict)
            bugs_ids_processed.append(row['id'])

        for project_name in settings.PROJECTS:
            print 'Cheking for new bugs in {}'.format(project_name)
            project = self._lp.projects[project_name]
            milestone = project.getMilestone(name=milestone_dict['targets'][0])

            for task in milestone.searchTasks():
                bug_id = task.bug.id
                if bug_id not in bugs_ids_processed:
                    print 'New bug {}'.format(bug_id)
                    bugs_ids_processed.append(bug_id)
                    row = table.get_new_bug_row()
                    self.row_add_note(row, 'auto-added {}'.format(strftime("%Y-%m-%d %H:%M", gmtime())))
                    self.bug_update_row(bug_id, table, row, milestone_dict)

        table.flush_updates()

    @staticmethod
    def row_add_note(row, note):
        if 'notes' in row:
            current_note = row['notes'] + ';'
            if note not in current_note:
                row['notes'] = current_note + note
        else:
            row['notes'] = note

    @staticmethod
    def row_set(row, key, value):
        if key == 'web_link':
            # do not change link, if we already have one
            if key in row and row[key] != '':
                return
        elif key == 'private':
            value = str(value).upper()
        row[key] = value

    @staticmethod
    def bug_get_task_for_mu(tasks, targets):
        task, target_id = None, None
        for current_task in tasks:
            for i, target in enumerate(targets):
                ms = current_task.milestone
                if ms is not None:
                    if current_task.milestone.name == target:
                        if task == None or i < target_id:
                            task, target_id = current_task, i
        return task, target_id


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
		print 'Choose milestone to update from list. Use --help!'
		return
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

    gs = gspread_login(settings.GOOGLE_SERVICE_ACCOUNT_CREDS_JSON_FILE)

    if lp is None or gs is None:
        return

    updater = CategorizationUpdater(lp, gs)
    updater.update_table(mu)

if __name__ == '__main__':
    main()

