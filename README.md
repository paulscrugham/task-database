# Task Tracking SQL Database w/ Admin Web UI

Based on this project: https://github.com/paulscrugham/cs340-project in collaboration with [legendMK13](https://github.com/legendMK13)

This project is task-tracking database with an admin web interface that allows a non-technical user to create/read/update/delete any database entity and modify relationships. 

This project was completed as a part of the course CS340 - Databases at Oregon State University.

# Pages

The database stores four entities (Tasks, Users, Tags, and Badges) with the web application supporting CRUD operations for each entity.

## Tasks Page

![main page](README/image-007.png)

The database stores four entities:

1. Tasks
2. Users
3. Tags
4. Badges

## Steps for installing app server

1. `virtualenv venv -p $(which python3)`

2. `source ./venv/bin/activate`

3. `pip3 install --upgrade pip`
4. `pip install -r requirements.txt`

## Steps for running server
1. `python -m flask run -h 0.0.0.0 -p [port number] --reload`
