var args = require('system').args;
var page = require('webpage').create();

var len = args.length;

if ( len < 2) {
    console.log('Please specify the URL.');
    phantom.exit(1);
}


var page_status,
    url = args[len - 1],
    resources = [],
    abort = false,
    urlOnly = (len === 3 && args[1] === '--url-only');

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
        if (response.id === 1 && (response.status === 301 || response.status === 302 || urlOnly)) {
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
        if (response.id === 1) {
            page_status = o;
        }
        else {
            resources.push(o);
        }
    }
};


page.onError = function(msg, trace) {
    // Ignore javascript errors for now.
};


page.open(url, function(status) {
    // When we abort with status_code == 200, success is triggered
    // When we abort with status_code in [301, 302] fail is triggered
    if (status === "success") {
        var links = [];
        if (! urlOnly) {
            links = page.evaluate(function() {
                var lis = document.querySelectorAll("a");
                return Array.prototype.map.call(lis, function(a) {
                    return a.href;
                });
            });
        }
        console.log(JSON.stringify({
            'page': page_status,
            'resources': resources,
            'urls': links
        }, undefined, 4));
        phantom.exit(0);
    }
    else {
        if (abort && !urlOnly) {
            // abort because of redirect
            console.log(JSON.stringify({
                'page': page_status,
                'resources': resources,
                'urls': [page_status.redirect_url]}, undefined, 4));
            phantom.exit(0);
        }
        else {
            // Can't open the url
            console.log(JSON.stringify({
                'page': {
                    'url': url,
                    'status_code': 500,
                    'status': 'Unable to open URL'

                },
                'resources': [],
                'urls': []}));
            phantom.exit(1);
        }
    }
});
