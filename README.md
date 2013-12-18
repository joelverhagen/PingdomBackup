# PingdomBackup

Backup Pingdom result logs to a SQLite database.

## Installation

This library is easily accessible using **pip**:

```
pip install pingdombackup
```

## Console Usage

This package includes a script for easy command-line usage. It is installed to your Python `scripts` directory. This depends on your system.

```
pingdombackup --help

usage: pingdombackup [-h] [-v] -e EMAIL -p PASSWORD -a APP_KEY [-d DB_PATH]
                     [-n CHECK_NAME] [--offine-check] [--no-update-results]
                     [--update-probes] [--update-checks] [--verbose]

Backup Pingdom result logs to a SQLite database.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show the version and exit (default: False)
  -e EMAIL, --email EMAIL
                        your Pingdom email address (used for logging in)
  -p PASSWORD, --password PASSWORD
                        your Pingdom password (used for logging in)
  -a APP_KEY, --app-key APP_KEY
                        a valid Pingdom API application key, see:
                        https://my.pingdom.com/account/appkeys
  -d DB_PATH, --db-path DB_PATH
                        a path to the SQLite database used for storage
                        (default: pingdom.db)
  -n CHECK_NAME, --check-name CHECK_NAME
                        the name of the check to update (default: None)
  --offine-check        get the check ID by name from the database, instead of
                        the Pingdom API (default: False)
  --no-update-results   do not update the results for the specified check
                        (default: False)
  --update-probes       update the probes (default: False)
  --update-checks       update the checks for your account (default: False)
  --verbose             trace progress (default: False)
```

## Script Usage

### Updating the database

This example does four things:

1. Updates the `probes` table (which is a persisted record of the `/probes` endpoint).
2. Updates the `checks` tabls (which is a persisted record of the `/checks` endpoint).
3. Gets a check record with the specified name from the local database.
4. Downloads all of the results on the specific check record.

```python
from pingdombackup import PingdomBackup

email = 'your Pingdom username'
password = 'your Pingdom password'
app_key = 'your API key'

pb = PingdomBackup(email, password, app_key, 'pingdom.db')
pb.update_probes()
pn.update_checks()
check = pb.get_check_by_name('your check name')
pb.update_results(check)
```

### Logging

PingdomBackup uses Python's built-in logging facilities. The logger name is `PingdomBackup`. You can hook into PingdomBackup's log statements to get some idea as to what is going on in the background.

Coincidentally, `logging.INFO` is used for the console tool's `--verbose` option.

```python
import logging
logger = logging.getLogger('PingdomBackup')
logger.setLevel(logging.DEBUG)

pb.update_results(check)
```

### Fetching results

The `Database` convenience class is made available so fetching data from the SQLite database is a jiffy.

```python
import sqlite3
from datetime import datetime

from pingdombackup import Database

# get all "up" or "down" records
db = Database('pingdom.db')
records = db.get_records('results', where='status IN (?, ?)', order_by='time ASC', parameters=('down', 'up'))

# find status changes
current_status = None
current_start = None
for record in records:
    # convert to Python datetime
    time = datetime.fromtimestamp(record['time'])
    if current_status == None:
        current_status = record['status']
        current_start = time
    elif record['status'] != current_status:
        # report the status change and duration
        print('{0}: {1} -> {2} ({1}-time: {3})'.format(
            time,
            current_status,
            record['status'],
            time - current_start)
        )
        current_status = record['status']
        current_start = time
```
