TABLE_COLUMNS_NAMES_DEFAULT = {
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

MILESTONES = (
    # first milestone is default
    {
        'name': '6.1-mu-7-test',
        'targets': ('6.1-mu-7', '6.1-updates'),
        'spreadsheet': '1h14uuug33MS6nDirQFt36Ri4yVu9PTWiCaUlsDeI7YI',
        'header_row': 4,  # columns names row index
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }, {
        'name': '7.0-mu-6',
        'targets': ('7.0-mu-6', '7.0-updates'),
        'spreadsheet': '1QefXrUy80WAoTY4OHwUlqqJEvj_D96WF7lZxFpaCefI',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }
)

# how many invalid rows can by in row.
# used to detect end of table
MAX_INVALID_ROWS_IN_SEQ = 3

# auth token caching
GOOGLE_SERVICE_ACCOUNT_CREDS_JSON_FILE = 'creds-google.json'
LAUNCHPAD_SERVICE_ACCOUNT_CREDS_FILE = 'creds-launchpad.ini'
