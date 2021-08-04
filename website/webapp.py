from flask import Flask, render_template
from flask import request, redirect
from flask.templating import render_template_string
from db_connector.db_connector import connect_to_database, execute_query
from itertools import islice
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

    # query to select User's name and id
    query = 'SELECT * FROM Users WHERE user_id = %s;'
    data = (id,)
    user = execute_query(db_connection, query, data).fetchone()

    # query to select User's badges
    query = 'SELECT badges.name AS Badge FROM Users_Badges u_b JOIN Users users ON u_b.ur_id = users.user_id JOIN Badges badges ON u_b.be_id = badges.badge_id WHERE users.user_id=%s;'
    data = (id,)
    badges = execute_query(db_connection, query, data).fetchall()

    # query to select three in-progress tasks
    query = 'SELECT Tasks.name, Tags.name, Tasks.task_id FROM Tasks LEFT JOIN Tasks_Tags t_t ON Tasks.task_id = t_t.tk_id LEFT JOIN Tags ON t_t.tg_id = Tags.tag_id WHERE assigned_user = %s AND status = 0 ORDER BY due_date ASC;'
    data = (id,)
    results = execute_query(db_connection, query, data).fetchall()
    # print('results: ', results)
    tasks_data = {}
    tasks_ids = []
    for item in results:
        if str(item[0]) not in tasks_data.keys():
            tasks_data[str(item[0])] = []
            tasks_ids.append(item[2])
        tasks_data[str(item[0])].append(str(item[1]))
    tasks_data = {key: tasks_data[key] for key in list(tasks_data)[:3]}  # only take the fist 3 tasks
    # print('tasks_data: ', tasks_data)
    # print('tasks_ids: ', tasks_ids)

    #query to select all in-progress tasks for User
    query = 'SELECT task_id, name, due_date FROM Tasks WHERE assigned_user=%s ORDER BY due_date;'
    data = (id,)
    open_tasks = execute_query(db_connection, query, data).fetchall()

    return render_template('user_main_page.html', user=user, badges=badges, tasks_data=tasks_data, open_tasks=open_tasks, tasks_ids=tasks_ids)


@webapp.route('/add_task_tag_user/<int:task_id>', methods=['POST', 'GET'])
def add_task_tag_user(task_id):
    db_connection = connect_to_database()
    # query DB for tags associated with task
    query = 'SELECT tg_id FROM Tasks_Tags WHERE tk_id=%s;'
    data = (task_id,)
    queried_tags = execute_query(db_connection, query, data).fetchall()
    current_tags = []
    
    for tup in queried_tags:
        current_tags.append(tup[0])
    
    if request.method == 'GET':
        # query DB for all tag names and IDs
        query = 'SELECT tag_id, name FROM Tags;'
        all_tags = execute_query(db_connection, query).fetchall()

        query = 'SELECT task_id, name FROM Tasks WHERE task_id=%s;'
        data = (task_id,)
        task = execute_query(db_connection, query, data).fetchone()

        return render_template('add_task_tag_user.html', current_tags=current_tags, all_tags=all_tags, task=task)
    if request.method == 'POST':
        print('Updating Tags for a Task...')
        print(request.form)

        new_tags = []
        for tag in request.form:
            new_tags.append(int(request.form.get(tag)))

        delete_list = set(current_tags) - set(new_tags)
        add_list = set(new_tags) - set(current_tags)

        # query to delete removed tags
        query = 'DELETE FROM Tasks_Tags WHERE tk_id=%s and tg_id=%s;'
        for tag in delete_list:
            data = (task_id, tag)
            execute_query(db_connection, query, data)

        # query to add new tags
        query = 'INSERT INTO Tasks_Tags(tk_id, tg_id) VALUES (%s, %s);'
        for tag in add_list:
            data = (task_id, tag)
            execute_query(db_connection, query, data)

        # get user id for user main page redirect
        query = 'SELECT assigned_user FROM Tasks WHERE task_id=%s;'
        data = (task_id,)
        user_id = execute_query(db_connection, query, data).fetchone()

        return redirect('/user_main_page/' + str(user_id[0]))
        




