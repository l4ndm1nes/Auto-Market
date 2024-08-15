# Auto-Market
Django pet project
___
## Instruction how to run a project with Docker
Before starting the project, you need to set .env file to ./docker directory
```
DEBUG=
SECRET_KEY=
DOMAIN_NAME=

ALLOWED_HOSTS=

DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
DATABASE_PORT=
```
After that run Docker using these commands:
```
docker-compose up -d --build
```
By this url you can achieve the site: http://127.0.0.1:8000/