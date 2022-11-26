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

def build_discord_embedded_field(name, value, inline = False):
    return {
        "name": name,
        "value": value,
        "inline": inline
    }

def get_workitem_link(workitem_info):
    
    return "https://app.hacknplan.com/p/{0}/kanban?categoryId={1}&boardId={2}&taskId={3}&tabId=basicinfo".format(
        workitem_info['ProjectId'], 
        workitem_info['Category']['CategoryId'],
        workitem_info['Board']['BoardId'],
        workitem_info['WorkItemId']
    )

def build_discord_workitem_message(content, workitem_info):
    message = {
        "content": content,
        "embeds": [
            {
                "title" : "Workitem #%s" % workitem_info['WorkItemId'],
                "description" : "Informazioni del WorkItem",
                "fields" : [
                    build_discord_embedded_field("Titolo", workitem_info['Title'], True),
                    build_discord_embedded_field("Id", "#%s" % workitem_info['WorkItemId'], True),
                    build_discord_embedded_field("Link", "[👉 hacknplan](%s)" % get_workitem_link(workitem_info), True)
                ]
            }
        ]
    }
    print(message)
    return message

def post_discord_message(discord_webhook, json_data):
    response = requests.post(discord_webhook, json = json_data)
    print("Response Code > %d " % response.status_code)
    print("Response Message > %s" % response_to_json(response.content))
    return response

def on_workitem_created(workitem_info):
    print("Workitem #%s created" % workitem_info["WorkItemId"])
    
    message = build_discord_workitem_message(
        "🎉 Un nuovo Workitem è stato creato",
        workitem_info
    )
    
    r = post_discord_message(discord_webhook, message)
    
    return r.status_code


def on_workitem_updated(workitem_info):
    print("Workitem #%s updated" % workitem_info["WorkItemId"])

    message = build_discord_workitem_message(
        "🟡 Un Workitem è stato aggiornato",
        workitem_info
    )
    
    r = post_discord_message(discord_webhook, message)
    
    return r.status_code


def on_workitem_deleted(workitem_info):
    print("Workitem #%s deleted" % workitem_info["WorkItemId"])

    message = build_discord_workitem_message(
        "⛔ Un Workitem è stato eliminato",
        workitem_info
    )
    
    r = post_discord_message(discord_webhook, message)
    
    return r.status_code


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("ok", "utf-8"))

    def do_POST(self):
        hacknplan_body = response_to_json(self)
        hacknplan_event = self.headers.get('X-Hacknplan-Event')
        
        print("Webhook from hacknplan: %s > %s" % (hacknplan_event, hacknplan_body))
        
        response_code = 500
        
        match hacknplan_event:
            case 'workitem.created':
                response_code = on_workitem_created(hacknplan_body)
            case 'workitem.updated':
                response_code = on_workitem_updated(hacknplan_body)
            case 'workitem.deleted':
                response_code = on_workitem_deleted(hacknplan_body)    
        
        self.send_response(response_code)


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