# app routes for Timer Page

@webapp.route('/timer', methods=['POST'])
def timer():
    selected_task = request.form['selected_task']
    db_connection = connect_to_database()
    query = 'SELECT * FROM Tasks WHERE task_id=%s;'
    data = (selected_task,)
    task = execute_query(db_connection, query, data).fetchone()
    print(task)
    return render_template('timer.html', task=task)

@webapp.route('/complete_task/<int:task_id>/<int:user_id>')
def complete_task(task_id, user_id):
    db_connection = connect_to_database()
    query = 'UPDATE Tasks SET status=1 WHERE task_id=%s;'
    data = (task_id,)
    task = execute_query(db_connection, query, data)
    print(task)
    return redirect('/user_main_page/' + str(user_id))


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
        # case if no tag is selectd
        if badge_tag == "None":
            badge_tag = None
        
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
    # get user info
    query = 'SELECT user_id, first_name, last_name FROM Users;'
    users = execute_query(db_connection, query).fetchall()
    print(users)
    return render_template('show_users.html', users=users)

@webapp.route('/add_user', methods=['POST', 'GET'])
def add_user():
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = 'SELECT badge_id, name FROM Badges;'
        badges = execute_query(db_connection, query).fetchall()
        return render_template('add_user.html', form_action='/add_user', all_badges=badges)
    if request.method == 'POST':
        print('Adding a User...')
        user_first_name = request.form['user_first_name']
        user_last_name = request.form['user_last_name']
        user_selected_badges = request.form.getlist('badges')
        
        # insert new user into table
        query = 'INSERT INTO Users(first_name, last_name) VALUES (%s, %s);'
        data = (user_first_name, user_last_name)
        results = execute_query(db_connection, query, data)

        # get id of new user
        new_user_id = results.lastrowid
        
        # assign badges to user if any are checked
        for badge in user_selected_badges:
            query = 'INSERT INTO Users_Badges(ur_id, be_id) VALUES (%s, %s);'
            data = (new_user_id, int(badge))
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
    
    # get this user's badges
    query = 'SELECT be_id FROM Users_Badges WHERE ur_id=%s;'
    data = (id,)
    queried_badges = execute_query(db_connection, query, data).fetchall()
    current_badges = []
    for tup in queried_badges:
        current_badges.append(tup[0])
    
    if request.method == 'GET':
        query = 'SELECT first_name, last_name FROM Users WHERE user_id = %s;'
        data = (id,)
        user = execute_query(db_connection, query, data).fetchall()

        # get all badges
        query = 'SELECT badge_id, name FROM Badges;'
        all_badges = execute_query(db_connection, query).fetchall()

        return render_template('add_user.html', user=user, all_badges=all_badges, current_badges=current_badges, form_action='/update_user/' + str(id))
    
    elif request.method == 'POST':
        print('Updating User', id, '...')
        # update user info
        user_first_name = request.form['user_first_name']
        user_last_name = request.form['user_last_name']
        query = 'UPDATE Users SET first_name = %s, last_name = %s WHERE user_id = %s'
        data = (user_first_name, user_last_name, id)
        execute_query(db_connection, query, data)

        form_badges = request.form.getlist('badges')
        new_badges = []
        for badge in form_badges:
            new_badges.append(int(badge))

        delete_list = set(current_badges) - set(new_badges)
        add_list = set(new_badges) - set(current_badges)

        # query to delete removed badges
        query = 'DELETE FROM Users_Badges WHERE ur_id=%s and be_id=%s;'
        for badge in delete_list:
            data = (id, badge)
            execute_query(db_connection, query, data)

        # query to add new badges
        query = 'INSERT INTO Users_Badges(ur_id, be_id) VALUES (%s, %s);'
        for badge in add_list:
            data = (id, badge)
            execute_query(db_connection, query, data)

        return redirect('/show_users')

# app routes for Users_Badges page

