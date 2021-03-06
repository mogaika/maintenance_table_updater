import os


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
	# first item for "real" milestone, second - to detect if milestone been changed
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
    }, {
        'name': '8.0-mu-5',
        'targets': ('8.0-mu-5', '8.0-updates'),
        'spreadsheet': '1ThelYPnQyzne3-sfKaxmuEhAYi_pBOlTeNaD3STS_D8',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }, {
        'name': '9.2-mu-3',
        'targets': ('9.2-mu-3', '9.x-updates'),
        'spreadsheet': '1y_Y_TPnT87KmeT50tFMQTyIKMZBFW_ZYDyvIShqr5HA',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }, {
        'name': '8.0-mu-6',
        'targets': ('8.0-mu-6', '8.0-updates'),
        'spreadsheet': '1JnrK9zHjy49_EPESll8d8XZ9Pr63QJOkZU2SgkxpxiQ',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }, {
        'name': '9.2-mu-4',
        'targets': ('9.2-mu-4', '9.x-updates'),
        'spreadsheet': '1xfYxYW6Y-3xn4DAVpDjf6a5urqELLTULzGKzyF5UAnM',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }, {
        'name': '9.2-mu-5',
        'targets': ('9.2-mu-5', '9.x-updates'),
        'spreadsheet': '1oeZ1qqE6URFHA1mV0ucT6tQYjOeV3Sv_uNCPOa8ahyo',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }, {
        'name': '9.2-mu-6',
        'targets': ('9.2-mu-6', '9.x-updates'),
        'spreadsheet': '1wmPmB3DGZBDRP97dutWjWg768vZYgmwwqQRxp4xy7Mg',
        'header_row': 4,
        'columns_names': TABLE_COLUMNS_NAMES_DEFAULT,
    }
)

# how many invalid rows can by in row
# used to detect end of table
MAX_INVALID_ROWS_IN_SEQ = 5

# auth token cachingf fiels
GOOGLE_SERVICE_ACCOUNT_CREDS_JSON_FILE = os.environ.get('GOOGLE_SERVICE_ACCOUNT_FILE', 'creds-google.json')
LAUNCHPAD_SERVICE_ACCOUNT_CREDS_FILE = os.environ.get('LAUNCHPAD_SERVICE_ACCOUNT_FILE', 'creds-launchpad.ini')

