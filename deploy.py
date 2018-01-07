"""
handles post requests from github webhooks
"""
import sys
import http.server
import json
import subprocess
import os
import hmac

instances = {}


class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path not in CONFIG["projects"]:
            self.send_response(404)
            self.end_headers()
            return

        req_len = int(self.headers['Content-Length'])
        req_bytes = self.rfile.read(req_len)
        req_data = json.loads(req_bytes.decode("utf-8"))
        
        if "secret" in CONFIG:
            req_sig = self.headers["X-Hub-Signature"]
            hmac_bytes = hmac.new(CONFIG["secret"].encode("utf-8"), msg=req_bytes).digest()
            hmac_sig = "sha1=" + hmac_bytes.hex()

            if hmac_sig != req_sig:
                print("rejecting deployment: bad signature")
                self.send_response(403)
                self.end_headers()
                return


        print("deploying", self.path)

        if self.path in instances:
            # properly kill all children of our process
            subprocess.run(["pkill", "-TERM", "-P", str(instances[self.path].pid)])

        if os.path.isdir("./"+self.path):
            subprocess.run(["git", "-C", "./"+self.path, "pull", "git@github.com:{}.git".format(self.path)], env=GIT_ENV)
        else:
            subprocess.run(["git", "clone", "git@github.com:{}.git".format(self.path), "./"+self.path], env=GIT_ENV)
        
        if self.path in instances:
            # make sure that the previous instance is done
            instances[self.path].wait()
        
        instances[self.path] = subprocess.Popen(CONFIG["projects"][self.path]["script"], cwd="./"+self.path, shell=True)

        print("deployed", self.path, "pid={}".format(instances[self.path].pid))
        self.send_response(200)
        self.end_headers()
 

if __name__ == "__main__":
    CONFIG = json.load(open(sys.argv[1]))
    
    GIT_ENV = os.environ.copy()
    if "ssh_key" in CONFIG:
        GIT_ENV["GIT_SSH_COMMAND"] = "ssh -i " + CONFIG["ssh_key"]
    
    if "port" in CONFIG:
        port = CONFIG["port"]
    else:
        port = 80

    httpd = http.server.HTTPServer(('', port), WebhookHandler)
    httpd.serve_forever()
