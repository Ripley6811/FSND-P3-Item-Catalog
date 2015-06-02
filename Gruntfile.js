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
            },
            sphinx: {
                files: ['vagrant/catalog/*.py'],
                tasks: ['shell'],
                options: {
                    spawn: false
                }
            }
        },
        shell: {
            target: {
                command: 'make html'
            }
        }
    });

    // Load plugins for tasks.
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-readme');
    grunt.loadNpmTasks('grunt-shell');

    // Default task(s).
    grunt.registerTask('default', ['readme', 'shell', 'watch']);
};