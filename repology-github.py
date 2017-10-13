#!/usr/bin/env python3
#
# Copyright (C) 2017 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of repology
#
# repology is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# repology is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with repology.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import datetime
import os
import sys
import time

import requests

import repology.config
from repology.database import Database


def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-D', '--dsn', default=repology.config.DSN, help='database connection params')
    options = parser.parse_args()

    database = Database(options.dsn, readonly=False, autocommit=True)

    headers = {'User-Agent': 'Repology GitHub tag fetcher/0'}

    if hasattr(repology.config, 'GITHUB_TOKEN'):
        headers['Authorization'] = 'token ' + repology.config.GITHUB_TOKEN

    projects = database.GetGithubProjects()

    for n, (account, project) in enumerate(projects):
        print('[{:6.2f}%] {}/{}: '.format(100.0 * n / len(projects), account, project), file=sys.stderr, end='')
        reply = requests.get('https://api.github.com/repos/{}/{}/tags'.format(account, project), headers=headers, timeout=5)
        if reply.status_code != 200:
            print('error {}'.format(reply.status_code), file=sys.stderr)
            continue

        database.UpdateGithubTags(account, project, [tag['name'] for tag in reply.json()])

        remaining = int(reply.headers['X-RateLimit-Remaining'])
        limit = int(reply.headers['X-RateLimit-Limit'])
        reset = int(reply.headers['X-RateLimit-Reset'])

        print('OK, {}/{} request budget'.format(remaining, limit), file=sys.stderr)

        if limit == 0:
            sleepfor = reset - datetime.datetime.now().timestamp() + 5

            if sleepfor > 0:
                print('    budget exceeded, sleeping for {} secs'.format(limit, remaining, sleepfor), file=sys.stderr)

                time.sleep(sleepfor)

    database.commit()


if __name__ == '__main__':
    os.sys.exit(Main())
