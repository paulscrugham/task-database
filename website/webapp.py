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

@webapp.route('/show_tasks')
def show_tasks():
    db_connection = connect_to_database()
    query = 'SELECT t.task_id, t.name, t.status, t.due_date, t.pomodoros, u.first_name, u.last_name FROM Tasks t LEFT JOIN Users u ON t.assigned_user = u.user_id;'
    results = execute_query(db_connection, query).fetchall()
    print(results)
    return render_template('show_tasks.html', tasks=results)

@webapp.route('/add_task', methods=['POST', 'GET'])
def add_task():
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = 'SELECT user_id, first_name, last_name FROM Users;'
        result = execute_query(db_connection, query).fetchall()
        print(result)
        return render_template('add_task.html', tags=result)

    elif request.method == 'POST':
        print('Adding a Task...')
        print(request.form)
        task_name = request.form['task_name']
        task_status = request.form['task_status']
        task_due_date = request.form['task_due_date']
        task_time_due = request.form['task_time_due']
        task_pomodoros = request.form['task_pomodoros']
        task_assigned_user = request.form['task_assigned_user']

        query = 'INSERT INTO Badges(name, status, due_date, pomodoros, assigned_user) VALUES (%s, %s, %s, %s, %s);'
        data = (task_name, task_status, task_due_date + task_time_due, task_pomodoros, task_assigned_user)
        execute_query(db_connection, query, data)
        return show_badges()
