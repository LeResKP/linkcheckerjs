var http = require('http');
var path = require('path');
var fs = require('fs');

var PORT = 8080;

function handleRequest(request, response){
    console.log(request.url);
    var url;
    if (request.url === '/redirect-301') {
        response.writeHead(301, {'Location': 'http://localhost:' + PORT});
        response.end();
        return;
    }

    if (request.url === '/redirect-302') {
        response.writeHead(302, {'Location': 'http://localhost:' + PORT});
        response.end();
        return;
    }

    if (request.url.indexOf('redirect-static-301') !== -1) {
        url = request.url.replace('redirect-static-301', 'static');
        response.writeHead(301, {'Location': 'http://localhost:' + PORT + url});
        response.end();
        return;
    }

    if (request.url.indexOf('redirect-static-302') !== -1) {
        url = request.url.replace('redirect-static-302', 'static');
        response.writeHead(302, {'Location': 'http://localhost:' + PORT + url});
        response.end();
        return;
    }

    var filePath = '.' + request.url;
    if (filePath == './')
        filePath = './index.html';
    filePath = path.resolve(__dirname, filePath);
    fs.exists(filePath, function(exists) {
        if (exists) {
            fs.readFile(filePath, function(error, content) {
                if (error) {
                    response.writeHead(500);
                    response.end();
                }
                else {
                    // TODO: use the right content type
                    response.writeHead(200, { 'Content-Type': 'text/html' });
                    response.end(content, 'utf-8');
                }
            });
        }
        else {
            response.writeHead(404);
            response.end();
        }
    });
}

var server = http.createServer(handleRequest);

server.listen(PORT, function(){
    console.log("Server listening on: http://localhost:%s", PORT);
});