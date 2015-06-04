module.exports = function(grunt) {
    'use strict';
    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        watch: {
            markdown: {
                files: ['docs/*.md'],
                tasks: ['readme'],
                options: {
                    spawn: false
                }
            }
        }
    });

    // Load plugins for tasks.
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-readme');

    // Default task(s).
    grunt.registerTask('default', ['readme', 'watch']);
};