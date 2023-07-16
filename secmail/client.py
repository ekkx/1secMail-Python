import os
import re
import asyncio
import random
import string
import httpx
import time
import json

from typing import List
from json import JSONDecodeError

from .config import (
    DOMAIN_LIST,
    GET_DOMAIN_LIST,
    GET_MESSAGES,
    GET_SINGLE_MESSAGE,
    DOWNLOAD,
)
from .models import Inbox, Message


# errors


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


# utils


def is_valid_username(username: str) -> bool:
    if username is None or len(username) > 64:
        return False
    return bool(
        re.match(r"^[A-Za-z][A-Za-z0-9._-]*[A-Za-z0-9]$", username)
        and not re.search(r"\.\.|\-\-|\_\_|\.$", username)
    )


current_path = os.path.abspath(os.getcwd())


# client


class Client:
    """An API wrapper for www.1secmail.com written in Python.

    >>> import secmail
    >>> client = secmail.Client()

    """

    def __init__(
        self, base_path=current_path + "/config/", host="www.1secmail.com"
    ) -> None:
        self.base_path = base_path
        self.api_url = "https://" + host + "/api/v1/"
        self.client = httpx.Client()

    def _request(self, action: str, params=None, data_type=None):
        r = self.client.request(method="GET", url=self.api_url + action, params=params)

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

        if action == DOWNLOAD:
            return r.content

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
        for _ in range(amount):
            username = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=12)
            )
            email = f"{username}@{domain or random.choice(DOMAIN_LIST)}"
            emails.append(email)

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

        if is_valid_username(username) is False:
            err_msg = f"'{username}' is not a valid username."
            raise ValueError(err_msg)

        return f"{username}@{domain or random.choice(DOMAIN_LIST)}"

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
        return self._request(action=GET_DOMAIN_LIST)

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
        username, domain = address.split("@")
        return self._request(
            action=GET_MESSAGES,
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
        username, domain = address.split("@")
        return self._request(
            action=GET_SINGLE_MESSAGE,
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

    def download_attachment(
        self,
        address: str,
        message_id: int,
        filename: str,
        save_path: str = current_path + "/config/",
    ):
        """This method downloads an attachment from a message in the mailbox for the specified email address and message ID.

        Parameters:
        ----------
        - `address`: `str` - The email address to check for the message containing the attachment.
        - `message_id`: `int` - The ID of the message containing the attachment to download.
        - `filename`: `str` - The name of the attachment file to download.
        - `save_path`: `str` - Optional. The path to save the downloaded attachment. Default is the current path + "/config/".

        Returns:
        -------
        - `str` - A string indicating the path and size of the downloaded attachment.

        Example:
        -------
        Download the attachment named "report.pdf" from the message with ID 12345 in the mailbox for the email address "johndoe@1secmail.com":

        >>> download_attachment("johndoe@1secmail.com", 12345, "report.pdf")

        """
        username, domain = address.split("@")
        attachment = self._request(
            action=DOWNLOAD,
            params={
                "login": username,
                "domain": domain,
                "id": message_id,
                "file": filename,
            },
        )

        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)

        with open(save_path + filename, "wb") as attachment_file:
            size = attachment_file.write(attachment)
        return "Path: (" + save_path + filename + "), Size: " + str(size) + "B"


# async client


class AsyncClient:
    """An API wrapper for www.1secmail.com written in Python.

    >>> import secmail
    >>> client = secmail.AsyncClient()

    """

    def __init__(
        self, base_path=current_path + "/config/", host="www.1secmail.com"
    ) -> None:
        self.base_path = base_path
        self.api_url = "https://" + host + "/api/v1/"
        self.client = httpx.AsyncClient()

    async def _request(self, action: str, params=None, data_type=None):
        r = await self.client.request(
            method="GET", url=self.api_url + action, params=params
        )

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

        if action == DOWNLOAD:
            return r.content

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
        for _ in range(amount):
            username = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=12)
            )
            email = f"{username}@{domain or random.choice(DOMAIN_LIST)}"
            emails.append(email)

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

        if is_valid_username(username) is False:
            err_msg = f"'{username}' is not a valid username."
            raise ValueError(err_msg)

        return f"{username}@{domain or random.choice(DOMAIN_LIST)}"

    async def await_new_message(self, address: str, fetch_interval=5) -> Inbox:
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

        >>> message = await client.await_new_message("johndoe@1secmail.com")

        The method will continuously check for new messages every `fetch_interval` seconds until a new message is received. Once a new message is received, the message object is returned. The method also maintains a set of message IDs to check if the message is new. If the same message is received again, the method will continue to wait for a new message.

        Note that if no new messages are received for a long time, the method may take a long time to return.

        """
        ids = {message.id for message in await self.get_inbox(address)}
        while True:
            await asyncio.sleep(fetch_interval)
            new_messages = await self.get_inbox(address)
            for message in new_messages:
                if message.id not in ids:
                    return message

    async def get_active_domains(self) -> List[str]:
        """This method retrieves a list of currently active domains.

        Returns:
        -------
        - `domains`: `List[str]` - A list of active domains.

        Example:
        -------
        Get a list of active domains:

        >>> domains = await client.get_active_domains()

        The method sends a GET request to the API endpoint to retrieve a list of currently active domains. The list is returned as a list of strings.

        Note that the list of active domains may change over time.

        """
        return await self._request(action=GET_DOMAIN_LIST)

    async def get_inbox(self, address: str) -> List[Inbox]:
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

        >>> messages = await client.get_inbox("johndoe@1secmail.com")

        The method sends a GET request to the API endpoint to retrieve all the messages in the mailbox for the specified email address. The messages are returned as a list of inbox objects. If there are no messages in the mailbox, an empty list is returned.

        """
        username, domain = address.split("@")
        return await self._request(
            action=GET_MESSAGES,
            params={"login": username, "domain": domain},
            data_type=Inbox,
        )

    async def get_message(self, address: str, message_id: int) -> Message:
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

        >>> message = await client.get_message("johndoe@1secmail.com", 12345)

        The method sends a GET request to the API endpoint to retrieve the message with the specified ID in the mailbox for the specified email address. The message is returned as a message object.

        """
        username, domain = address.split("@")
        return await self._request(
            action=GET_SINGLE_MESSAGE,
            params={"login": username, "domain": domain, "id": message_id},
            data_type=Message,
        )

    async def save_email(self, address: str) -> None:
        """This method saves the specified email address to a JSON file for future use.

        Parameters:
        ----------
        - `address`: `str` - The email address to save.

        Example:
        -------
        Save the email address "johndoe@1secmail.com" to the JSON file:

        >>> await client.save_email("johndoe@1secmail.com")

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

    async def download_attachment(
        self,
        address: str,
        message_id: int,
        filename: str,
        save_path: str = current_path + "/config/",
    ):
        """This method downloads an attachment from a message in the mailbox for the specified email address and message ID.

        Parameters:
        ----------
        - `address`: `str` - The email address to check for the message containing the attachment.
        - `message_id`: `int` - The ID of the message containing the attachment to download.
        - `filename`: `str` - The name of the attachment file to download.
        - `save_path`: `str` - Optional. The path to save the downloaded attachment. Default is the current path + "/config/".

        Returns:
        -------
        - `str` - A string indicating the path and size of the downloaded attachment.

        Example:
        -------
        Download the attachment named "report.pdf" from the message with ID 12345 in the mailbox for the email address "johndoe@1secmail.com":

        >>> await download_attachment("johndoe@1secmail.com", 12345, "report.pdf")

        """
        username, domain = address.split("@")
        attachment = await self._request(
            action=DOWNLOAD,
            params={
                "login": username,
                "domain": domain,
                "id": message_id,
                "file": filename,
            },
        )

        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)

        with open(save_path + filename, "wb") as attachment_file:
            size = attachment_file.write(attachment)
        return "Path: (" + save_path + filename + "), Size: " + str(size) + "B"
