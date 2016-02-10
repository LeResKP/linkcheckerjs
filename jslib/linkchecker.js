var args = require('system').args;
var page = require('webpage').create();

if (args.length != 2) {
    console.log('Please specify the URL.');
    phantom.exit(1);
}

var url = args[1],
    resources = [],
    abort = false;


page.onResourceRequested = function(requestData, networkRequest) {
    if (abort) {
        networkRequest.abort();
    }
};


page.onResourceReceived = function (response) {
    if (abort) {
        return;
    }

    if (response.stage === 'end') {
        if (response.id === 1 && (response.status === 301 || response.status === 302)) {
            abort = true;
        }
        // For now only get a part of the response
        var o = {
            'url': url,
            'response_url': response.url,
            'redirect_url': response.redirectURL,
            'status_code': response.status,
            'status': response.statusText
        };
        resources.push(o);
    }
};


page.onError = function(msg, trace) {
    // Ignore javascript errors for now.
};


page.open(url, function(status) {
    if (status === "success") {
        var links = page.evaluate(function() {
            var lis = document.querySelectorAll("a");
            return Array.prototype.map.call(lis, function(a) {
                return a.href;
            });
        });
        console.log(JSON.stringify({
            'resources': resources,
            'urls': links
        }, undefined, 4));
        phantom.exit(0);
    }
    else {
        if (abort) {
            console.log(JSON.stringify({
                'resources': resources,
                'urls': [resources[0].redirect_url]}, undefined, 4));
            phantom.exit(0);
        }
        else {
            console.log("Could not open " + url);
            phantom.exit(1);
        }
    }
});
