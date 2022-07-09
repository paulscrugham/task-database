# Task Tracking SQL Database w/ Admin Web UI

Based on this project: https://github.com/paulscrugham/cs340-project

This project is task-tracking database with an admin web interface that allows a non-technical user to create/read/update/delete any database entity and modify relationships.

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