@webapp.route('/show_users_badges')
def show_users_badges():
    db_connection = connect_to_database()
    query = 'SELECT users.first_name, badges.name, users.user_id, badges.badge_id FROM Users_Badges u_b JOIN Users users ON u_b.ur_id = users.user_id JOIN Badges badges ON u_b.be_id = badges.badge_id ORDER BY users.first_name;'
    users_badges = execute_query(db_connection, query).fetchall()

    return render_template('show_users_badges.html', users_badges=users_badges)

@webapp.route('/delete_user_badge/<int:user_id>/<int:badge_id>')
def delete_user_badge(user_id, badge_id):
    db_connection = connect_to_database()
    query = 'DELETE FROM Users_Badges WHERE ur_id = %s AND be_id = %s;'
    data = (user_id, badge_id)
    execute_query(db_connection, query, data)
    return redirect('/show_users_badges')

@webapp.route('/add_user_badge', methods=['POST', 'GET'])
def add_user_badge():
    db_connection = connect_to_database()
    if request.method == 'GET':
        user = None
        query = 'SELECT badge_id, name FROM Badges;'
        badges = execute_query(db_connection, query).fetchall()
        query = 'SELECT user_id, first_name, last_name FROM Users'
        all_users = execute_query(db_connection, query).fetchall()
        return render_template('add_user_badge.html', form_action="/add_user_badge", badges=badges, all_users=all_users, user=user)
    elif request.method == 'POST':
        print('Assigning a Badge...')
        badge_id = request.form['badge_id']
        user_id = request.form['selected_user']
        query = 'INSERT INTO Users_Badges(ur_id, be_id) VALUES (%s, %s);'
        data = (user_id, badge_id)
        execute_query(db_connection, query, data)
        return redirect('/show_users_badges')

@webapp.route('/add_user_badge/<int:user_id>', methods=['POST', 'GET'])
def add_user_specific_badge(user_id):
    db_connection = connect_to_database()
    if request.method == 'GET':
        all_users = None
        query = 'SELECT badge_id, name FROM Badges;'
        badges = execute_query(db_connection, query).fetchall()
        query = 'SELECT user_id, first_name, last_name FROM Users WHERE user_id=%s;'
        data = (user_id,)
        user = execute_query(db_connection, query, data).fetchone()
        return render_template('add_user_badge.html', form_action="/add_user_badge/" + str(user_id), badges=badges, all_users=all_users, user=user)
    elif request.method == 'POST':
        print('Assigning a Badge...')
        badge_id = request.form['badge_id']
        user_id = request.form['selected_user']
        query = 'INSERT INTO Users_Badges(ur_id, be_id) VALUES (%s, %s);'
        data = (user_id, badge_id)
        execute_query(db_connection, query, data)
        return redirect('/user_main_page/' + str(user_id))


# app routes for Tasks page

@webapp.route('/show_tasks')
def show_tasks():
    db_connection = connect_to_database()
    query = 'SELECT t.task_id, t.name, t.status, t.due_date, t.pomodoros, u.first_name, u.last_name FROM Tasks t LEFT JOIN Users u ON t.assigned_user = u.user_id;'
    results = execute_query(db_connection, query).fetchall()
    print(results)
    return render_template('show_tasks.html', tasks=results)

@webapp.route('/show_tasks/<int:user_id>')
def show_user_tasks(user_id):
    db_connection = connect_to_database()
    query = 'SELECT t.task_id, t.name, t.status, t.due_date, t.pomodoros, u.first_name, u.last_name FROM Tasks t LEFT JOIN Users u ON t.assigned_user = u.user_id WHERE u.user_id=%s;'
    data = (user_id,)
    results = execute_query(db_connection, query, data).fetchall()
    print(results)
    return render_template('show_tasks.html', tasks=results)

