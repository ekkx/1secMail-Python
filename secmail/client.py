import os
import random
import string
import httpx

from json import JSONDecodeError

from .config import (
    DOMAIN_LIST,
    GEN_RANDOM_MAILBOX,
    GET_DOMAIN_LIST,
    GET_MESSAGES,
    GET_SINGLE_MESSAGE,
    DELETE_MAILBOX,
    DOWNLOAD,
)


class SecMailError(Exception):
    """Base exception for 1secMail"""

    pass


class BadRequestError(SecMailError):
    """BadRequestError()

    Exception raised for a 400 HTTP status code
    """

    pass


class AuthenticationError(SecMailError):
    """AuthenticationError()

    Exception raised for a 401 HTTP status code
    """

    pass


class ForbiddenError(SecMailError):
    """ForbiddenError()

    Exception raised for a 403 HTTP status code
    """

    pass


class NotFoundError(SecMailError):
    """NotFoundError()

    Exception raised for a 404 HTTP status code
    """

    pass


class RateLimitError(SecMailError):
    """RateLimitError()

    Exception raised for a 429 HTTP status code
    """

    pass


class ServerError(SecMailError):
    """ServerError()

    Exception raised for a 5xx HTTP status code
    """

    pass


class Client:
    """An API wrapper for www.1secmail.com written in Python.

    >>> import secmail
    >>> client = secmail.Client()

    """

    def __init__(self, host="www.1secmail.com") -> None:
        self.host = "https://" + host + "/api/v1/"
        self.client = httpx.Client()

    def _request(self, method, url, params=None, json=None, data_type=None):
        r = self.client.request(method=method, url=url, params=params, json=json)

        if r.status_code == 400:
            raise BadRequestError(f"HTTP {r.status_code}: {r.text}")
        if r.status_code == 401:
            raise AuthenticationError(f"HTTP {r.status_code}: {r.text}")
        if r.status_code == 403:
            raise ForbiddenError(f"HTTP {r.status_code}: {r.text}")
        if r.status_code == 404:
            raise NotFoundError(f"HTTP {r.status_code}: {r.text}")
        if r.status_code == 429:
            raise RateLimitError(f"HTTP {r.status_code}: {r.text}")
        if r.status_code == 500:
            raise ServerError(f"HTTP {r.status_code}: {r.text}")

        try:
            r = r.json()
        except JSONDecodeError:
            return r.text

        if data_type is not None:
            return data_type(r)

        return r

    @staticmethod
    def _split_email(address: str) -> tuple:
        return address.split("@")

    def get_active_domains(self) -> list:
        """Get list of currently active domains."""
        return self._request(method="GET", url=f"{self.host + GET_DOMAIN_LIST}")

    def random_email(self, amount: int, domain: str = None) -> list:
        """Generate a list of random email addresses."""
        if domain is not None and domain not in DOMAIN_LIST:
            err_msg = (
                f"{domain} is not a valid domain name.\nValid Domains: {DOMAIN_LIST}"
            )
            raise ValueError(err_msg)

        emails = []
        for i in range(amount):
            name = string.ascii_lowercase + string.digits
            username = "".join(random.choice(name) for i in range(10))
            if domain is not None:
                emails.append(username + "@" + domain)
            else:
                emails.append(username + "@" + random.choice(DOMAIN_LIST))

        return emails

    def delete_email(self, address: str) -> str:
        """Delete specific email address."""
        username, domain = self._split_email(address)
        return self._request(
            method="DELETE",
            url=f"{self.host + DELETE_MAILBOX}",
            params={"login": username, "domain": domain},
        )

    def custom_email(self, username: str, domain: str = "1secmail.com") -> str:
        """Generate custom email address."""
        if domain is not None and domain not in DOMAIN_LIST:
            err_msg = (
                f"{domain} is not a valid domain name.\nValid Domains: {DOMAIN_LIST}"
            )
            raise ValueError(err_msg)

        if domain is not None:
            email = username + "@" + domain
        else:
            email = username + "@" + random.choice(DOMAIN_LIST)

        return email

    def get_messages(self, address: str) -> list:
        """Check your mailbox."""
        username, domain = self._split_email(address)
        return self._request(
            method="GET",
            url=f"{self.host + GET_MESSAGES}",
            params={"login": username, "domain": domain},
        )

    def get_message(self, address: str, message_id: int):
        """Fetch single message."""
        username, domain = self._split_email(address)
        return self._request(
            method="GET",
            url=f"{self.host + GET_SINGLE_MESSAGE}",
            params={"login": username, "domain": domain, "id": message_id},
        )

    def await_new_message(self, address: str):
        """Wait until you receive a new message."""
        pass

    def save_email(self, address: str):
        """Save email to json file."""
        pass

    def download_attachment(self, address: str, message_id: int, filename: str):
        """Download attachment from message."""
        pass
