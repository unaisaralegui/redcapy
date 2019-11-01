import requests


class RedCapError(requests.RequestException):
    pass


from . import request

