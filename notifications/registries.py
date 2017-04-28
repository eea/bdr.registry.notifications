import requests
import logging

from django.conf import settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseRegistry(object):
    """ Base class for both registries.
    """

    def __init__(self, name, entrypoint, auth=None, token=None, timeout=5):
        self.name = name
        self.entrypoint = entrypoint
        self.auth = auth
        self.token = token
        self.timeout = timeout

    def __str__(self):
        return '{} @ {}'.format(self.name, self.entrypoint)

    def get_url(self, path):
        return '{}{}'.format(self.entrypoint, path)

    def do_request(self, path, method='get', params=None, data=None,
                   headers=None, cookies=None, auth=None):
        """ Handler for a generic API call:
            - method  -- get/post
            - params  -- dictionary or bytes to be sent in the query string of
                         the Request
            - data    -- dictionary or list of tuples [(key, value)] to send in
                         the body of the Request
            - headers -- dictionary of HTTP Headers to send with the Request
            - cookies -- dictionary or CookieJar object to send with the Request
            - auth    -- auth tuple to enable Basic/Digest/Custom HTTP Auth
        """
        request = requests.get
        if method == 'post':
            request = requests.post

        url = self.get_url(path)
        r = None
        try:
            r = request(url,
                        params=params,
                        data=data,
                        headers=headers,
                        cookies=cookies,
                        auth=auth,
                        timeout=self.timeout,
                        verify=True)
        except Exception as e:
            logger.warning('Error contacting {} ({})'.format(self.name, e))
        else:
            if r.status_code != requests.codes.ok:
                logger.warning('Retrieved a {} status code when contacting'
                               ' {}\'s url: {} '.format(r.status_code,
                                                        self.name,
                                                        url))
        return r


class BDRRegistry(BaseRegistry):
    """ Middleware to communicate with BDR Registry.
    """

    def __init__(self):
        entrypoint = settings.BDRREGISTRY_URL
        auth = (
            settings.BDRREGISTRY_USERNAME,
            settings.BDRREGISTRY_PASSWORD
        )
        super(BDRRegistry, self).__init__('BDRRegistry',
                                          entrypoint=entrypoint,
                                          auth=auth)

    def do_login(self):
        """ Login to registry using the credentials from auth.
        """
        url = self.get_url('/accounts/login')
        cookies = None

        client = requests.session()
        csrf = None
        try:
            csrf = client.get(url).cookies.get('csrftoken')
        except RequestException as e:
            logger.warning('Unable to retrieve csrf: {}'.format(e))

        data = {
            'username': self.auth[0],
            'password': self.auth[1],
            'csrfmiddlewaretoken': csrf,
            'next': '/'
        }
        try:
            resp = client.post(url, data=data, headers=dict(Referer=url))
        except RequestException as e:
            logger.warning('Unable to login to {} ({})'.format(self.name, e))
        else:
            if resp.status_code == 200:
                cookies = resp.request.headers.get('Cookie').split(';')
                for cookie in cookies:
                    cookie = cookie.strip()
                    session = cookie.split('sessionid=')
                    if len(session) == 2:
                        sessionid = session[-1]
                        self.cookies = dict(sessionid=sessionid)
                        cookies = self.cookies
        return cookies

    def do_request(self, path, method='get', params=None, data=None,
                   headers=None, cookies=None, auth=None):
        """ Handler for BDR API calls - the authorization is done
            using an user and a password.
        """
        if not cookies:
            cookies = self.do_login()
        return super(BDRRegistry, self).do_request(path,
                                                   method=method,
                                                   params=params,
                                                   data=data,
                                                   headers=headers,
                                                   cookies=cookies,
                                                   auth=auth)

    def get_companies(self):
        r = self.do_request('/management/companies/export/json', 'post')
        if r:
            return r.json()


class FGasesRegistry(BaseRegistry):
    """ Middleware to communicate with BDR Registry.
    """

    def __init__(self):
        entrypoint = settings.FGASESREGISTRY_URL
        token = settings.FGASESREGISTRY_TOKEN
        super(FGasesRegistry, self).__init__('FGasesRegistry',
                                          entrypoint=entrypoint,
                                          token=token)

    def do_request(self, path, method='get', params=None, data=None,
                   headers=None, cookies=None, auth=None):
        """ Handler for FGases API calls - the authorization is done
            using a token.
        """
        headers = {'Authorization': self.token}
        return super(FGasesRegistry, self).do_request(path,
                                                   method=method,
                                                   params=params,
                                                   data=data,
                                                   headers=headers,
                                                   cookies=cookies,
                                                   auth=auth)

    def get_companies(self):
        r = self.do_request('/undertaking/list')
        if r:
            return r.json()
