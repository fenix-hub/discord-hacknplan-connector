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

def build_discord_embedded_field(name, value):
    return {
        "name": name,
        "value": value
    }

def get_workitem_link(workitem_info):
    return "https://app.hackplan.com/p/{0}/kanban?categoryId={1}&boardId={2}&taskId={3}&tapId=basicinfo".format(
        workitem_info['ProjectId'], 
        workitem_info['Category']['CategoryId'],
        workitem_info['Board']['BoardId'],
        workitem_info['WorkItemId']
    )

def build_discord_message(content, workitem_info):
    return {
        "content": content,
        "embeds": [
            {
                "fields" : [
                    build_discord_embedded_field("Titolo", workitem_info['Title']),
                    build_discord_embedded_field("Id", "#%s" % workitem_info['WorkItemId']),
                    build_discord_embedded_field("Link", "[👉 hacknplan](%s)" % get_workitem_link(workitem_info))
                ]
            }
        ]
    }

def on_workitem_created(workitem_info):
    print("Workitem #%s created" % workitem_info["WorkItemId"])
    r = requests.post(
        discord_webhook,
        data = {
            build_discord_message(
                "Un nuovo Workitem è stato creato",
                workitem_info
            )
        }
    )
    return r


def on_workitem_updated(workitem_info):
    print("Workitem #%s updated" % workitem_info["WorkItemId"])
    return


def on_workitem_deleted(workitem_info):
    print("Workitem #%s updated" % workitem_info["WorkItemId"])
    return


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<p>RUNNING</p>", "utf-8"))

    def do_POST(self):
        body = response_to_json(self)
        
        hacknplan_event = self.headers.get('X-Hacknplan-Event')
        response = None
        
        match hacknplan_event:
            case 'workitem.created':
                response = on_workitem_created(body)
            case 'workitem.updated':
                response = on_workitem_updated(body)
            case 'workitem.deleted':
                response = on_workitem_deleted(body)    
        
        self.send_response(response.status_code)


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