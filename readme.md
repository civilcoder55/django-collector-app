# TheCollectorApp

> Open source Django web app and twitter bot to pull twitter threads into blog post to read/save easily .

## Table of contents

- [General info](#general-info)
- [Screenshots](#screenshots)
- [Technologies](#technologies)
- [Setup](#setup)
- [Features](#features)
- [TO DO](#TO-DO)

## General info

## Screenshots

<img src="/screenshots/3FnDyDJ22N.gif?raw=true">
<img src="/screenshots/2020-09-22_204753.png?raw=true">
<img src="/screenshots/2020-09-22_204856.png?raw=true">
<img src="/screenshots/2020-09-22_205014.png?raw=true">
<img src="/screenshots/2020-09-22_204839.png?raw=true">

## Technologies

- Django - version 3.0.1
- tweepy - version 3.8.0
- social_django
- channels

## Setup

- make sure you have redis setup on 127.0.0.1:6379
- edit .env file with right keys
- setup python libraries `pip install -r requirements.txt`
- run the bot with `python manage.py runscript TwitterBot.py`
- run the server with `python manage.py runserver`
- go to 127.0.0.1:8000 and start using the project

you can see demo here [thecollect0rapp.com](https://thecollect0rapp.com)

## Features

List of features ready and TODOs for future development

- authentication system
- social login
- two factor authentication on noraml login and socail login
- add comments and able to like/dislike posts
- able to download post as pdf
- simple web socket to notify user when new post added

## TO DO

- [x] save all threads media on aws s3 (if thread deleted from twitter it will remain in thecollect0rapp.com )
- [ ] refactor some code
- [ ] adding some comments
