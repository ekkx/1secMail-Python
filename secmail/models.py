class Inbox:
    """The inbox object contains an array of email objects, each with an unique ID,\n
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

    def __repr__(self) -> str:
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

    def __repr__(self) -> str:
        return (
            f"Message(id={self.id}, from_address={self.from_address}, subject={self.subject}, "
            f"date={self.date}, attachments={self.attachments}, body={self.body}, "
            f"text_body={self.text_body}, html_body={self.html_body})"
        )


class Attachment:
    """The attachment object contains the attachment's filename, content_type and file size.

    ---

    Attributes:
    ----------

    - filename : (``str``) - Attachment filename

    - content_type : (``str``) - Attachment content type

    - size : (``int``) - Attachment size

    """

    __slots__ = "filename", "content_type", "size"

    def __init__(self, response) -> None:
        self.filename = response.get("filename")
        self.content_type = response.get("contentType")
        self.size = response.get("size")

    def __repr__(self) -> str:
        return f"Attachment(filename={self.filename}, content_type={self.content_type}, size={self.size})"
