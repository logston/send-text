#!/usr/bin/env python

import argparse
import csv
import datetime
import glob
import os
import random
import sys

from send import send_message

DIRNAME = os.path.dirname(os.path.abspath(__file__))
RELATIVE_NUMBERS_DIR = 'numbers'
PROGRESS_FILENAME = 'progress.csv'

SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
SMTP_ADDRESS = os.environ.get('SMTP_ADDRESS')
SMTP_PORT = int(os.environ.get('SMTP_PORT'))


def get_next_file_path_for_number(number_dir):
    if not os.path.exists(number_dir):
        os.makedirs(number_dir)

    progress_file_path = os.path.join(number_dir, PROGRESS_FILENAME)
    if not os.path.exists(progress_file_path):
        with open(progress_file_path, 'x'):
            pass

    with open(progress_file_path) as fp:
        reader = csv.reader(fp)
        rows = list(reader)

    # Headers: Time Sent, File Path
    files_sent = set(os.path.basename(row[1]) for row in rows)

    files_cached = []
    extentions = ['txt', 'png', 'jpg']
    for extention in extentions:
        pattern = number_dir.rstrip('/') + '/*.{}'.format(extention)
        files_cached += glob.glob(pattern)

    files_cached = set(os.path.basename(f) for f in files_cached)

    unsent_files = files_cached - files_sent

    if not unsent_files:
        raise RuntimeError('No unsent files in number dir')

    unsent_file = random.choice(sorted(unsent_files))
    unsent_file = os.path.join(number_dir, unsent_file)

    return unsent_file


def run(smtp_address,
        smtp_port,
        smtp_username,
        smtp_password,
        number,
        carrier,
        sender):
 
    number_dir = os.path.join(DIRNAME, RELATIVE_NUMBERS_DIR, number)

    file_path = get_next_file_path_for_number(number_dir)

    message = None
    attachments = ()
    if file_path.endswith('txt'):
        with open(file_path) as fp:
            message = fp.read().replace('\n', '').strip()
    else:
        attachments = (file_path,)

    send_message(
        smtp_address,
        smtp_port,
        smtp_username,
        smtp_password,
        number,
        carrier,
        sender,
        subject,
        message=message,
        attachments=attachments,
    )

    progress_file_path = os.path.join(number_dir, PROGRESS_FILENAME)
    with open(progress_file_path, 'a') as fp:
        writer = csv.writer(fp)
        now = str(datetime.datetime.utcnow())
        writer.writerow([now, file_path])


def main():
    parser = argparse.ArgumentParser('Send a text')
    parser.add_argument('-n', '--number')
    parser.add_argument('-c', '--carrier')
    parser.add_argument('-s', '--sender')
    parser.add_argument('-a', '--smtp-address')
    parser.add_argument('-p', '--smtp-port')
    parser.add_argument('-U', '--smtp-username')
    parser.add_argument('-P', '--smtp-password')
    args = parser.parse_args()

    smtp_address = args.smtp_address or os.environ.get('SMTP_ADDRESS')
    smtp_port = args.smtp_port or os.environ.get('SMTP_PORT')
    smtp_username = args.smtp_username or os.environ.get('SMTP_USERNAME')
    smtp_password = args.smtp_password or os.environ.get('SMTP_PASSWORD')
    number = args.number or os.environ.get('NUMBER')
    carrier = args.carrier or os.environ.get('CARRIER')
    sender = args.sender or os.environ.get('SENDER')

    required_args = ('smtp_address', 'smtp_port',
                     'smtp_username', 'smtp_password',
                     'number', 'carrier', 'sender')

    exit = False
    for arg in required_args:
        if not locals().get(arg):
            exit = True
            print('{} not defined'.format(arg))

        if exit: 
            parser.print_help()
            sys.exit(1)

    run(
        smtp_address=smtp_address,
        smtp_port=smtp_port,
        smtp_username=smtp_username,
        smtp_password=smtp_password,
        number=number,
        carrier=carrier,
        sender=sender,
    )


if __name__ == '__main__':
    main()

