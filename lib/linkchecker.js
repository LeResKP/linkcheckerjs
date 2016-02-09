var args = require('system').args;
var page = require('webpage').create();
var Logging = require('./logging.js').Logging;

var len = args.length;

if (len < 2) {
    console.log('Please specify the URL.');
    phantom.exit(1);
}

var logLevel;

for(var i=1; i < len; i++) {
    if (args[i].indexOf('=')) {
        var k = args[i].split('=')[0].substr(2);
        var v = args[i].split('=')[1];
        if (k === 'log-level') {
            logLevel = parseInt(v, 10);
        }
    }
}

var url = args[len - 1];
var logger = new Logging(logLevel);


page.onResourceReceived = function (response) {
    if (response.stage === "start") {
        if (response.url.substr(0, 5) !== 'data:' && url.substr(0, 8) === 'https://' && response.url.substr(0, 8) !== 'https://') {
            logger.error(url, response.url, response.status, 'Unsecure resource');
        }
    }
    else if (response.stage === 'end') {
        if (response.status === null && response.url.substr(0, 5) == 'data:') {
            logger.info(url, response.url, response.status, response.statusText);
        }
        else if (response.status < 200) {
            logger.warning(url, response.url, response.status, response.statusText);
        }
        else if (response.status < 300) {
            logger.info(url, response.url, response.status, response.statusText);
        }
        else if (response.status < 400){
            logger.warning(url, response.url, response.status, response.statusText);
        }
        else {
            // Already handled by page.onResourceError
        }
    }
};


page.onResourceError = function(response) {
    logger.error(url, response.url, response.status, response.errorString);
};


page.open(url, function(status) {
    if (status === "success") {
        logger.display();
        phantom.exit(0);
    }
    else {
        console.log("Could not open " + args[1]);
        phantom.exit(1);
    }
});
