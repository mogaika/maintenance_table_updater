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

# used for determine "possibly missed from table" bugs
PROJECTS = ('mos', 'fuel')
MILESTONES = (
    {
        # used in command line and printing
        'name': '6.1-mu-7-test',
	# valid milestones for bugs, used to fetch stataus and assigner
	# first item for "real" milestone,
	# because used to detect "possiby missed from table" bugs
        'targets': ('6.1-mu-7', '6.1-updates'),
	# spreadsheet id, can be taken from url
        'spreadsheet': '1h14uuug33MS6nDirQFt36Ri4yVu9PTWiCaUlsDeI7YI',
	# row index, where table header is stored
        'header_row': 4,
	# header column name => bug field names mapping
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }, {
        'name': '7.0-mu-6',
        'targets': ('7.0-mu-6', '7.0-updates'),
        'spreadsheet': '1QefXrUy80WAoTY4OHwUlqqJEvj_D96WF7lZxFpaCefI',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }, {
        'name': '7.0-mu-7',
        'targets': ('7.0-mu-7', '7.0-updates'),
        'spreadsheet': '1SHKoqsADcbee5B-7fZZXaInjcXjcVtmmtG97KSoRjno',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }, {
        'name': '8.0-mu-4',
        'targets': ('8.0-mu-4', '8.0-updates'),
        'spreadsheet': '1YoC2XnzerbT73F9gKD5O9Zi19qRD32u23L93R-jWlCo',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }, {
        'name': '9.2-mu-1',
        'targets': ('9.2-mu-1', '9.x-updates'),
        'spreadsheet': '1lKtS5bF5ulIWAJuPYE7qJh1KJ8-7SUy_qV17XGoHOD4',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }, {
        'name': '7.0-mu-8',
        'targets': ('7.0-mu-8', '7.0-updates'),
        'spreadsheet': '15m-5JooatYuuSs2nTDsbO9D8sfmKJWsJ6je1_fIrXxs',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }, {
        'name': '9.2-mu-2',
        'targets': ('9.2-mu-2', '9.x-updates'),
        'spreadsheet': '1YzABuR--FHit-qkKhRWxs9zOxfLImf_l52NvXIeSZgU',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }
)

# how many invalid rows can by in row.
# used to detect end of table
MAX_INVALID_ROWS_IN_SEQ = 5

# auth token cachingf fiels
GOOGLE_SERVICE_ACCOUNT_CREDS_JSON_FILE = 'creds-google.json'
LAUNCHPAD_SERVICE_ACCOUNT_CREDS_FILE = 'creds-launchpad.ini'
