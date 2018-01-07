"""
handles post requests from github webhooks
"""
import sys
import http.server
import json
import subprocess
import os

instances = {}


class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path not in CONFIG:
            self.send_response(404)
            self.end_headers()
            return

        req_len = int(self.headers['Content-Length'])
        req_data = json.loads(self.rfile.read(req_len).decode("utf-8"))
        
        print("deploying", self.path)

        if self.path in instances:
            # properly kill all children of our process
            subprocess.run(["pkill", "-TERM", "-P", str(instances[self.path].pid)])

        if os.path.isdir("./"+self.path):
            subprocess.run(["git", "-C", "./"+self.path, "pull", "git@github.com:{}.git".format(self.path)])
        else:
            subprocess.run(["git", "clone", "git@github.com:{}.git".format(self.path), "./"+self.path])
        
        if self.path in instances:
            # make sure that the previous instance is done
            instances[self.path].wait()
        
        instances[self.path] = subprocess.Popen(["sh", "-c", CONFIG[self.path]["script"]], cwd="./"+self.path)

        print("deployed", self.path, "pid={}".format(instances[self.path].pid))
        self.send_response(200)
        self.end_headers()
 

if __name__ == "__main__":
     CONFIG = json.load(open(sys.argv[1]))

     httpd = http.server.HTTPServer(('', 8000), WebhookHandler)
     httpd.serve_forever()
