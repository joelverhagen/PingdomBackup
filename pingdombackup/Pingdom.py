import requests
from requests.auth import HTTPBasicAuth

from .log import log

class Pingdom:
    def __init__(self, email, password, app_key, version=2.0):
        self.email = email
        self.password = password
        self.app_key = app_key
        self.version = version

    def api(self, method, endpoint, params=None, data=None):
        url = 'https://api.pingdom.com/api/{0}/{1}'.format(self.version, endpoint)

        import urllib.parse
        if params is not None:
            encoded_params = '?' + urllib.parse.urlencode(params)
        else:
            encoded_params = ''
        log.debug('Pingdom: GET ' + url + encoded_params)

        resp = requests.request(method, url,
            auth=HTTPBasicAuth(self.email, self.password),
            headers={'App-Key': self.app_key},
            params=params,
            data=data
            )

        return resp.json()