@webapp.route('/add_task', methods=['POST', 'GET'])
def add_task():
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = 'SELECT * FROM Tags;'
        results = execute_query(db_connection, query).fetchall()
        return render_template('add_task.html', form_action='/add_task', tags=results)

    elif request.method == 'POST':
        print('Adding a Task...')
        task_name = request.form['task_name']
        task_status = str(request.form['task_status'])
        task_due_date = request.form['task_due_date']
        task_time_due = str(request.form['task_time_due'])
        task_pomodoros = request.form['task_pomodoros']
        task_assigned_user = request.form['task_assigned_user']
        task_selected_tags = request.form.getlist('tags')

        query = 'INSERT INTO Tasks(name, status, due_date, pomodoros, assigned_user) VALUES (%s, %s, %s, %s, %s);'
        task_due = str(task_due_date) + ' ' + str(task_time_due)
        print('task_due: ', task_due)
        data = (task_name, task_status, task_due, task_pomodoros, task_assigned_user)
        execute_query(db_connection, query, data)

        query = 'SELECT task_id FROM Tasks WHERE name = %s AND status = %s AND due_date = %s AND pomodoros = %s AND assigned_user = %s;'
        data = (task_name, task_status, task_due, task_pomodoros, task_assigned_user)
        results = execute_query(db_connection, query, data).fetchall()
        task_id = results[0][0]
        print('selected-tags: ', task_selected_tags)
        for tag in task_selected_tags:
            query = 'INSERT INTO Tasks_Tags(tk_id, tg_id) VALUES (%s, %s);'
            data = (task_id, int(tag))
            execute_query(db_connection, query, data)
        return redirect('/show_tasks')

# creates user-specific task
@webapp.route('/add_task/<int:user_id>', methods=['POST', 'GET'])
def add_user_specific_task(user_id):
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = 'SELECT * FROM Tags;'
        results = execute_query(db_connection, query).fetchall()
        return render_template('add_task.html', form_action='/add_task/'+str(user_id), tags=results, user_id=user_id)

    elif request.method == 'POST':
        print('Adding a Task...')
        task_name = request.form['task_name']
        task_status = str(request.form['task_status'])
        task_due_date = request.form['task_due_date']
        task_time_due = str(request.form['task_time_due'])
        task_pomodoros = request.form['task_pomodoros']
        task_assigned_user = user_id
        task_selected_tags = request.form.getlist('tags')

        query = 'INSERT INTO Tasks(name, status, due_date, pomodoros, assigned_user) VALUES (%s, %s, %s, %s, %s);'
        task_due = str(task_due_date) + ' ' + str(task_time_due)
        print('task_due: ', task_due)
        data = (task_name, task_status, task_due, task_pomodoros, task_assigned_user)
        execute_query(db_connection, query, data)

        query = 'SELECT task_id FROM Tasks WHERE name = %s AND status = %s AND due_date = %s AND pomodoros = %s AND assigned_user = %s;'
        data = (task_name, task_status, task_due, task_pomodoros, task_assigned_user)
        results = execute_query(db_connection, query, data).fetchall()
        task_id = results[0][0]
        print('selected-tags: ', task_selected_tags)
        for tag in task_selected_tags:
            query = 'INSERT INTO Tasks_Tags(tk_id, tg_id) VALUES (%s, %s);'
            data = (task_id, int(tag))
            execute_query(db_connection, query, data)
        return redirect('/user_main_page/'+str(user_id))

@webapp.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    db_connection = connect_to_database()
    query = 'DELETE FROM Tasks WHERE task_id = %s;'
    data = (task_id,)
    result = execute_query(db_connection, query, data)
    return redirect('/show_tasks')


