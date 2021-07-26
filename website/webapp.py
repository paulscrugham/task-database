from flask import Flask, render_template
from flask import request, redirect
from db_connector.db_connector import connect_to_database, execute_query
#create the web application
webapp = Flask(__name__)

#provide a route where requests on the web application can be addressed
@webapp.route('/hello')
#provide a view (fancy name for a function) which responds to any requests on this route
def hello():
    return "Hello World!"

@webapp.route('/dbtest')
def index():
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = 'SELECT * FROM Tasks;'
        values = execute_query(db_connection, query).fetchall()
        print(values)
    return render_template('home.html', results=values)


# app routes for Badges page

@webapp.route('/show_badges')
def show_badges():
    db_connection = connect_to_database()
    query = 'SELECT b.badge_id, b.name, t.name, b.criteria FROM Badges b LEFT JOIN Tags t ON b.tg_id = t.tag_id;'
    results = execute_query(db_connection, query).fetchall()
    print(results)
    return render_template('show_badges.html', badges=results)

@webapp.route('/add_badge', methods=['POST', 'GET'])
def add_badge():
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = 'SELECT tag_id, name from Tags;'
        result = execute_query(db_connection, query).fetchall()
        print(result)
        return render_template('add_badge.html', tags=result)

    elif request.method == 'POST':
        print('Adding a Badge...')
        print(request.form['badge_name'])
        print(request.form['badge_criteria'])
        badge_name = request.form['badge_name']
        badge_criteria = request.form['badge_criteria']
        badge_tag = request.form['badge_tag']

        query = 'INSERT INTO Badges(name, tg_id, criteria) VALUES (%s, %s, %s);'
        data = (badge_name, badge_tag, badge_criteria)
        execute_query(db_connection, query, data)
        return show_badges()

@webapp.route('/delete_badge/<int:id>')
def delete_people(id):
    db_connection = connect_to_database()
    query = 'DELETE FROM Badges WHERE badge_id = %s;'
    data = (id,)

    result = execute_query(db_connection, query, data)
    return (str(result.rowcount) + " row deleted")
