# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import requests
import os
import simplejson

hostName = "0.0.0.0"
serverPort = os.environ['PORT']

discord_webhook = os.environ['DISCORD_WEBHOOK']

def response_to_json(response):
    return simplejson.loads(response.rfile.read(int(response.headers.get('Content-Length'))))

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<p>RUNNING</p>", "utf-8"))

    def do_POST(self):
        body = response_to_json(self)
        print(body)
        
        # r = requests.post(
        #     discord_webhook,
        #     data = {
        #         body['message']
        #     }
        # )
        
        self.send_response(r.status_code)


if __name__ == "__main__":        
    webServer = HTTPServer((hostName, int(serverPort)), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    print("Dicord Webhook set to: %s" % discord_webhook)
    
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")