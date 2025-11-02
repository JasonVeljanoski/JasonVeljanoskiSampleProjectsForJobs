ace.

https://ace.fmgl.com.au
https://ace.fmgl.com.au/api/docs#

# DevOps

https://fmgl.visualstudio.com/Action%20Centre%20of%20Excellence/_boards/board/t/Action%20Centre%20of%20Excellence%20Team/Backlog%20items

https://tfs.fmgl.com.au/tfs/Primary/Action%20Centre%20For%20Execution%20(ACE)/_workitems/recentlyupdated/ (old)

### Prod

```
  # access
  aws sso login --profile Asset
  ssh -N -D 9090 uat-ace
  /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --user-data-dir="$HOME/proxy-profile" --proxy-server="socks5://localhost:9090" --proxy-bypass-list="localhost"

  # access logs
  ssh uat-ace
  sudo su gitlab-runner
  sudo docker logs -f ace_backend
```

### Docker

```
  # build the solution
  sudo docker-compose build

  # run the solution
  sudo docker-compose up -d

  # stop the solution
  sudo docker-compose down

  # list of containers
  sudo docker-compose ps

  # logs
  sudo docker logs -f ace_backend

  # generate a secure password for swagger docs
  htpasswd -bnBC 10 "" <password> | tr -d ':\n'

  # bash container
  docker run -it dep_backend bash
```

### Git

```
  # pull the latest repo
  git pull origin master
```

### Connecting To Postgres

```
  # list docker containers
  sudo docker container ls

  # go into interactive mode for the relevant container
  sudo docker container exec -it humanz_db /bin/bash

  # login into db via psql
  psql app admin

  # run a query
  ALTER USER admin WITH PASSWORD "...";
```

### Alembic

```
docker container exec ace_backend alembic revision --autogenerate -m "revision title/notes go here"

docker container exec ace_backend alembic upgrade head

docker container exec ace_backend alembic downgrade -1

docker container exec ace_backend alembic history

docker container exec ace_backend alembic merge heads -m "name"
```

### Standards

Please follow the relevant document posted on Google drive. Quick links are listed below.

- https://github.com/airbnb/javascript
- https://sass-lang.com/
- https://docs.python.org/3/library/

### Useful things

- https://martinheinz.dev/blog/28 (Advanced SQLAlchemy Features You Need To Start Using)
