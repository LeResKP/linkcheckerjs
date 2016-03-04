(function() {
    "use strict";

    var args = require('system').args;
    var page = require('webpage').create();

    var len = args.length;

    if ( len < 2) {
        console.log('Please specify the URL.');
        phantom.exit(1);
    }

    var url = args[len - 1];


    page.resources = {};


    page.onLoadStarted = function () {
        page.startTime = new Date();
    };


    page.onResourceRequested = function (req) {
        page.resources[req.id] = {
            request: req,
            startReply: null,
            endReply: null
        };
    };


    page.onResourceReceived = function (res) {
        if (res.stage === 'start') {
            page.resources[res.id].startReply = res;
        }
        if (res.stage === 'end') {
            page.resources[res.id].endReply = res;
        }
    };


    page.onError = function(msg, trace) {
        // Ignore javascript errors for now.
    };

    // timeout = 5s
    page.settings.resourceTimeout = 5000;


    page.open(url, function(status) {
        page.endTime = new Date();
        page.status = status;
        console.log(JSON.stringify(page.resources));
        phantom.exit(0);
    });
})();
