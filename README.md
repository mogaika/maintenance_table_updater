# maintenance_table_updater
Sciprt for updating google spreadheet of maintenance bugs

## First run
- Get google api key (http://gspread.readthedocs.io/en/latest/oauth2.html), place google api json file with script and rename it to creds-google.json
- Check settings.py for your spreadhseet configuration
- Share your spreadsheet with email, provided in creds-google.json
- Start script with `python update.py -m milestone_name`
- Script print link to auth in launchpad, follow link and allow reading. This need do only once, your api key been stored in creds-launchpad.ini file.
- You can change path to creds files using env variables:
  - GOOGLE_SERVICE_ACCOUNT_FILE
  - LAUNCHPAD_SERVICE_ACCOUNT_FILE
