import os
import sys
import datetime
import pytz
from invoke import run, task, exceptions
import getpass
import traceback
import socket
from prompt_toolkit.shortcuts import prompt


DB_NAME = os.environ['RSVP_DB_NAME']
DB_PASS = os.environ['RSVP_DB_PASS']
DB_ADMIN = os.environ['DB_ADMIN']

sudo = f'sudo -u {DB_ADMIN}'


@task
def create_db(ctx):
    results = run('%s psql -lqt | cut -d \| -f 1 | grep -w %s | wc -l' %
                  (sudo, DB_NAME)).stdout
    if '0' not in results:
        print("Database found, dropping db and creating new db")
        run('%s dropdb %s' % (sudo, DB_NAME))
    print("Creating db %s" % DB_NAME)
    run('%s createdb %s' % (sudo, DB_NAME))


@task
def create_user(ctx):
    try:
        run('%s dropuser %s' % (sudo, DB_NAME))
    except exceptions.Failure as e:
        pass
    run('%s createuser -e -l -R -S -D %s' % (sudo, DB_NAME))
    run("""%s psql -d "%s" -c "ALTER USER %s WITH PASSWORD '%s'" """
        % (sudo, DB_NAME, DB_NAME, DB_PASS))


@task
def grant_privilege(ctx):
    run('%s psql -d %s -c \'GRANT ALL PRIVILEGES ON DATABASE %s TO %s;\'' %
        (sudo, DB_NAME, DB_NAME, DB_NAME))


@task
def initialize_db(ctx):
    """
    Initialize the database. If db exists, drop and recreate. Assume DB is running.
    If the database exists, drop the database and user and recreate.
    If we're on an ubuntu server, we need to execute as postgres user.
    Otherwise, we assume mac and execute command without sudo.
    """
    create_db(ctx)
    create_user(ctx)
    grant_privilege(ctx)
    run('python ./manage.py migrate')
