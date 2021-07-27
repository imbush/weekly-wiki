from datetime import datetime
import json
import email
import imaplib


def main():
    """
    Functions:
        1. Update JSON emails, topics, and date.
        2. Selects weekly post for each subscriber.
        3. Sends wiki article.
    """
    json_name = "emails.json"
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

    # Get emails since last update
    last_update = email_json.last_update
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)
    mail.login(from_email, from_password)
    mail.select('inbox')
    
    # Process emails through email_json

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

    for email, topic in email_json.email_dict:
        # Get email, send email
        pass


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
    # main()
    pass
