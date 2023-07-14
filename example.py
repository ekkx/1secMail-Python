import secmail

client = secmail.Client()


# Generating Email Addresses

# To generate a list of random email addresses, use the random_email() method:
client.random_email(amount=3, domain="1secmail.com")

# You can also generate a custom email address by specifying the username and domain:
client.custom_email(username="bobby-bob")


# Receiving Messages

# To wait until a new message is received, use the await_new_message() method:
message = client.await_new_message("bobby-bob@kzccv.com")

# To check all messages received on a particular email address, use the get_inbox() method and pass the email address:
messages = client.get_inbox("bobby-bob@kzccv.com")
for message in messages:
    print(message.id)
    print(message.from_address)
    print(message.subject)
    print(message.date)

# You can also fetch a single message using the get_message() method and passing the email address and message ID:
message = client.get_message(address="bobby-bob@kzccv.com", message_id=235200687)
print(message.id)
print(message.subject)
print(message.body)
print(message.text_body)
print(message.html_body)
print(message.attachments)
print(message.date)


# Attachment Information

# To check attachment information, loop through the attachments in the message object and print the filename, content type, and size:
for attachment in message.attachments:
    print(attachment.filename)
    print(attachment.content_type)
    print(attachment.size)
