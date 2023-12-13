# Siliq
[![Django lint and deploy to Dockerhub.](https://github.com/frNNcs/siliq/actions/workflows/test_and_deploy.yml/badge.svg)](https://github.com/frNNcs/siliq/actions/workflows/test_and_deploy.yml)

[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/frNNcs/siliq)

## SqlServerOnDocker

docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml run app python manage.py loaddata fixtures/*

python manage.py dumpdata Hiscar.Reparticiones --indent 2 > hiscar_reparticiones.json
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

## To start development:

1. install [docker](https://docs.docker.com/#/components) and [docker-compose](https://docs.docker.com/compose/install/)
2. run `sudo git clone http://git.ips.gba.gov.ar/Francisco/SILIQ.git`
3. run `sudo docker-compose build` to build both containers
4. run `sudo docker-compose up db` to start de db container
5. run `docker ps` to list runing containers
6. run `docker exec -t -i "YOUR CONTAINER ID" bash` to enter to the bash console of the container
7. run `python3 manage.py makemigrations` to create migrations.
8. run `python3 manage.py migrate` to apply migrations. **Important! all migrations will go to master database unless you create new database and update settings.py files**
9. run `python3 manage.py createsuperuser` to create admin account

## Configuring DNS Linux

1. First, create a systemd drop-in directory for the Docker service:
`mkdir /etc/systemd/system/docker.service.d`

2. Now create a file called /etc/systemd/system/docker.service.d/http-proxy.conf that adds the HTTP_PROXY environment variable:
`[Service]
Environment="HTTP_PROXY=http://proxy.example.com:80/"`

3. If you have internal Docker registries that you need to contact without proxying you can specify them via the NO_PROXY environment variable:
`Environment="HTTP_PROXY=http://proxy.example.com:80/"
Environment="NO_PROXY=localhost,127.0.0.0/8,docker-registry.somecorporation.com"`

4. Flush changes:
`$ sudo systemctl daemon-reload`

5. Verify that the configuration has been loaded:
`$ sudo systemctl show --property Environment docker
Environment=HTTP_PROXY=http://proxy.example.com:80/`

6. Restart Docker:
`$ sudo systemctl restart docker`

## Tips Linux

1. Make Tab auto-completion case-insensitive in Bash: `echo set completion-ignore-case on | sudo tee -a /etc/inputrc`

## Node.js & npm throw proxy

1. `npm config set proxy http://proxy.ips.gba.gov.ar:80`
2. `npm config set https-proxy http://proxy.ips.gba.gov.ar:80`

## Configure docker proxy on ubuntu 18.04

/etc/systemd/system/docker.service.d/http-proxy.conf : Check if this file exists in your setup, and if it does not create this file and perform below steps:
Open the file and add below statements in it and save:

- [Service]
- Environment="HTTP_PROXY=<http://proxy.ips.gba.gov.ar:80>"
- Environment="HTTPS_PROXY=<http://proxy.ips.gba.gov.ar:80>"
- Environment="NO_PROXY=localhost,127.0.0.1"

Flush the above changes by running below command

1. `sudo systemctl daemon-reload`
Verify that the above changes have been taken affect by running below commnad. This should print the Environment variable value

2. `sudo systemctl show --property Environment docker`
Once you successfully verify that the variable is set, restart the docker service by running below command:

3. `sudo systemctl restart docker`
~/.docker/config.json : Add below json property to the existing properties in the file

``` json
{
 "proxies": {
   "defaults": {
     "httpProxy":"http://proxy.ips.gba.gov.ar:80",
     "httpsProxy":"http://proxy.ips.gba.gov.ar:80"
   }
 }
}
```

- /etc/default/docker : Open or create this file with below content in it:

1. export http_proxy='http://proxy.ips.gba.gov.ar:80'
2. export https_proxy='http://proxy.ips.gba.gov.ar:80'

## Get log if you lose current Container

`docker logs --f "CONTAINER ID"`

## Producction commands

``` bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start
sudo supervisorctl restart siliq
```

To restart after pull or changes

## For logs

``` bash
cat /var/log/supervisor/siliq.err.log
cat /var/log/supervisor/siliq.out.log
```

## RABBIT MTQ

`sudo rabbitmq-server`


## Archivo Hiscar
- FOHIS001.cbl

## Redis

```bash
config set save ""
set bind 0.0.0.0
save
```