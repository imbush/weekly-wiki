from datetime import datetime
from email.message import EmailMessage
import json
import email
import imaplib
import smtplib
import ssl


def main():
    """
    Functions:
        1. Update JSON emails, topics, and date.
        2. Selects weekly post for each subscriber.
        3. Sends wiki article.
    """
    json_name = "emails.json"
    # message_markdown = "message.md"
    from_email = input("Email: ").strip()
    from_password = input("Password: ").strip()
    if input("Would you like to proceed with " + from_email + " (y,n): ").strip() == "n":
        print("Main function aborted.")
        return None

    update_json(from_email, from_password, json_name)

    send_emails(from_email, from_password, json_name)


def update_json(from_email: str, from_password: str, json_name: str):
    """
    Function:
        1. Query last date and time from JSON file.
        2. Based on emails since last date:.
            a. Add subscriber
            b. Remove subscriber
            c. Change subscriber topic
        3. Update date and time in JSON file.
    """
    email_json = json_data(json_name)
    last_update_id = email_json.last_update

    # Get emails since last update
    for subscriber_email, email_subject, email_contents in get_new_emails(from_email, from_password, last_update_id):
        if email_subject.strip().lower() == "subscribe":
            email_json.add_email(subscriber_email)
        elif email_subject.strip().lower() == "unsubscribe":
            email_json.remove_email(subscriber_email)
        elif email_subject.strip().lower() == "topic":
            email_json.change_topic(subscriber_email, email_contents)
        else:
            print("No Action:", subscriber_email,
                  "sent email with subject", email_subject)

    # Change last update and record changes in .json file
    email_json.change_last_update(str(datetime.now()))
    email_json.update_json()


def send_emails(from_email: str, from_password: str, json_name: str):
    """
    Function:
        1. For each subscriber, select weekly post.
        2. Send formatted email with link to wiki.
    """
    email_json = json_data(json_name)

    wiki_link_list = list()  # Contains (email, wiki_link) tuples
    for to_email, topic in email_json.email_dict:
        wiki_link_list.append((to_email, find_wiki_page(topic)))

    display_name = "Weekly Wiki"
    port = 465  # For SSL
    host = "smtp.gmail.com"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host=host, port=port, context=context) as server:
        server.login(from_email, from_password)
        for to_email, wiki_link in wiki_link_list:
            msg = EmailMessage()

            msg["Subject"] = "Your Weekly Wiki!"
            msg["From"] = display_name + f' <{from_email}>'
            msg["To"] = to_email
            msg.set_content(format_msg(wiki_link), subtype="html")

            server.sendmail(from_email, to_email, msg)
            print("Sent email to " + to_email + " about:\n" + wiki_link + "\n")


def format_msg(wiki_link: str):
    """Return html formatted email content."""
    contents = f'''
    <!DOCTYPE html>
    <html>
        <body>
            <div style="text-align:center;">
                <h1>Your Weekly Article:</h1>
                <a href="{wiki_link}">{wiki_link}</a>
            </div>
        </body>
    </html>
    '''
    return contents


def find_wiki_page(topic: str):
    # If all, use random_page function from api
    if topic == "all":
        pass
    else:
        pass


def get_new_emails(from_email: str, from_password: str, last_update_id: int):
    SMTP_SERVER = "imap.gmail.com"
    SMTP_PORT = 993
    imap_server = imaplib.IMAP4_SSL(SMTP_SERVER)

    imap_server.login(from_email, from_password)
    imap_server.select('INBOX')

    _, message_numbers_raw = imap_server.search(None, 'ALL')
    for message_number in message_numbers_raw[0].split():
        _, msg = imap_server.fetch(message_number, '(RFC822)')

        # Parse the raw email message in to a convenient object
        message = email.message_from_bytes(msg[0][1])
        if message.is_multipart():
            multipart_payload = message.get_payload()
            message_contents = ""
            for sub_message in multipart_payload:
                if sub_message.get_content_type().strip() == "text/html":
                    message_contents.append(sub_message.get_payload())
            yield(message["from"], message['subject'], message_contents)
        else:  # Not a multipart message, payload is simple string
            yield(message["from"], message['subject'], message.get_payload())


class json_data:
    def __init__(self, json_name: str):
        self.json_name = json_name

        a_file = open(json_name, "r")
        json_dict = json.load(a_file)
        self.last_update = json_dict['last_update']
        self.email_dict = json_dict['subscriber_list']
        a_file.close()

    def change_last_update(self, new_date: str):
        self.last_update = new_date

    def add_email(self, to_email: str, topic="all"):
        """Adds email if not yet subscribed."""
        if to_email not in self.email_dict:
            self.email_dict[to_email] = {"topic": topic}

    def remove_email(self, to_email: str):
        if to_email in self.email_dict:
            del(self.email_dict[to_email])

    def change_topic(self, to_email: str, topic: str):
        if to_email in self.email_dict:
            self.email_dict[to_email]['topic'] = topic

    def update_json(self):
        json_dict = {
                        'last_update': self.last_update,
                        'subscriber_list': self.email_dict}

        a_file = open(self.json_name, "w")
        json.dump(json_dict, a_file)
        a_file.close()


if __name__ == "__main__":
    main()
