import os
import random
import httpx


class Client:
    """An API wrapper for www.1secmail.com written in Python.

    >>> import secmail
    >>> client = secmail.Client()

    """

    def __init__(self, host="www.1secmail.com") -> None:
        self.host = "https://" + host + "/api/v1/"
        self.client = httpx.Client()

    def _request(self):
        pass

    def create_random_email(self, amount: int):
        pass
