"""
handles post requests from github webhooks
"""
import sys
import http.server
import json
import subprocess
import os
import hmac
import hashlib


def get_get_config(path):
    """
    given the path of a json config file,
    returns a function that will give the current config
    """
    conf_time = -float("inf")
    config = None

    def get_config():
        new_cnf_tme = os.path.getmtime(path)
        if new_cnf_tme > conf_time:
            # reload config
            config = json.load(open(path))
            
            config["git_env"] = os.environ.copy()
            if "ssh_key" in config:
                config["git_env"]["GIT_SSH_COMMAND"] = "ssh -i " + config["ssh_key"]

            for proj in config["projects"].items():
                if "branch" not in proj:
                    proj["branch"] = "master"

            if "port" not in config:
                config["port"] = 80

        return config
    
    return get_config


def make_handler(get_config):
    instances = {}

    class WebhookHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self): 
            config = get_config()
                        
            if self.path not in config["projects"]:
                self.send_response(404)
                self.end_headers()
                return

            req_len = int(self.headers['Content-Length'])
            req_bytes = self.rfile.read(req_len)
            # the following line currently has no use, but will be used in the future
            # req_data = json.loads(req_bytes.decode("utf-8"))
            
            if "secret" in config:
                req_sig = self.headers["X-Hub-Signature"]
                
                if req_sig is None:
                    print("rejecting deployment: no signature")
                    self.send_response(403)
                    self.end_headers()
                    return
                
                hmac_bytes = hmac.new(config["secret"].encode("utf-8"), req_bytes, hashlib.sha1).digest()
                hmac_sig = "sha1=" + hmac_bytes.hex()

                if not hmac.compare_digest(hmac_sig, req_sig):
                    print("rejecting deployment: bad signature")
                    self.send_response(403)
                    self.end_headers()
                    return

            print("deploying", self.path)

            if os.path.isdir("./"+self.path):
                subprocess.run(["git", "-C", "./"+self.path, "checkout", config[projects][self.path]["branch"]])
                subprocess.run(["git", "-C", "./"+self.path, "pull", "git@github.com:{}.git".format(self.path)], env=config["git_env"])
            else:
                subprocess.run(["git", "clone", "git@github.com:{}.git".format(self.path), "./"+self.path], env=config["git_env"])
                subprocess.run(["git", "-C", "./"+self.path, "checkout", config[projects][self.path]["branch"]])
                subprocess.run(["git", "-C", "./"+self.path, "pull"], env=config["git_env"])
            
            if self.path in instances:
                # kill the previous instance and make sure it completes
                subprocess.run(["pkill", "-TERM", "-P", str(instances[self.path].pid)])
                instances[self.path].wait()
            
            instances[self.path] = subprocess.Popen(config["projects"][self.path]["script"], cwd="./"+self.path, shell=True)

            print("deployed", self.path, "pid={}".format(instances[self.path].pid))
            self.send_response(200)
            self.end_headers()

    return WebHookHandler
     

if __name__ == "__main__":
    get_config = get_get_config(sys.argv[1])
    WebhookHandler = make_handler(get_config) 

    httpd = http.server.HTTPServer(('', get_config()["port"]), WebhookHandler)
    httpd.serve_forever()
