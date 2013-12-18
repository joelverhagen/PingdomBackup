from calendar import timegm
from datetime import datetime, timedelta

from .Pingdom import Pingdom
from .Database import Database
from .log import log

class PingdomBackup:
    MAX_INTERVAL = 2764800

    def __init__(self, email, password, app_key, database):
        self.pingdom = Pingdom(email, password, app_key)
        self.database = Database(database)

    def update_probes(self):
        # get the probe list
        log.info('Updating probe records.')
        resp_json = self.pingdom.api('GET', 'probes', params={'includedeleted': True})
        probes = resp_json['probes']
        for probe in probes:
            self.database.upsert_record('probes', probe)
        log.info('{0} {1} updated.'.format(len(probes), 'probe was' if len(probes) == 1 else 'probes were'))

    def update_checks(self):
        # get the checks list
        log.info('Updating check records.')
        resp_json = self.pingdom.api('GET', 'checks')
        checks = resp_json['checks']
        for check in checks:
            del check['tags']
            self.database.upsert_record('checks', check)
        log.info('{0} {1} updated.'.format(len(checks), 'check was' if len(checks) == 1 else 'checks were'))

    def get_check_by_name(self, name):
        return self.database.get_record('checks', where='name = ?', parameters=(name, ))

    def update_results(self, check):
        log.info('Checking for new results.')
        # get the most recent result time from the database
        results = self.database.get_records('results', order_by='time DESC', limit=1)
        if len(results) == 0:
            min_from_t = 0
        else:
            # + 1 because we don't want to include the previous result
            min_from_t = results[0]['time'] + 1

        to_t = timegm((datetime.now() + timedelta(days=2)).timetuple())
        limit = 1000
        last_count = limit
        all_results = []
        while last_count == limit:
            # calculate the minimum bound
            from_t = max(to_t - self.MAX_INTERVAL, min_from_t)

            # get the next page
            resp_json = self.pingdom.api('GET', 'results/{0}'.format(check['id']), params={
                'to': to_t,
                'from': from_t,
                'limit': limit
            })
            results = resp_json['results']
            last_count = len(results)

            # inspect each row
            for result in results:
                result['id'] = None
                result['checkid'] = check['id']

                # update the to_timestamp
                if result['time'] < to_t:
                    to_t = result['time']

            all_results.extend(results)

        # bulk insert
        all_results = sorted(all_results, key=lambda r: r['time'])
        log.info('{0} new {1} been found.'.format(len(all_results), 'result has' if len(all_results) == 1 else 'results have'))
        self.database.insert_records('results', all_results)
