# Pomodoro App

## Steps for installing app server

1. `virtualenv venv -p $(which python3)`

2. `source ./venv/bin/activate`

3. `pip3 install --upgrade pip`
4. `pip install -r requirements.txt`

## Steps for running server
1. `python -m flask run -h 0.0.0.0 -p [port number] --reload`