@webapp.route('/update_task/<int:task_id>', methods=['POST', 'GET'])
def update_task(task_id):
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = "SELECT task_id, name, status, CAST(due_date AS DATE), pomodoros, assigned_user FROM Tasks WHERE task_id = %s;"
        data = (task_id,)
        results = execute_query(db_connection, query, data).fetchall()
        query = 'SELECT * FROM Tags;'
        tags = execute_query(db_connection, query).fetchall()
        return render_template('add_task.html', task_data=results, form_action='/update_task/' + str(task_id), tags=tags)

    elif request.method == 'POST':
        print('Updating Task', task_id, '...')
        task_name = request.form['task_name']
        task_status = str(request.form['task_status'])
        task_due_date = request.form['task_due_date']
        task_time_due = str(request.form['task_time_due'])
        task_pomodoros = request.form['task_pomodoros']
        task_assigned_user = request.form['task_assigned_user']
        task_selected_tags = request.form.getlist('tags')

        query = 'UPDATE Tasks SET name = %s, status = %s, due_date = %s, pomodoros = %s, assigned_user = %s WHERE task_id = %s;'
        task_due = str(task_due_date) + ' ' + str(task_time_due)
        print('task_due: ', task_due)
        data = (task_name, task_status, task_due, task_pomodoros, task_assigned_user, task_id)
        execute_query(db_connection, query, data)

        # remove all existing tags from this task
        query = 'DELETE FROM Tasks_Tags WHERE tk_id = %s;'
        data = (task_id,)
        execute_query(db_connection, query, data)

        # now add the selected tags to Tasks_Tags
        print('selected-tags: ', task_selected_tags)
        for tag in task_selected_tags:
            query = 'INSERT INTO Tasks_Tags(tk_id, tg_id) VALUES (%s, %s);'
            data = (task_id, int(tag))
            execute_query(db_connection, query, data)
        return redirect('/show_tasks')

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
    return redirect('/show_tags')

@webapp.route('/add_tag', methods=['POST', 'GET'])
def add_tag():
    db_connection = connect_to_database()
    if request.method == 'GET':
        return render_template('add_tag.html', form_action='/add_tag')

    elif request.method == 'POST':
        print('Adding a Tag...')
        tag_name = request.form['tag_name']
        query = 'INSERT INTO Tags(name) VALUES (%s);'
        data = (tag_name,)
        execute_query(db_connection, query, data)
        return redirect('/show_tags')

@webapp.route('/update_tag/<int:tag_id>', methods=['POST', 'GET'])
def update_tag(tag_id):
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = "SELECT * FROM Tags WHERE tag_id = %s;"
        data = (tag_id,)
        results = execute_query(db_connection, query, data).fetchall()
        return render_template('add_tag.html', tag_data=results, form_action='/update_tag/' + str(tag_id))

    elif request.method == 'POST':
        print('Updating Tag', tag_id, '...')
        tag_name = request.form['tag_name']
        query = 'UPDATE Tags SET name = %s WHERE tag_id = %s;'
        data = (tag_name, tag_id)
        execute_query(db_connection, query, data)
        return redirect('/show_tags')


# app routes for Tasks_Tags page

@webapp.route('/show_tasks_tags')
def show_tasks_tags():
    db_connection = connect_to_database()
    query = 'SELECT tk_id AS task_id, tg_id AS tag_id, tasks.name AS Task, tags.name AS Tag FROM Tasks_Tags t_t JOIN Tasks tasks ON t_t.tk_id = tasks.task_id JOIN Tags tags ON t_t.tg_id = tags.tag_id;'
    results = execute_query(db_connection, query).fetchall()
    return render_template('show_tasks_tags.html', tasks_tags_data=results)

@webapp.route('/delete_task_tag/<int:task_id>/<int:tag_id>')
def delete_task_tag(task_id, tag_id):
    db_connection = connect_to_database()
    query = 'DELETE FROM Tasks_Tags WHERE tk_id = %s AND tg_id = %s;'
    data = (task_id, tag_id)
    execute_query(db_connection, query, data)
    return redirect('/show_tasks_tags')

@webapp.route('/add_task_tag', methods=['POST', 'GET'])
def add_task_tag():
    db_connection = connect_to_database()
    if request.method == 'GET':
        return render_template('add_task_tag.html', form_action='/add_task_tag')

    elif request.method == 'POST':
        print('Assigning a Task to a Tag...')
        task_id = request.form['task_id']
        tag_id = request.form['tag_id']
        query = 'INSERT INTO Tasks_Tags(tk_id, tg_id) VALUES (%s, %s);'
        data = (task_id, tag_id)
        execute_query(db_connection, query, data)
        return redirect('/show_tasks_tags')
