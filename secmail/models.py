class MailBox:
    """The mailbox object contains an array of email objects, each with an unique ID,\n
    sender's email address, subject line, and date and time the email was sent.

    ---

    Attributes:
    ----------

    - id : (``int``) - Message id

    - from_address : (``str``) - Sender email address

    - subject : (``str``) - Subject

    - date : (``str``) - Receive date

    """

    __slots__ = ("id", "from_address", "subject", "date")

    def __init__(self, response) -> None:
        self.id = response.get("id")
        self.from_address = response.get("from")
        self.subject = response.get("subject")
        self.date = response.get("date")

    def __str__(self) -> str:
        return f"MailBox(id={self.id}, from_address={self.from_address}, subject={self.subject}, date={self.date})"


class Message:
    """The message object contains an unique ID, sender's email address,\n
    subject line, date and time the email was sent, list of attachment object,\n
    body (html if exists, text otherwise), text body and HTML body.

    ---

    Attributes:
    ----------

    - id : (``int``) - Message id

    - from_address : (``str``) - Sender email address

    - subject : (``str``) - Subject

    - date : (``str``) - Receive date

    - attachments : (``str``) - List of Attachment object

    - body : (``str``) - Message body (html if exists, text otherwise)

    - text_body : (``str``) - Message body (text)

    - html_body : (``str``) - Message body (html)

    """

    __slots__ = (
        "id",
        "from_address",
        "subject",
        "date",
        "attachments",
        "body",
        "text_body",
        "html_body",
    )

    def __init__(self, response) -> None:
        self.id = response.get("id")
        self.from_address = response.get("from")
        self.subject = response.get("subject")
        self.date = response.get("date")

        self.attachments = response.get("attachments")
        if self.attachments is not None:
            self.attachments = [
                Attachment(attachment) for attachment in self.attachments
            ]

        self.body = response.get("body")
        self.text_body = response.get("textBody")
        self.html_body = response.get("htmlBody")

    def __str__(self) -> str:
        return f"Message(id={self.id}, from_address={self.from_address}, subject={self.subject}, date={self.date})"


class Attachment:
    pass
