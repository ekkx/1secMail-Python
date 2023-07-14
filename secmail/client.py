import os
import time
import random
import string
import httpx
import json

from typing import List, Tuple
from json import JSONDecodeError

from .config import (
    DOMAIN_LIST,
    GET_DOMAIN_LIST,
    GET_MESSAGES,
    GET_SINGLE_MESSAGE,
    DELETE_MAILBOX,
    DOWNLOAD,
)
from .models import Inbox, Message


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


current_path = os.path.abspath(os.getcwd())


class Client:
    """An API wrapper for www.1secmail.com written in Python.

    >>> import secmail
    >>> client = secmail.Client()

    """

    def __init__(
        self, base_path=current_path + "/config/", host="www.1secmail.com"
    ) -> None:
        self.base_path = base_path
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
            if isinstance(r, list):
                r = [data_type(result) for result in r]
            elif r is not None:
                r = data_type(r)

        return r

    @staticmethod
    def _split_email(address: str) -> Tuple[str, str]:
        return address.split("@")

    @staticmethod
    def random_email(amount: int, domain: str = None) -> List[str]:
        """This method generates a list of random email addresses.

        Parameters:
        ----------

            - `amount`: `int` - The number of email addresses to generate.
            - `domain`: `str` (optional) - The domain name to use for the email addresses. If not provided, a random domain from the valid list of domains will be selected.

        Example:
        -------
        Generate a list of 5 email addresses with the domain "1secmail.com":

            >>> client.random_email(amount=5, domain="1secmail.com")

        Valid domains:
        -------------

            - 1secmail.com
            - 1secmail.org
            - 1secmail.net
            - kzccv.com
            - qiott.com
            - wuuvo.com
            - icznn.com
            - ezztt.com

        If `domain` is provided and not in the valid list of domains, a ValueError will be raised with a message indicating the invalid domain and the valid list of domains.

        """
        if domain is not None and domain not in DOMAIN_LIST:
            err_msg = (
                f"{domain} is not a valid domain name.\nValid Domains: {DOMAIN_LIST}"
            )
            raise ValueError(err_msg)

        emails = []
        for i in range(amount):
            name = string.ascii_lowercase + string.digits
            username = "".join(random.choice(name) for i in range(12))
            if domain is not None:
                emails.append(username + "@" + domain)
            else:
                emails.append(username + "@" + random.choice(DOMAIN_LIST))

        return emails

    @staticmethod
    def custom_email(username: str, domain: str = None) -> str:
        """This method generates a custom email address.

        Parameters:
        ----------
        - `username`: `str` - The username to use for the email address.
        - `domain`: `str` (optional) - The domain name to use for the email address. If not provided, a random domain from the valid list of domains will be selected.

        Returns:
        -------
        - `email`: `str` - The generated email address.

        Example:
        -------
        Generate a custom email address with the username "johndoe":

        >>> client.custom_email(username="johndoe")

        Valid domains:
        -------------
        - 1secmail.com
        - 1secmail.org
        - 1secmail.net
        - kzccv.com
        - qiott.com
        - wuuvo.com
        - icznn.com
        - ezztt.com

        If `domain` is provided and not in the valid list of domains, a ValueError will be raised with a message indicating the invalid domain and the valid list of domains.

        """
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

    def await_new_message(self, address: str, fetch_interval=5) -> Inbox:
        """This method waits until a new message is received for the specified email address.

        Parameters:
        ----------
        - `address`: `str` - The email address to check for new messages.
        - `fetch_interval`: `int` (optional) - The time interval (in seconds) for checking new messages. The default value is 5 seconds.

        Returns:
        -------
        - `message`: `Inbox` - The new message received.

        Example:
        -------
        Wait for a new message to be received for the email address "johndoe@1secmail.com":

        >>> message = client.await_new_message("johndoe@1secmail.com")

        The method will continuously check for new messages every `fetch_interval` seconds until a new message is received. Once a new message is received, the message object is returned. The method also maintains a set of message IDs to check if the message is new. If the same message is received again, the method will continue to wait for a new message.

        Note that if no new messages are received for a long time, the method may take a long time to return.

        """
        ids = {message.id for message in self.get_inbox(address)}
        while True:
            time.sleep(fetch_interval)
            new_messages = self.get_inbox(address)
            for message in new_messages:
                if message.id not in ids:
                    return message

    def get_active_domains(self) -> List[str]:
        """This method retrieves a list of currently active domains.

        Returns:
        -------
        - `domains`: `List[str]` - A list of active domains.

        Example:
        -------
        Get a list of active domains:

        >>> domains = client.get_active_domains()

        The method sends a GET request to the API endpoint to retrieve a list of currently active domains. The list is returned as a list of strings.

        Note that the list of active domains may change over time.

        """
        return self._request(method="GET", url=self.host + GET_DOMAIN_LIST)

    def delete_email(self, address: str) -> None:
        """This method deletes the mailbox for the specified email address.

        Parameters:
        ----------
        - `address`: `str` - The email address to delete.

        Returns:
        -------
        - `response`: `None` - The response message from the API.

        Example:
        -------
        Delete the mailbox for the email address "johndoe@1secmail.com":

        >>> client.delete_email("johndoe@1secmail.com")

        The method sends a DELETE request to the API endpoint to delete the mailbox for the specified email address.

        """
        username, domain = self._split_email(address)
        return self._request(
            method="DELETE",
            url=self.host + DELETE_MAILBOX,
            params={"login": username, "domain": domain},
        )

    def get_inbox(self, address: str) -> List[Inbox]:
        """This method retrieves all the messages in the mailbox for the specified email address.

        Parameters:
        ----------
        - `address`: `str` - The email address to check for messages.

        Returns:
        -------
        - `messages`: `List[Inbox]` - A list of message objects in the mailbox.

        Example:
        -------
        Get all the messages in the mailbox for the email address "johndoe@1secmail.com":

        >>> messages = client.get_inbox("johndoe@1secmail.com")

        The method sends a GET request to the API endpoint to retrieve all the messages in the mailbox for the specified email address. The messages are returned as a list of inbox objects. If there are no messages in the mailbox, an empty list is returned.

        """
        username, domain = self._split_email(address)
        return self._request(
            method="GET",
            url=self.host + GET_MESSAGES,
            params={"login": username, "domain": domain},
            data_type=Inbox,
        )

    def get_message(self, address: str, message_id: int) -> Message:
        """This method retrieves a detailed message from the mailbox for the specified email address and message ID.

        Parameters:
        ----------
        - `address`: `str` - The email address to check for the message.
        - `message_id`: `int` - The ID of the message to retrieve.

        Returns:
        -------
        - `message`: `Message` - The message object with the specified ID.

        Example:
        -------
        Get the message with ID 12345 in the mailbox for the email address "johndoe@1secmail.com":

        >>> message = client.get_message("johndoe@1secmail.com", 12345)

        The method sends a GET request to the API endpoint to retrieve the message with the specified ID in the mailbox for the specified email address. The message is returned as a message object.

        """
        username, domain = self._split_email(address)
        return self._request(
            method="GET",
            url=self.host + GET_SINGLE_MESSAGE,
            params={"login": username, "domain": domain, "id": message_id},
            data_type=Message,
        )

    def save_email(self, address: str) -> None:
        """This method saves the specified email address to a JSON file for future use.

        Parameters:
        ----------
        - `address`: `str` - The email address to save.

        Example:
        -------
        Save the email address "johndoe@1secmail.com" to the JSON file:

        >>> client.save_email("johndoe@1secmail.com")

        The JSON file is saved in the base path specified during client initialization, with the name `secmail.json`.

        """
        data = {}

        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)

        if os.path.exists(self.base_path + "secmail.json"):
            with open(self.base_path + "secmail.json", "r") as f:
                data = json.load(f)

        data.setdefault("email", []).append(address)

        with open(self.base_path + "secmail.json", "w") as f:
            json.dump(data, f, indent=4)

    def download_attachment(self, address: str, message_id: int, filename: str):
        """Download attachment from message."""
        username, domain = self._split_email(address)
        return self._request(
            method="GET",
            url=self.host + DOWNLOAD,
            params={
                "login": username,
                "domain": domain,
                "id": message_id,
                "file": filename,
            },
        )
