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

    def __init__(self, host="www.1secmail.com") -> None:
        self.host = "https://" + host + "/api/v1/"
        self.client = httpx.Client()

    def _request(self, method, url, params, json, data_type):
        pass

    def get_active_domains(self) -> list:
        """Get list of currently active domains"""
        pass

    def random_email(self, amount: int, domain: str) -> list:
        """Generate random email addresses"""
        pass

    def custom_email(self, username: str, domain: str) -> str:
        """Generate custom email address"""
        pass

    def get_messages(self, address: str) -> list:
        """Check your mailbox"""
        pass

    def get_message(self, address: str, message_id: int):
        """Fetch single message"""
        pass

    def await_new_message(self, address: str):
        """Wait until you receive a new message"""
        pass

    def save_email(self, address: str):
        """Save email to json file"""
        pass

    def download_attachment(self, address: str, message_id: int, filename: str):
        """Download attachment from message"""
        pass
