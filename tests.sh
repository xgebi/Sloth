#!/bin/sh
pipenv lock
pipenv install --system --deploy
mv schedule.lock schedule.lock.bak
mv registration.lock registration.lock.bak
mv rss.lock rss.lock.bak
python run.py &
rm -rf node_modules
npm install
npm run cy:test
mv schedule.lock.bak schedule.lock
mv registration.lock.bak registration.lock
mv rss.lock.bak rss.lock