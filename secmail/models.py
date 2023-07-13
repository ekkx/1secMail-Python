class MailBox:
    """The mailbox object contains an array of email objects, each with an unique ID,\n
    sender's email address, subject line, and date and time the email was sent.

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
        self.from_address = response.get("from_address")
        self.subject = response.get("subject")
        self.date = response.get("date")

    def __str__(self) -> str:
        return f"MailBox(id={self.id}, from_address={self.from_address}, subject={self.subject}, date={self.date})"


class Message:
    pass


class Attachment:
    pass
