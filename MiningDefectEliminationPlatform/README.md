# DEP.

https://dep.fmgl.com.au
https://dep.fmgl.com.au/api/docs#

# Contact:

jwhite@fmgl.com.au
jrow@fmgl.com.au

### aws

https://fmgl.awsapps.com/start#/

### dev ops

https://devops.fmgl.com.au/tfs/Primary/The%20Defect%20Elimination%20Platform/_boards/board/t/The%20Defect%20Elimination%20Platform%20Team/Backlog%20items

### snowflake

https://wn74261.ap-southeast-2.snowflakecomputing.com/console#/internal/worksheet

### Prod

```
  # access
  aws sso login --profile Asset
  ssh -N -D 9090 fmg
  /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --user-data-dir="$HOME/proxy-profile" --proxy-server="socks5://localhost:9090" --proxy-bypass-list="localhost"

  # access logs
  ssh dep
  sudo su gitlab-runner
  sudo docker logs -f dep_backend
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
  sudo docker logs -f dep_backend

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
sudo docker container exec dep_backend alembic revision --autogenerate -m "revision title/notes go here"

sudo docker container exec dep_backend alembic upgrade head

sudo docker container exec dep_backend alembic downgrade -1

sudo docker container exec dep_backend alembic history

sudo docker container exec dep_backend alembic merge heads -m "name"
```

### Standards

Please follow the relevant document posted on Google drive. Quick links are listed below.

- https://github.com/airbnb/javascript
- https://sass-lang.com/
- https://docs.python.org/3/library/

### Useful things

- https://martinheinz.dev/blog/28 (Advanced SQLAlchemy Features You Need To Start Using)
