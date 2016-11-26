from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
import smtplib


DIRNAME = os.path.dirname(os.path.abspath(__file__))


def get_us_mms_gateways(carrier):
    with open(os.path.join(DIRNAME, 'gateways.json')) as fp:
        gateways = json.load(fp)

    return gateways['mms_carriers']['us'][carrier][1]


def get_us_sms_gateways(carrier):
    with open(os.path.join(DIRNAME, 'gateways.json')) as fp:
        gateways = json.load(fp)

    return gateways['sms_carriers']['us'][carrier][1]


def build_sms(number,
              carrier,
              sender,
              subject,
              message):

    gateway = get_us_sms_gateways(carrier)
    recipient = gateway.format(number=number)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    # Add two spaces to end of message because it seems to get truncated.
    # I don't know why.
    msg.attach(MIMEText(message + '  '))

    return msg


def build_mms(number,
              carrier,
              sender,
              subject,
              attachments=()):

    gateway = get_us_mms_gateways(carrier)
    recipient = gateway.format(number=number)

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    for attachment in attachments:
        with open(attachment, 'rb') as fp:
            img = MIMEImage(fp.read())
        msg.attach(img)

    return msg


def send_message(smtp_address,
                 smtp_port,
                 smtp_username,
                 smtp_password,
                 number,
                 carrier,
                 sender,
                 subject,
                 message=None,
                 attachments=()):

    smtp_server = smtplib.SMTP_SSL(smtp_address, smtp_port)
    smtp_server.ehlo()
    smtp_server.login(smtp_username, smtp_password)

    if attachments:
        msg = build_mms(
            number=number,
            carrier=carrier,
            sender=sender,
            subject=subject,
            attachments=attachments,
        )
    else:
        msg = build_sms(
            number=number,
            carrier=carrier,
            sender=sender,
            subject=subject,
            message=message,
        )

    smtp_server.send_message(msg)
    smtp_server.quit()

