(function() {
    "use strict";

    var args = require('system').args;
    var page = require('webpage').create();

    var len = args.length;

    if ( len < 2) {
        console.log('Please specify the URL.');
        phantom.exit(1);
    }

    var url = args[1];

    if (len > 2) {
        page.settings.resourceTimeout = parseInt(args[2], 10) * 1000;
    }
    else {
        // Default 5s
        page.settings.resourceTimeout = 5000;
    }


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


    var timeoutIds = [];
    page.onResourceTimeout = function(request) {
        timeoutIds.push(request.id);
    };


    page.open(url, function(status) {
        page.endTime = new Date();
        page.status = status;

        var urls = [];
        if (status === "success") {
            urls = page.evaluate(function() {
                var lis = document.querySelectorAll("a");
                return Array.prototype.map.call(lis, function(a) {
                    return a.href;
                });
            });
        }

        // Set the timeouted resources as timeouted
        for (var i=0; i<timeoutIds.length; i++) {
            var res = page.resources[timeoutIds[i]];
            res.endReply.statusText = 'Request Time-out';
            res.endReply.status = 408;
        }

        console.log(JSON.stringify({
            resources: page.resources,
            status: status,
            startTime: page.startTime,
            endTime: page.endTime,
            urls: urls
        }));
        phantom.exit(0);
    });
})();
