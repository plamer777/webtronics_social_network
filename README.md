# The Webtronics Social Network API
This application is a part of API for social network.

The app provides functionality as follows:
 - Register, login a user
 - Update user data
 - Delete current user
 - Update user data and delete users
 - Create, update, delete posts
 - Like and dislike any post except your own
 
---

**Technologies used in the project:**
 
 - Fast-API 
 - SQLAlchemy
 - Alembic
 - Uvicorn 
 - Pydantic
 - Email-validate
 - PyJWT
 - Docker
 - Docker-compose

---

**Project's structure:**
 
 - dao - data access objects to work with database
 - services - service objects with business logic
 - routers - FastAPI routers to split application into logical parts
 - settings.py - constants to configure the application
 - images - user avatars and post pictures
 - container.py - DAO and Service instances
 - Docker-compose.yaml - main file to start the application by using Docker
 - Dockerfile - description of the image to create API container
 - migrations - alembic files with DB migrations
 - main.py - file with FastApi application to start
 - utils.py - utility functions
 - requirements.txt - project dependencies
 - README.md - this file with project description
---

**How to start the project:**
The app is ready to install out of the box. There are three containers in the docker - db providing database,
api with the application and alembic migrations.
To start the app just follow the next steps:
 - Clone the repository (you need only docker-compose.yaml and .env and project description file actually)
 - Install docker and docker-compose packages by the command `sudo apt install docker.io docker-compose`
 - Prepare .env file using an example .env-example file
 - Prepare docker-compose.yaml file (change settings such as ports, images if you need)
 - Start the app by using `sudo docker-compose up -d` command
 - The main page with swagger will be available by the url http://localhost/ (if started locally) or http://yourdomain/ 
(if started on a VPS)
 - After that application is ready to process requests


The project was created by Alexey Mavrin in 16 July 2023