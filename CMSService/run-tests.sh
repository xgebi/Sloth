#!/bin/sh
if test -f schedule.lock; then
    mv schedule.lock schedule.lock.bak
fi
if test -f registration.lock; then
    mv registration.lock registration.lock.bak
fi
if test -f rss.lock; then
    mv rss.lock rss.lock.bak
fi
if test -f generating.lock; then
    mv generating.lock rss.lock.bak
fi
if test ! -d site_test; then
  mkdir "site_test"
fi
killall twistd
rm twistd.pid
python run.py &
twistd -no web --path=site_test &
npm run cy:run
mv schedule.lock.bak schedule.lock
mv registration.lock.bak registration.lock
mv rss.lock.bak rss.lock