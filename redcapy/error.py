import requests


class RedCapError(requests.RequestException):
    """Default Error Type for the redcapy package"""
    pass
