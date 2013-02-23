# Testing Bonjour Apps

## Bash

### Create a simple HTTP Server

    ```JavaScript
    var http = require('http');
    http.createServer(function (req, res) {
        var data = '';
        req.on('data', function(chunk) {
            data += chunk;
        }).on('end', function() {
            console.log(data);
            data = '';
        });
        res.statusCode = 200;
        res.end()
    }).listen(1337, '0.0.0.0');
    console.log('Server running at http://127.0.0.1:1337/');
    ```

    ```python
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

    class BonjourService(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers['content-length'])
            content = self.rfile.read(content_length)
            print "Received: ", content
            self.send_response(200)


    if __name__ == '__main__':
        print "Press Ctrl-c to exit..."
        try:
            httpd = HTTPServer(('0.0.0.0', 1337), BonjourService)
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
    ```


### Use the `dns-sd` command to register the service

    dns-sd -R "Local AirBoard Service" _airboard._tcp. local. 1337

### Use pybonjour to register the service

    ```python
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

    import select
    import pybonjour


    class BonjourService(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers['content-length'])
            content = self.rfile.read(content_length)
            print "Received: ", content
            self.send_response(200)

    def register_service():
        def callback(sdRef, flags, errorCode, name, regtype, domain):
            if errorCode == pybonjour.kDNSServiceErr_NoError:
                print "service registered..."

        sdRef = pybonjour.DNSServiceRegister(
            name='Local AirBoard Service',
            regtype='_airboard._tcp.',
            domain='local.',
            port=1337,
            callBack=callback)

        while True:
            ready = select.select([sdRef], [], [])
            if sdRef in ready[0]:
                pybonjour.DNSServiceProcessResult(sdRef)
                break

        return sdRef


    if __name__ == '__main__':
        sdRef = register_service()
        httpd = HTTPServer(('0.0.0.0', 1337), BonjourService)
        try:
            print "Press Ctrl-c to exit..."
            httpd.serve_forever()
        except KeyboardInterrupt:
            sdRef.close()
    ```
