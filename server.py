# Python 3 server example
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
import simplejson

from discord_classes import DiscordEmbed, DiscordEmbedField, DiscordMessage

hostName: str = "0.0.0.0"
serverPort: int = int(os.environ['PORT'])

discord_webhook: str = os.environ['DISCORD_WEBHOOK']

def httprq_to_json(httprq: BaseHTTPRequestHandler) -> dict:
    return simplejson.loads(httprq.rfile.read(int(httprq.headers.get('Content-Length'))))

def get_workitem_link(workitem_info: dict) -> str:
    return "https://app.hacknplan.com/p/{0}/kanban?categoryId={1}&boardId={2}&taskId={3}&tabId=basicinfo".format(
        workitem_info['ProjectId'], 
        workitem_info['Category']['CategoryId'],
        workitem_info['Board']['BoardId'],
        workitem_info['WorkItemId']
    )

def build_discord_workitem_message(content: str, workitem_info: dict) -> DiscordMessage:
    return DiscordMessage(
        content,
        [
            DiscordEmbed(
                "Workitem #%s" % workitem_info['WorkItemId'],
                "Informazioni del WorkItem",
                [
                    DiscordEmbedField("Titolo", workitem_info['Title'], True),
                    DiscordEmbedField("Id", "#%s" % workitem_info['WorkItemId'], True),
                    DiscordEmbedField("Link", "[👉 hacknplan](%s)" % get_workitem_link(workitem_info), True)
                ]
            )
        ]
    )

def post_discord_message(discord_webhook: str, discord_message: DiscordMessage) -> requests.Response:
    response: requests.Response = requests.post(
        discord_webhook, 
        json = discord_message.to_dict()
    )
    print("Response Code > %d " % response.status_code)
    if (response.status_code > 299):
        print("Response Message > %s" % response.json())
    return response

def on_workitem_created(workitem_info: dict) -> int:
    print("Workitem #%s created" % workitem_info["WorkItemId"])
    
    message: DiscordMessage = build_discord_workitem_message(
        "🎉 Un nuovo Workitem è stato creato",
        workitem_info
    )
    print(message.to_dict())
    
    r = post_discord_message(discord_webhook, message)
    
    return r.status_code


def on_workitem_updated(workitem_info) -> int:
    print("Workitem #%s updated" % workitem_info["WorkItemId"])

    message: DiscordMessage = build_discord_workitem_message(
        "🟡 Un Workitem è stato aggiornato",
        workitem_info
    )
    print(message.to_dict())
    
    r = post_discord_message(discord_webhook, message)
    
    return r.status_code


def on_workitem_deleted(workitem_info: dict) -> int:
    print("Workitem #%s deleted" % workitem_info["WorkItemId"])

    message: DiscordMessage = build_discord_workitem_message(
        "⛔ Un Workitem è stato eliminato",
        workitem_info
    )
    print(message.to_dict())
    
    r = post_discord_message(discord_webhook, message)
    
    return r.status_code


class WebhookServer(BaseHTTPRequestHandler):
    
    def do_GET(self: BaseHTTPRequestHandler):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("ok", "utf-8"))

    def do_POST(self: BaseHTTPRequestHandler):
        hacknplan_body: dict = httprq_to_json(self)
        hacknplan_event: str = self.headers.get('X-Hacknplan-Event')
        
        print("Webhook from hacknplan: %s > %s" % (hacknplan_event, hacknplan_body))
        
        response_code: int = 500
        
        match hacknplan_event:
            case 'workitem.created':
                response_code = on_workitem_created(hacknplan_body)
            case 'workitem.updated':
                response_code = on_workitem_updated(hacknplan_body)
            case 'workitem.deleted':
                response_code = on_workitem_deleted(hacknplan_body)    
        
        self.send_response(response_code)


if __name__ == "__main__":        
    webServer: BaseHTTPRequestHandler = HTTPServer((hostName, serverPort), WebhookServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    print("Dicord Webhook set to: %s" % discord_webhook)
    
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")