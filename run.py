#!/usr/bin/env python

import argparse
import csv
import datetime
import glob
import os
import random

from send import send_mms

DIRNAME = os.path.dirname(os.path.abspath(__file__))
RELATIVE_NUMBERS_DIR = 'numbers'
PROGRESS_FILENAME = 'progress.csv'

# Headers
# Time Sent, File Path


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('number')
    args = parser.parse_args()

    number_dir = os.path.join(DIRNAME, RELATIVE_NUMBERS_DIR, args.number)

    file_path = get_next_file_path_for_number(number_dir)

    message = ''
    attachments = ()
    if file_path.endswith('txt'):
        with open(file_path) as fp:
            message = fp.read().replace('\n', '').strip()
    else:
        attachments = (file_path,)

    send_mms(
        args.number,
        carrier='t_mobile',
        sender='noreply@logston.me',
        subject=None,  # message in text
        message=message,
        attachments=attachments,
    )

    progress_file_path = os.path.join(number_dir, PROGRESS_FILENAME)
    with open(progress_file_path, 'a') as fp:
        writer = csv.writer(fp)
        now = str(datetime.datetime.utcnow())
        writer.writerow([now, file_path])


if __name__ == '__main__':
    main()

