const gulp = require('gulp')
const shell = require('gulp-shell')

function defaultTask(cb) {
    gulp
        .src('**/*', {read: false})
        .pipe(shell(['cp node_modules/d3/dist/d3.min.js app/static/js/libs/d3.min.js']));
    cb();
}

exports.default = defaultTask