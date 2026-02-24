#!/bin/sh

if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for MySQL at $MYSQL_DB_HOST:$MYSQL_DB_PORT..."

    while ! nc -z -w 2 "$MYSQL_DB_HOST" "$MYSQL_DB_PORT"; do
        echo "Waiting for MySQL at $MYSQL_DB_HOST:$MYSQL_DB_PORT..."
        sleep 1
    done

    echo "MySQL started"
fi

if [ "$RUN_MIGRATIONS" = "true" ]
then
    echo "Running migrations...."
    python3 manage.py makemigrations
    python3 manage.py migrate
    echo "yes"

    echo "Running collectstatic..."
    python manage.py collectstatic --verbosity 3 --noinput
    echo "yes" 
fi

# Finally, start the actual server
exec "$@"
