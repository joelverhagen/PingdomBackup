# PingdomBackup

Backup Pingdom result logs to a SQLite database.

## Example

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

## Logging

**PingdomBackup** uses Python's built-in logging facilities. The logger name is `PingdomBackup`.

```python
import logging
logger = logging.getLogger('PingdomBackup')
logger.setLevel(logging.DEBUG)

pb.update_results(check)
```
