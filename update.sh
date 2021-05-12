#!/bin/bash
killall gunicorn

git fetch
git pull

rm generation.lock
rm schedule.lock

pipenv run gunicorn -w 4 --error-logfile log/error.log --access-logfile log/access.log --log-level debug "app:create_app()" &