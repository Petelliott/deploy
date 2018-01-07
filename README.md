# deploy.py

a little script to deploy your code using webhooks. MIT license

## json configuration

| attribute | description |
|-----------|-------------|
| `ssh_key` | the ssh key that is configured for deployment on your repos. must have no password. if left blank, default ssh key will be used |
| `secret`  | the secret that is provided to GitHub for the webhook. if left blank, signatures will not be checked |
| `projects`| a json object of the projects that are deployed |
| `port`    | the port that the server will run on. defaults to 80 |

### project configuration

the name of a project must correspond to GitHub path of the project with a preceding slash (for now).
 
| attribute | description |
|-----------|-------------|
| `script`  | the valid /bin/sh command that will be executed in your project directory when triggered by GitHub |
| `branch`  | the branch to be run. defaults to master |

### example config

```json
{
    "port": 8000,
    "ssh_key": "~/.ssh/id_ecdsa",
    "secret": "7d38cdd689735b008b3c702edd92eea23791c5f6",
    "projects": {
        "/petelliott/bbs": {
            "script": "make && ./bbs",
            "branch": "testing"
        }
    }
}
```

## running

```
python3 deploy.py config.json
```

## requirements

- python 3.5 or newer
- git 2.3 or newer
