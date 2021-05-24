#!/bin/bash
killall gunicorn

git fetch
git pull

FILE=generation.lock
if test -f "$FILE"; then
    rm generation.lock
fi
FILE=schedule.lock
if test -f "$FILE"; then
    rm schedule.lock
fi

pipenv shell
python migration_script.py
deactivate

pipenv run gunicorn -w 4 --error-logfile log/error.log --access-logfile log/access.log --log-level debug "app:create_app()" &