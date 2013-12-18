# PingdomBackup

Backup Pingdom result logs to a SQLite database.

## Installation

This library is easily accessible using **pip**:

```
pip install pingdombackup
```

## Example

This example does three things:

1. Updates the `probes` table (which is a persisted record of the `/probes` endpoint).
2. Gets a check record with the specified name.
3. Downloads all of the results on the specific check record.

```python
from pingdombackup import PingdomBackup

email = 'your Pingdom username'
password = 'your Pingdom password'
app_key = 'your API key'

pb = PingdomBackup(email, password, app_key, 'pingdom.db')
pb.update_probes()
check = pb.get_check_by_name('your check name')
pb.update_results(check)
```

### Logging

**PingdomBackup** uses Python's built-in logging facilities. The logger name is `PingdomBackup`. You can hook into PingdomBackup's log statements to get some idea as to what is going on in the background.

```python
import logging
logger = logging.getLogger('PingdomBackup')
logger.setLevel(logging.DEBUG)

pb.update_results(check)
```
