import logging
import requests
from requests.exceptions import RequestException

from django.conf import settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseRegistry(object):
    """ Base class for both registries.
    """

    def __init__(self, name, entrypoint, auth=None, token=None, timeout=20):
        self.name = name
        self.entrypoint = entrypoint
        self.auth = auth
        self.token = token
        self.timeout = timeout

    def __str__(self):
        return '{} @ {}'.format(self.name, self.entrypoint)

    def __repr__(self):
        """ Overwrite default for memcache key generation.
        """
        return '{}.{}'.format(self.__module__, self.__class__.__name__)

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
        response = None

        try:
            response = request(url,
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
            if response.status_code != requests.codes.ok:
                logger.warning('Retrieved a {} status code when contacting'
                               ' {}\'s url: {} '.format(response.status_code,
                                                        self.name,
                                                        url))
        return response


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
        self.cookies = None

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
            response = client.post(url, data=data, headers=dict(Referer=url))
        except RequestException as e:
            logger.warning('Unable to login to {} ({})'.format(self.name, e))
        else:
            if response.status_code == 200:
                cookies = {}
                for cookie in response.request.headers.get('Cookie').split(';'):
                    cookie = cookie.strip()
                    session = cookie.split('sessionid=')
                    if len(session) == 2:
                        sessionid = session[-1]
                        cookies = dict(sessionid=sessionid)
                        break
        return cookies

    def do_request(self, path, method='get', params=None, data=None,
                   headers=None, cookies=None, auth=None):
        """ Handler for BDR API calls - the authorization is done
            using an user and a password.
        """
        if self.cookies is None:
            self.cookies = self.do_login()

        return super(BDRRegistry, self).do_request(path,
                                                   method=method,
                                                   params=params,
                                                   data=data,
                                                   headers=headers,
                                                   cookies=self.cookies,
                                                   auth=auth)

    def get_companies(self):
        """ Gets the list with all companies. Each company has
            the following fields:
            - name
            - country (code)
            - country_name
            - addr_street
            - userid
            - date_registered
            - addr_place1
            - addr_place2
            - active
            - vat_number
            - obligation
            - outdated
            - persons (array)
                - first_name
                - last_name
                - title
                - email
                - phone
                - phone2
                - phone3
        """
        response = self.do_request(settings.BDR_COMPANIES_PATH)
        if response:
            return response.json()
        return []

    def get_persons(self):
        """ Gets the list with all persons. Each person has
            the following fields:
            - userid
            - companyname
            - country -- company's country
            - contactname
            - contactemail
            - phone
            - phone2
            - phone3
            - fax
        """
        response = self.do_request(settings.BDR_PERSONS_PATH)
        if response:
            return response.json()
        return []


class FCSRegistry(BaseRegistry):
    """ Middleware to communicate with BDR Registry.
    """

    def __init__(self):
        entrypoint = settings.FCSREGISTRY_URL
        token = settings.FCSREGISTRY_TOKEN
        super(FCSRegistry, self).__init__('FCSRegistry',
                                          entrypoint=entrypoint,
                                          token=token)

    def do_request(self, path, method='get', params=None, data=None,
                   headers=None, cookies=None, auth=None):
        """ Handler for FCS API calls - the authorization is done
            using a token.
        """
        headers = {'Authorization': self.token}
        return super(FCSRegistry, self).do_request(path,
                                                   method=method,
                                                   params=params,
                                                   data=data,
                                                   headers=headers,
                                                   cookies=cookies,
                                                   auth=auth)

    def get_companies(self, path):
        """ Gets the list with all companies. Each company has
            the following fields:
             - status
             - date_updated
             - domain
             - oldcompany_extid
             - country_code
             - undertaking_type
             - oldcompany_verified
             - company_id
             - businessprofile
                - highleveluses
             - vat
             - website
             - users
             - phone
             - representative
             - address (dict)
                - city
                - country (dict)
                    - code
                    - type
                    - name,
                - zipcode
                - number
                - street
             - collection_id
             - types
             - name
             - country_code_orig
             - date_created
             - oldcompany_account
        """
        response = self.do_request(path)
        if response:
            return response.json()
        return []

    def get_persons(self, path):
        """ Gets the list with all persons. Each person has
            the following fields:
            - username
            - first_name
            - last_name
            - email
        """
        response = self.do_request(path)
        if response:
            return response.json()
        return []
