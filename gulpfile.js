const gulp = require('gulp')
const shell = require('gulp-shell')

function defaultTask(cb) {
    gulp
        .src('**/*', {read: false})
        .pipe(shell(['cp node_modules/d3/dist/d3.min.js app/static/js/libs/d3.min.js']))
        .pipe(shell([
            'cd src/post-editor && echo $PWD && npm run build',
        ]))
        .pipe(shell([
            'cp src/post-editor/dist/post-editor.min.js app/static/js/libs/post-editor.min.js'
        ]));
    //cb();
}

exports.default = defaultTask