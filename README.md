# deploy.py

a little script to deploy your code using webhooks. MIT license

## json configuration

| attribute | description |
|-----------|-------------|
| `ssh_key` | the ssh key that is configured for deployment on your repos. must have no password. if left blank, default ssh key will be used |
| `secret`  | the secret that is provided to GitHub for the webhook. if left blank, signatures will not be checked |
| `projects`| a json object of the projects that are deployed |
| `port`    | the port that the server will run on |

### project configuration

the name of a project must correspond to GitHub path of the project with a preceding slash (for now).
 
| attribute | description |
|-----------|-------------|
| `script`  | the valid /bin/sh command that will be executed in your project directory when triggered by GitHub |

### example config

```json
{
    "port": 8000,
    "ssh_key": "~/.ssh/id_ecdsa",
    "secret": "7d38cdd689735b008b3c702edd92eea23791c5f6",
    "projects": {
        "/petelliott/bbs": {
            "script": "make && ./bbs"
        }
    }
}
```

## running

```
python3 deploy.py config.json
```
