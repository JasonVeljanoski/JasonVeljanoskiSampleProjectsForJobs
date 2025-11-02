# ACE.

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

### Alembic (For every Schema Change)

```
docker container exec ace_backend alembic revision --autogenerate -m "revision title/notes go here"

docker container exec ace_backend alembic upgrade head

docker container exec ace_backend alembic downgrade -1

docker container exec ace_backend alembic history

docker container exec ace_backend alembic merge heads -m "name"
```

### Standard

Please follow the relevant document posted on Google drive. Quick links are listed below.

- https://github.com/airbnb/javascript
- https://sass-lang.com/
- https://docs.python.org/3/library/
