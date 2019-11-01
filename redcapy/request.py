__author__ = "Unai Saralegui"
__copyright__ = "Copyright 2019, Unai Saralegui"
__credits__ = ["Unai Saralegui", "Josu Gomez"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Unai Saralegui"
__email__ = "usaralegui@gmail.com"
__status__ = "Development"


from . import keywords
from . import RedCapError
import requests
import json
from lxml import etree


class APIHandler:
    """Class to interact with RecCap API"""

    def __init__(self, api_url, token, name='', verify_ssl=True):
        """

        :param api_url: API URL to the REDCap server
        :param token: API token for the project
        :param name: name of the project (optional)
        :param verify_ssl: Verify SSL, default True.
        """
        self.__api_url = api_url
        self.__token = token
        self.__name = name
        self.__verify_ssl = verify_ssl
        self.metadata = None
        self.redcap_version = None
        self.__check_configuration()

    def __check_configuration(self):
        """
        Check the URL and token are valid with API calls to obtain metadata and REDCAP version
        :return: None (raises redcapy.RedCapError if the ocnfiguration is not OK)
        """
        try:
            self.metadata = self.get_metadata()
        except RedCapError:
            raise RedCapError("Exporting metadata failed. Check your URL and token.")
        try:
            self.redcap_version = self.get_redcap_version()
        except:
            raise RedCapError("Determination of REDCap version failed")

    def __call_api(self, payload):
        """
        Function to call the api with the specifiec payload
        :param payload: payload in dictionary format
        :return: return of the request call
        """
        data = list(payload.items())
        request_data = requests.post(self.__api_url, data=data)
        return request_data

    def __construct_payload(self, content, data_format=None):
        """
        Construct the payload with specified content and data_format
        :param content: content to obtain from API
        :param data_format: format of data to obtain (default json)
        :return: payload in dict
        """
        payload = {
            keywords.TOKEN: self.__token,
            keywords.CONTENT: content,
            keywords.FORMAT: data_format,
        }
        if data_format is not None:
            payload[keywords.FORMAT] = data_format
        return payload

    def __get_data_from_request(self, request_data):
        """
        Function to obtain the data from the request
        :param request_data: request return obtained fro API call
        :return: data in python format (str, json or lxml.etree)
        """
        if request_data.status_code != 200:
            raise RedCapError(request_data.content)
        try:
            data = request_data.json()
            return data
        except json.decoder.JSONDecodeError as e:
            pass
        try:
            data = etree.fromstring(request_data.content)
            return data
        except etree.XMLSyntaxError as ex:
            pass
        data = request_data.content
        return data

    def __get_data(self, content, data_format=None):
        """
        Obtain data for content and data_format
        :param content: content to obtain
        :param data_format: format of the data to obtain
        :return: data obtained from server formatted to use inside python
        """
        payload = self.__construct_payload(content=content, data_format=data_format)
        request_data = self.__call_api(payload=payload)
        data = self.__get_data_from_request(request_data=request_data)
        return data

    def get_metadata(self, data_format=None):
        """
        Get metadata for REDCAP project
        :param data_format: format of the data to obtain
        :return: metadata for the REDCAP project
        """
        if self.metadata is not None:
            return self.metadata
        if data_format is None:
            data_format = keywords.FORMAT_JSON
        content = keywords.CONTENT_METADATA
        metadata = self.__get_data(content=content, data_format=data_format)
        return metadata

    def get_redcap_version(self):
        """
        Get the version of the REDCAP project
        :return: redcap version
        """
        if self.redcap_version is not None:
            return self.redcap_version
        content = keywords.CONTENT_VERSION
        redcap_version = self.__get_data(content=content, data_format=None)
        return redcap_version
