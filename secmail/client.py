import os
import random
import httpx

from .config import (
    DOMAIN_LIST,
    GEN_RANDOM_MAILBOX,
    GET_DOMAIN_LIST,
    GET_MESSAGES,
    SINGLE_MESSAGE,
    DOWNLOAD,
)


class Client:
    """An API wrapper for www.1secmail.com written in Python.

    >>> import secmail
    >>> client = secmail.Client()

    """

    def __init__(self, save_email=False, host="www.1secmail.com") -> None:
        self.host = "https://" + host + "/api/v1/"
        self.client = httpx.Client()

    def _request(self, method, url, params, json, data_type):
        pass

    def get_active_domains(self):
        """Getting list of active domains"""
        pass

    def generate_random_email(self, amount: int, domain: str):
        """Generating random email addresses"""
        pass

    def generate_custom_email(self, name: str, domain: str):
        """Generating custom email address"""
        pass
    
    
