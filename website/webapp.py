from flask import Flask, render_template
from flask import request, redirect
from flask.templating import render_template_string
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
    return render_template('db_test.html', results=values)


# app routes for Landing page

@webapp.route('/')
def home():
    return render_template('home.html')


# app routes for user searches

@webapp.route('/user_search', methods=['POST'])
def user_search():
    db_connection = connect_to_database()
    search_term = request.form['search_term']
    search_term = '%' + search_term + '%'  # concatenate %s with search term outside of query
    query = '''SELECT user_id, first_name, last_name FROM Users WHERE CONCAT(first_name, ' ', last_name) LIKE CONCAT(%s);'''
    data = (search_term,)
    results = execute_query(db_connection, query, data).fetchall()
    print(results)
    return render_template('user_search.html', results=results)


# app routes for User Main Page

@webapp.route('/user_main_page/<int:id>')
def user_main_page(id):
    db_connection = connect_to_database()
    query = 'SELECT first_name, last_name FROM Users WHERE user_id = %s;'
    data = (id,)
    user = execute_query(db_connection, query, data).fetchone()
    print(user)
    return render_template('user_main_page.html', user=user)


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
        print('result: ', result)
        return render_template('add_badge.html', tags=result, form_action='/add_badge')

    elif request.method == 'POST':
        print('Adding a Badge...')
        badge_name = request.form['badge_name']
        badge_criteria = request.form['badge_criteria']
        badge_tag = request.form['badge_tag']
        query = 'INSERT INTO Badges(name, tg_id, criteria) VALUES (%s, %s, %s);'
        data = (badge_name, badge_tag, badge_criteria)
        execute_query(db_connection, query, data)
        return redirect('/show_badges')

@webapp.route('/delete_badge/<int:id>')
def delete_badge(id):
    db_connection = connect_to_database()
    query = 'DELETE FROM Badges WHERE badge_id = %s;'
    data = (id,)
    result = execute_query(db_connection, query, data)
    return redirect('/show_badges')

@webapp.route('/update_badge/<int:id>', methods=['POST', 'GET'])
def update_badge(id):
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = 'SELECT tag_id, name from Tags;'
        tags = execute_query(db_connection, query).fetchall()
        query = 'SELECT b.badge_id, b.name, b.criteria, t.tag_id, t.name FROM Badges b LEFT JOIN Tags t ON b.tg_id = t.tag_id WHERE badge_id = %s;'
        data = (id,)
        badge = execute_query(db_connection, query, data).fetchall()
        return render_template('add_badge.html', tags=tags, badge=badge, form_action='/update_badge/' + str(id))
    
    elif request.method == 'POST':
        print('Updating Badge', id, '...')
        badge_name = request.form['badge_name']
        badge_criteria = request.form['badge_criteria']
        if request.form['badge_tag'] == "None":
            badge_tag = None
        else:
            badge_tag = request.form['badge_tag']
        query = 'UPDATE Badges SET name = %s, tg_id = %s, criteria = %s WHERE badge_id = %s;'
        data = (badge_name, badge_tag, badge_criteria, id)
        execute_query(db_connection, query, data)
        return redirect('/show_badges')


# app routes for Users page

@webapp.route('/show_users')
def show_users():
    db_connection = connect_to_database()
    query = 'SELECT * FROM Users;'
    results = execute_query(db_connection, query).fetchall()
    print(results)
    return render_template('show_users.html', users=results)

@webapp.route('/add_user', methods=['POST', 'GET'])
def add_user():
    db_connection = connect_to_database()
    if request.method == 'GET':
        return render_template('add_user.html', form_action='/add_user')
    if request.method == 'POST':
        print('Adding a User...')
        user_first_name = request.form['user_first_name']
        user_last_name = request.form['user_last_name']
        query = 'INSERT INTO Users(first_name, last_name) VALUES (%s, %s);'
        data = (user_first_name, user_last_name)
        execute_query(db_connection, query, data)
        return redirect('/show_users')

