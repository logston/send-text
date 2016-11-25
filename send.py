#!/usr/bin/env python
'''
This program texts a user when run.
'''
import argparse
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
import smtplib


DIRNAME = os.path.dirname(os.path.abspath(__file__))
USER_NAME = os.environ.get('USER_NAME')
PASSWORD = os.environ.get('PASSWORD')
SMTP_ADDRESS = os.environ.get('SMTP_ADDRESS')
SMTP_PORT = int(os.environ.get('SMTP_PORT'))


def get_us_mms_gateways(carrier):
    with open(os.path.join(DIRNAME, 'gateways.json')) as fp:
        gateways = json.load(fp)

    return set(gateways['mms_carriers']['us'][carrier][1:])


def send_email(recipients=(), sender='', subject='', message='', attachments=()):
    msg = MIMEMultipart() if attachments else MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    if message:
        # Add two spaces to end of message because it seems to get truncated.
        # I don't know why.
        message += '  '
        msg.attach(MIMEText(message))

    if attachments:
        for attachment in attachments:
            with open(attachment, 'rb') as fp:
                img = MIMEImage(fp.read())
            msg.attach(img)

    # Send the email via our own SMTP server.
    s = smtplib.SMTP_SSL(SMTP_ADDRESS, SMTP_PORT)
    s.ehlo()
    s.login(USER_NAME, PASSWORD)
    s.send_message(msg)
    s.quit()


def send_mms(number,
             carrier,
             sender,
             subject,
             message='',
             attachments=()):
    gateways = get_us_mms_gateways(carrier)

    recipients = set()
    for gateway in gateways:
        recipients.add(gateway.format(number=number))

    recipients = sorted(recipients)

    for recipient in recipients:
        send_email(
            (recipient,),
            sender=sender,
            subject=subject,
            message=message,
            attachments=attachments,
        )


def main():
    parser = argparse.ArgumentParser('Send text via email')
    parser.add_argument('number')
    args = parser.parse_args()

    gateways = get_us_mms_gateways()
    recipients = sorted(gateway.format(number=args.number) for gateway in gateways)

    send_email(
        recipients,
        sender='noreply@logston.me',
        subject='test subject 3',
        message='test message 3'
        #attachments=('/users/paul/pictures/pyvideo.png',),
    )


if __name__ == '__main__':
    main()

