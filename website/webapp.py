from flask import Flask, render_template
from flask import request, redirect
from db_connector.db_connector import connect_to_database, execute_query
#create the web application
webapp = Flask(__name__)

#provide a route where requests on the web application can be addressed
@webapp.route('/hello')
#provide a view (fancy name for a function) which responds to any requests on this route
def hello():
    return "Hello World!";

@webapp.route('/')
def index():
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = 'SELECT * FROM Tasks;'
        values = execute_query(db_connection, query).fetchall()
        print(values)
    return render_template('home.html', results=values)