@webapp.route('/delete_user/<int:id>')
def delete_user(id):
    db_connection = connect_to_database()
    query = 'DELETE FROM Users WHERE user_id = %s;'
    data = (id,)
    execute_query(db_connection, query, data)
    return redirect('/show_users')

@webapp.route('/update_user/<int:id>', methods=['POST', 'GET'])
def update_user(id):
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = 'SELECT first_name, last_name FROM Users WHERE user_id = %s;'
        data = (id,)
        user = execute_query(db_connection, query, data).fetchall()
        return render_template('add_user.html', user=user, form_action='/update_user/' + str(id))
    
    elif request.method == 'POST':
        print('Updating User', id, '...')
        user_first_name = request.form['user_first_name']
        user_last_name = request.form['user_last_name']
        query = 'UPDATE Users SET first_name = %s, last_name = %s WHERE user_id = %s'
        data = (user_first_name, user_last_name, id)
        execute_query(db_connection, query, data)
        return redirect('/show_users')


# app routes for Tasks page

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
        return render_template('add_task.html', form_action='/add_task')

    elif request.method == 'POST':
        print('Adding a Task...')
        task_name = request.form['task_name']
        task_status = str(request.form['task_status'])
        task_due_date = request.form['task_due_date']
        task_time_due = str(request.form['task_time_due'])
        task_pomodoros = request.form['task_pomodoros']
        task_assigned_user = request.form['task_assigned_user']

        query = 'INSERT INTO Tasks(name, status, due_date, pomodoros, assigned_user) VALUES (%s, %s, %s, %s, %s);'
        task_due = str(task_due_date) + ' ' + str(task_time_due)
        print('task_due: ', task_due)
        data = (task_name, task_status, task_due, task_pomodoros, task_assigned_user)
        execute_query(db_connection, query, data)
        return redirect('show_tasks')

@webapp.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    db_connection = connect_to_database()
    query = 'DELETE FROM Tasks WHERE task_id = %s;'
    data = (task_id,)
    result = execute_query(db_connection, query, data)
    return redirect('show_tasks')


@webapp.route('/update_task/<int:task_id>', methods=['POST', 'GET'])
def update_task(task_id):
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = "SELECT task_id, name, status, CAST(due_date AS DATE), pomodoros, assigned_user FROM Tasks WHERE task_id = %s;"
        data = (task_id,)
        results = execute_query(db_connection, query, data).fetchall()
        return render_template('add_task.html', task_data=results, form_action='/update_task/' + str(task_id))

    elif request.method == 'POST':
        print('Updating Task', task_id, '...')
        task_name = request.form['task_name']
        task_status = str(request.form['task_status'])
        task_due_date = request.form['task_due_date']
        task_time_due = str(request.form['task_time_due'])
        task_pomodoros = request.form['task_pomodoros']
        task_assigned_user = request.form['task_assigned_user']

        query = 'UPDATE Tasks SET name = %s, status = %s, due_date = %s, pomodoros = %s, assigned_user = %s WHERE task_id = %s;'
        task_due = str(task_due_date) + ' ' + str(task_time_due)
        print('task_due: ', task_due)
        data = (task_name, task_status, task_due, task_pomodoros, task_assigned_user, task_id)
        execute_query(db_connection, query, data)
        return redirect('show_tasks')

# app routes for Tags page

@webapp.route('/show_tags')
def show_tags():
    db_connection = connect_to_database()
    query = 'SELECT * FROM Tags;'
    results = execute_query(db_connection, query).fetchall()
    return render_template('show_tags.html', tags=results)

@webapp.route('/delete_tag/<int:tag_id>')
def delete_tag(tag_id):
    db_connection = connect_to_database()
    query = 'DELETE FROM Tags WHERE tag_id = %s;'
    data = (tag_id,)
    result = execute_query(db_connection, query, data)
    return redirect('show_tags')