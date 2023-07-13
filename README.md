<p align="center">
  <br>
  <img src="https://github.com/qvco/1secMail-Python/assets/77382767/fde69c1a-b95f-4d78-af1a-2dca315204bc" alt="1secMail" width="700">
<!--   <br>
  1secMail for Python
  <br> -->
</p>

<h4 align="center">An API wrapper for <a href="https://www.1secmail.com/" target="_blank">www.1secmail.com</a> written in Python.</h4>

  <p align="center">
    <img src="https://img.shields.io/github/release/qvco/1secMail-Python">
    <img src="https://img.shields.io/badge/python-3.8-blue.svg">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg">
  </p>

### About

This is a simple Python API wrapper for www.1secmail.com ↗ using the official 1secMail API. It allows you to easily generate temporary email addresses as much as you want and retrieve emails sent to those addresses.

### Install

To install this package, you'll need Python 3.8 or above installed on your computer. From your command line:

```bash
pip install 1secMail
```

<br>

> **Note**
> If you're willing to install the development version, do the following:

```bash
git clone https://github.com/qvco/1secMail-Python

cd 1secMail-Python

pip install -r requirements.txt

pip install -e .
```

### How To Use

```python
import secmail

client = secmail.Client()

client.random_email(amount=1)[0]
>>> 'vsd2bq6zo3@1secmail.net'

client.custom_email(username="bobby-bob")
>>> 'bobby-bob@1secmail.org'


# Checking your mailbox:
messages = client.get_messages("bobby-bob@1secmail.org")
for message in messages:
    print(message.id)
    print(message.from_address)
    print(message.subject)
    print(message.date)


# Fetching single message:
message = client.get_message(address="bobby-bob@1secmail.org", message_id=235200687)
print(message.id)
print(message.subject)
print(message.body)
print(message.text_body)
print(message.html_body)
print(message.attachments)
print(message.date)


# Checking attachment informations
for attachment in message.attachments:
    print(attachment.filename)
    print(attachment.content_type)
    print(attachment.size)
```

### Licnese

This software is licensed under the [MIT](https://github.com/qvco/1secMail-Python/blob/master/LICENSE) © [Qvco](https://github.com/qvco).
