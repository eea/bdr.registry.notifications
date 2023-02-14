import logging
import requests

from django.conf import settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseRegistry(object):
    """Base class for both registries."""

    def __init__(self, name, entrypoint, auth=None, token=None, timeout=500):
        self.name = name
        self.entrypoint = entrypoint
        self.auth = auth
        self.token = token
        self.timeout = timeout

    def __str__(self):
        return "{} @ {}".format(self.name, self.entrypoint)

    def __repr__(self):
        """Overwrite default for memcache key generation."""
        return "{}.{}".format(self.__module__, self.__class__.__name__)

    def get_url(self, path):
        return "{}{}".format(self.entrypoint, path)

    def do_request(
        self,
        path,
        method="get",
        params=None,
        data=None,
        headers=None,
        cookies=None,
        auth=None,
    ):
        """Handler for a generic API call:
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
        if method == "post":
            request = requests.post

        url = self.get_url(path)
        response = None

        try:
            response = request(
                url,
                params=params,
                data=data,
                headers=headers,
                cookies=cookies,
                auth=auth,
                timeout=self.timeout,
                verify=True,
            )
        except Exception as e:
            logger.warning("Error contacting {} ({})".format(self.name, e))
        else:
            if response.status_code != requests.codes.ok:
                logger.warning(
                    "Retrieved a {} status code when contacting"
                    " {}'s url: {} ".format(response.status_code, self.name, url)
                )
        return response


class BDRRegistry(BaseRegistry):
    """Middleware to communicate with BDR Registry."""

    def __init__(self):
        entrypoint = settings.BDR_REGISTRY_URL
        token = settings.BDR_REGISTRY_TOKEN
        super(BDRRegistry, self).__init__(
            "BDRRegistry", entrypoint=entrypoint, token=token
        )

    def do_request(
        self,
        path,
        method="get",
        params=None,
        data=None,
        headers=None,
        cookies=None,
        auth=None,
    ):
        """Handler for BDR API calls - the authorization is done
        using a token.
        """
        headers = {"Authorization": self.token}
        return super(BDRRegistry, self).do_request(
            path,
            method=method,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            auth=auth,
        )

    def get_companies(self):
        """Gets the list with all companies. Each company has
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
        """Gets the list with all persons. Each person has
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


class EuropeanCacheRegistry(BaseRegistry):
    """Middleware to communicate with BDR Registry."""

    def __init__(self):
        entrypoint = settings.ECR_REGISTRY_URL
        token = settings.ECR_REGISTRY_TOKEN
        super(EuropeanCacheRegistry, self).__init__(
            "EuropeanCacheRegistry", entrypoint=entrypoint, token=token
        )

    def do_request(
        self,
        path,
        method="get",
        params=None,
        data=None,
        headers=None,
        cookies=None,
        auth=None,
    ):
        """Handler for ECR API calls - the authorization is done
        using a token.
        """
        headers = {"Authorization": self.token}
        return super(EuropeanCacheRegistry, self).do_request(
            path,
            method=method,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            auth=auth,
        )

    def get_companies(self):
        """Gets the list with all companies. Each company has
        the following fields:
         - website
         - status
         - domain
         - vat
         - users
         - undertaking_type
         - date_updated
         - country_code_orig
         - company_id
         - date_created
         - phone
         - businessprofile
         - country_code
         - address (dict)
            - city
            - street
            - number
            - zipcode
            - country (dict)
                - code
                - type
                - name,
         - types
         - name
        """
        companies = []
        for domain in settings.ECR_DOMAINS:
            response = self.do_request(
                settings.ECR_COMPANY_PATH.replace("[domain]", domain)
            )
            if response:
                companies += response.json()
        return companies

    def get_persons(self):
        """Gets the list with all persons. Each person has
        the following fields:
        - username
        - companyname
        - country -- company's country
        - contact_firstname
        - contact_lastname
        - contact_email
        """
        response = self.do_request(settings.ECR_PERSON_PATH)
        if response:
            return response.json()
        return []
