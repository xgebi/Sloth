#!/usr/bin/env bash

browserify app/static/js/dev/analytics.js | uglifyjs > app/static/js/analytics.js