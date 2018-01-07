"""
handles post requests from github webhooks
"""
import sys
import http.server
import json

instances = {}

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path not in CONFIG:
            self.send_response(404)
            self.end_headers()
            return

        req_len = int(self.headers['Content-Length'])
        req_data = json.loads(self.rfile.read(req_len).decode("utf-8"))
        
        if (req_data["action"] != "published" or
            (req_data["release"]["prerelease"]
             and not CONFIG[self.path]["prerelease"])):
            # reject the deployment
            self.send_response(200)
            self.end_headers()
            return
        
        print("deploying", self.path)
        self.send_response(200)
        self.end_headers()
 

if __name__ == "__main__":
     CONFIG = json.load(open(sys.argv[1]))

     httpd = http.server.HTTPServer(('', 8000), WebhookHandler)
     httpd.serve_forever()
