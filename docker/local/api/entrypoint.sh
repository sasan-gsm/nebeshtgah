#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python << END
import sys
import time
import psycopg2
unrecoverable_after = 30
start = time.time()
while True:
    try:
        psycopg2.connect(
            dbname="${POSTGRES_DB}",
            user="${POSTGRES_USER}",
            password="${POSTGRES_PASSWORD}",
            host="${POSTGRES_HOST}",
            port="${POSTGRES_PORT}",
        )
        break
    except psycopg2.OperationalError as error:
        sys.stderr.write("Waiting for DB to become online...\n")
        if time.time() - start > unrecoverable_after:
            sys.stderr.write(f"Too long.\n The following error message is being generated:\n {error}\n"
            )
        time.sleep(3)
END

echo >&2 'Database is available'
exec "$@"