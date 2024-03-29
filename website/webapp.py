from flask import Flask, render_template
from flask import request, redirect
from flask.templating import render_template_string
from db_connector.db_connector import connect_to_database, execute_query
from itertools import islice
import MySQLdb as mariadb

webapp = Flask(__name__)


def datetime_to_string(datetime):
    # extract string from datetime object
    return datetime.strftime("%B %-d %-I:%M%p")


# test routes
@webapp.route('/hello')
def hello():
    return "Hello World!"

@webapp.route('/dbtest')
def index():
    db_connection = connect_to_database()
    if request.method == 'GET':
        query = 'SELECT task_id, name, assigned_user, status, due_date, pomodoros FROM Tasks;'
        values = execute_query(db_connection, query).fetchall()
        print(values)
    return render_template('db_test.html', results=values)


# app routes for Landing page

@webapp.route('/')
def home():
    # Renders the landing page for the website.
    return render_template('home.html')


# app routes for Errors and Exceptions

@webapp.errorhandler(mariadb.Error)
def error_handler():
   return render_template('error.html')


@webapp.errorhandler(mariadb.Warning)
def warning_handler():
   return render_template('error.html')


# General error handler for all exceptions e.g. 500
@webapp.errorhandler(Exception)
def general_handler(error):
   return render_template('error.html')

# app routes for user searches

@webapp.route('/user_search', methods=['POST'])
def user_search():
    # Searches for a user in the data base with the specified search term
    # and renders a list of results.
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
    # Queries the database for user-specific data based on the 
    # specified user id and renders their dashboard.
    db_connection = connect_to_database()

    # query to select User's name and id
    query = 'SELECT user_id, first_name, last_name FROM Users WHERE user_id = %s;'
    data = (id,)
    user = execute_query(db_connection, query, data).fetchone()

    # query to select User's badges
    query = 'SELECT badges.name AS Badge FROM Users_Badges u_b JOIN Users users ON u_b.ur_id = users.user_id JOIN Badges badges ON u_b.be_id = badges.badge_id WHERE users.user_id=%s;'
    data = (id,)
    badges = execute_query(db_connection, query, data).fetchall()

    # query to select three in-progress tasks
    query = 'SELECT Tasks.name, Tags.name, Tasks.task_id, Tasks.due_date FROM Tasks LEFT JOIN Tasks_Tags t_t ON Tasks.task_id = t_t.tk_id LEFT JOIN Tags ON t_t.tg_id = Tags.tag_id WHERE assigned_user = %s AND status = 0 ORDER BY due_date ASC;'
    data = (id,)
    results = execute_query(db_connection, query, data).fetchall()
    # print('results: ', results)
    tasks_data = {}
    tasks_ids = []
    due_dates = []
    for item in results:
        if str(item[0]) not in tasks_data.keys():
            tasks_data[str(item[0])] = []
            tasks_ids.append(item[2])
            due_dates.append(datetime_to_string(item[3]))
        tasks_data[str(item[0])].append(str(item[1]))
    tasks_data = {key: tasks_data[key] for key in list(tasks_data)}  # only take the fist 3 tasks
    print('tasks_data: ', tasks_data)
    print('tasks_ids: ', tasks_ids)
    print('due_dates: ', due_dates)

    #query to select all in-progress tasks for User
    query = 'SELECT task_id, name, due_date FROM Tasks WHERE assigned_user=%s ORDER BY due_date;'
    data = (id,)
    open_tasks = execute_query(db_connection, query, data).fetchall()

    return render_template('user_main_page.html', user=user, badges=badges, tasks_data=tasks_data, open_tasks=open_tasks, tasks_ids=tasks_ids, due_dates=due_dates)


@webapp.route('/add_task_tag_user/<int:task_id>', methods=['POST', 'GET'])
def add_task_tag_user(task_id):
    # Allows the user to directly assign Tags to a Task from their dashboard.
    db_connection = connect_to_database()
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

@webapp.route('/timer/<int:task_id>', methods=['POST', 'GET'])
def timer(task_id):
    # Gets information for the specified Task and renders the Pomodoro Timer page.
    db_connection = connect_to_database()
    query = 'SELECT task_id, name, assigned_user, status, due_date, pomodoros FROM Tasks WHERE task_id=%s;'
    data = (task_id,)
    task = execute_query(db_connection, query, data).fetchone()
    print(task)
    return render_template('timer.html', task=task)

@webapp.route('/complete_task/<int:task_id>/<int:user_id>')
def complete_task(task_id, user_id):
    # Marks the specified task complete and redirects to the user's dashboard.
    # Used to update a Task from the Timer page.
    db_connection = connect_to_database()
    query = 'UPDATE Tasks SET status=1 WHERE task_id=%s;'
    data = (task_id,)
    task = execute_query(db_connection, query, data)
    print(task)
    return redirect('/user_main_page/' + str(user_id))


# app routes for Badges page

@webapp.route('/show_badges')
def show_badges():
    # Queries the database for all existing Badges and renders a page displaying them.
    db_connection = connect_to_database()
    query = 'SELECT b.badge_id, b.name, t.name, b.criteria FROM Badges b LEFT JOIN Tags t ON b.tg_id = t.tag_id;'
    results = execute_query(db_connection, query).fetchall()
    print(results)
    return render_template('show_badges.html', badges=results)

@webapp.route('/add_badge', methods=['POST', 'GET'])
def add_badge():
    # Queries the database to INSERT a new Badge and renders the show Badges page.
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
    # Queries the database to delete the specified badge by its id.
    db_connection = connect_to_database()
    query = 'DELETE FROM Badges WHERE badge_id = %s;'
    data = (id,)
    result = execute_query(db_connection, query, data)
    return redirect('/show_badges')

@webapp.route('/update_badge/<int:id>', methods=['POST', 'GET'])
def update_badge(id):
    # Queries the database for the specified Badge entry, then updates the entry
    # with any user provided changes.
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
            badge_tag = None  # set badge_tag to None to create NULL entry in database
        else:
            badge_tag = request.form['badge_tag']
        
        query = 'UPDATE Badges SET name = %s, tg_id = %s, criteria = %s WHERE badge_id = %s;'
        data = (badge_name, badge_tag, badge_criteria, id)
        execute_query(db_connection, query, data)
        return redirect('/show_badges')


# app routes for Users page

@webapp.route('/show_users')
def show_users():
    # Queries the database for all existing Users and renders a page displaying them.
    db_connection = connect_to_database()
    # get all user rows
    query = 'SELECT user_id, first_name, last_name FROM Users;'
    users = execute_query(db_connection, query).fetchall()

    # get all assigned badges
    query = 'SELECT ub.ur_id, b.name FROM Users_Badges ub JOIN Badges b ON b.badge_id = ub.be_id ORDER BY ur_id;'
    all_assigned_badges = list(execute_query(db_connection, query).fetchall())
    
    # create new data structure with user data and their badges
    users_badges = []
    for u in users:
        row = [u[0], u[1], u[2], []]
        while all_assigned_badges and all_assigned_badges[0][0] == u[0]:
            row[3].append(all_assigned_badges.pop(0)[1])
        users_badges.append(row)

    print(users_badges)
    return render_template('show_users.html', users=users_badges)


@webapp.route('/add_user', methods=['POST', 'GET'])
def add_user():
    # Queries the database to INSERT a new User entry from user provided data.
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
        
        query = 'INSERT INTO Users(first_name, last_name) VALUES (%s, %s);'
        data = (user_first_name, user_last_name)
        results = execute_query(db_connection, query, data)
        
        new_user_id = results.lastrowid # get id of new user
        
        for badge in user_selected_badges:  # assign badges to user if any are checked
            query = 'INSERT INTO Users_Badges(ur_id, be_id) VALUES (%s, %s);'
            data = (new_user_id, int(badge))
            execute_query(db_connection, query, data)
        return redirect('/show_users')

@webapp.route('/delete_user/<int:id>')
def delete_user(id):
    # Queries the database to DELETE a user with the specified user id.
    db_connection = connect_to_database()
    query = 'DELETE FROM Users WHERE user_id = %s;'
    data = (id,)
    execute_query(db_connection, query, data)
    return redirect('/show_users')

@webapp.route('/update_user/<int:id>', methods=['POST', 'GET'])
def update_user(id):
    # On a GET request, queries the database to get existing data for the specified User.
    # On a POST, queries the database to UPDATE the User with any provided changes.
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
    # Queries the database for all Badges assigned to Users.
    db_connection = connect_to_database()
    query = 'SELECT users.first_name, badges.name, users.user_id, badges.badge_id FROM Users_Badges u_b JOIN Users users ON u_b.ur_id = users.user_id JOIN Badges badges ON u_b.be_id = badges.badge_id ORDER BY users.first_name;'
    users_badges = execute_query(db_connection, query).fetchall()
    return render_template('show_users_badges.html', users_badges=users_badges)

@webapp.route('/delete_user_badge/<int:user_id>/<int:badge_id>')
def delete_user_badge(user_id, badge_id):
    # Queries the database to DELETE a User-Badge assignment with the provided user id.
    db_connection = connect_to_database()
    query = 'DELETE FROM Users_Badges WHERE ur_id = %s AND be_id = %s;'
    data = (user_id, badge_id)
    execute_query(db_connection, query, data)
    return redirect('/show_users_badges')

@webapp.route('/add_user_badge', methods=['POST', 'GET'])
def add_user_badge():
    # Queries the database to INSERT a new User-Badge assignment with the provided user id and badge id.
    db_connection = connect_to_database()
    if request.method == 'GET':
        user = None
        query = 'SELECT badge_id, name FROM Badges;'
        all_badges = execute_query(db_connection, query).fetchall()
        query = 'SELECT user_id, first_name, last_name FROM Users'
        all_users = execute_query(db_connection, query).fetchall()
        return render_template('add_user_badge.html', form_action="/add_user_badge", all_badges=all_badges, all_users=all_users, user=user)
    elif request.method == 'POST':
        print('Assigning a Badge...')
        badge_id = request.form['selected_badge']
        user_id = request.form['selected_user']
        query = 'INSERT INTO Users_Badges(ur_id, be_id) VALUES (%s, %s);'
        data = (user_id, badge_id)
        execute_query(db_connection, query, data)
        return redirect('/show_users_badges')

        
@webapp.route('/add_user_badge/<int:user_id>', methods=['POST', 'GET'])
def add_user_specific_badge(user_id):
    # Queries the database to INSERT a new User-Badge assignment with the specified badge id.
    # Used on the user main page to directly assign a badge.
    db_connection = connect_to_database()
    if request.method == 'GET':
        all_users = None
        query = 'SELECT badge_id, name FROM Badges;'
        all_badges = execute_query(db_connection, query).fetchall()
        query = 'SELECT user_id, first_name, last_name FROM Users WHERE user_id=%s;'
        data = (user_id,)
        user = execute_query(db_connection, query, data).fetchone()
        return render_template('add_user_badge.html', form_action="/add_user_badge/" + str(user_id), all_badges=all_badges, all_users=all_users, user=user)
    elif request.method == 'POST':
        print('Assigning a Badge...')
        badge_id = request.form['selected_badge']
        query = 'INSERT INTO Users_Badges(ur_id, be_id) VALUES (%s, %s);'
        data = (user_id, badge_id)
        execute_query(db_connection, query, data)
        return redirect('/user_main_page/' + str(user_id))


# app routes for Tasks page

@webapp.route('/show_tasks')
def show_tasks():
    # Shows all the Tasks in the Tasks table
    db_connection = connect_to_database()
    query = 'SELECT t.task_id, t.name, t.status, t.due_date, t.pomodoros, u.first_name, u.last_name FROM Tasks t LEFT JOIN Users u ON t.assigned_user = u.user_id;'
    results = execute_query(db_connection, query).fetchall()
    print(results)

    # get all assigned tags
    query = 'SELECT tt.tk_id, tg.name FROM Tasks_Tags tt JOIN Tags tg ON tg.tag_id = tt.tg_id ORDER BY tk_id;'
    all_assigned_tags = list(execute_query(db_connection, query).fetchall())
    print(all_assigned_tags)
    
    #create new data structure with user data and their badges
    tasks_tags = []
    for t in results:
        row = [t[0], t[1], t[2], datetime_to_string(t[3]), t[4], t[5], t[6], []]
        while all_assigned_tags and all_assigned_tags[0][0] == t[0]:
            row[7].append(all_assigned_tags.pop(0)[1])
        tasks_tags.append(row)

    return render_template('show_tasks.html', tasks=tasks_tags)

@webapp.route('/show_tasks/<int:user_id>')
def show_user_tasks(user_id):
    # Shows all Tasks belonging to User with User ID = user_id
    db_connection = connect_to_database()
    query = 'SELECT t.task_id, t.name, t.status, t.due_date, t.pomodoros, u.first_name, u.last_name FROM Tasks t LEFT JOIN Users u ON t.assigned_user = u.user_id WHERE u.user_id=%s;'
    data = (user_id,)
    results = execute_query(db_connection, query, data).fetchall()
    print(results)
    return render_template('show_tasks.html', tasks=results)

@webapp.route('/add_task', methods=['POST', 'GET'])
def add_task():
    # Handles requests to show form to add a Task;
    # and Inserts results of that form to Tasks table
    db_connection = connect_to_database()
    if request.method == 'GET':
        # Show the add task form
        query = 'SELECT tag_id, name FROM Tags;'
        all_tags = execute_query(db_connection, query).fetchall()
        query = 'SELECT user_id, first_name, last_name FROM Users;'
        users = execute_query(db_connection, query).fetchall()
        return render_template('add_task.html', form_action='/add_task', all_tags=all_tags, users=users)

    elif request.method == 'POST':
        # Insert the Task data from the form
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
        try:
            execute_query(db_connection, query, data)
        except (mariadb.Error, mariadb.Warning):
            return render_template('error.html')

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
    # Handles requests to show form to add a Task for a specific user
    # with User ID = user_id
    db_connection = connect_to_database()
    if request.method == 'GET':
        # Show the form
        query = 'SELECT tag_id, name FROM Tags;'
        all_tags = execute_query(db_connection, query).fetchall()
        return render_template('add_task.html', form_action='/add_task/'+str(user_id), all_tags=all_tags, user_id=user_id)

    elif request.method == 'POST':
        # Insert the data from the form
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
        try:
            execute_query(db_connection, query, data)
        except (mariadb.Error, mariadb.Warning):
            return render_template('error.html')

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
    # Deletes Task with Task ID = task_id
    db_connection = connect_to_database()
    query = 'DELETE FROM Tasks WHERE task_id = %s;'
    data = (task_id,)
    result = execute_query(db_connection, query, data)
    return redirect('/show_tasks')


@webapp.route('/update_task/<int:task_id>', methods=['POST', 'GET'])
def update_task(task_id):
    # Handles requests to show form to update a Task, and updates
    # the database with that data
    db_connection = connect_to_database()
    # get this Task's Tags
    query = 'SELECT tg_id FROM Tasks_Tags WHERE tk_id=%s;'
    data = (task_id,)
    queried_tags = execute_query(db_connection, query, data).fetchall()
    current_tags = []
    for tup in queried_tags:
        current_tags.append(tup[0])
    
    if request.method == 'GET':
        query = "SELECT task_id, name, status, due_date, pomodoros, assigned_user FROM Tasks WHERE task_id = %s;"
        data = (task_id,)
        results = execute_query(db_connection, query, data).fetchall()
        due_date = {'date': results[0][3].strftime("%Y-%m-%d"), 'time': results[0][3].strftime("%H:%M:%S")}
        query = 'SELECT tag_id, name FROM Tags;'
        all_tags = execute_query(db_connection, query).fetchall()
        query = 'SELECT user_id, first_name, last_name FROM Users;'
        users = execute_query(db_connection, query).fetchall()
        return render_template('add_task.html', task_data=results, form_action='/update_task/' + str(task_id), 
                                users=users, all_tags=all_tags, current_tags=current_tags, due_date=due_date
                                )

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
        try:
            execute_query(db_connection, query, data)
        except (mariadb.Error, mariadb.Warning):
            return render_template('error.html')
        
        new_tags = []
        for tag in task_selected_tags:
            new_tags.append(int(tag))

        # get lists of only the tags that were added/removed
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

        return redirect('/show_tasks')

# app routes for Tags page

@webapp.route('/show_tags')
def show_tags():
    # Shows all Tags in the Tags table
    db_connection = connect_to_database()
    query = 'SELECT tag_id, name FROM Tags;'
    results = execute_query(db_connection, query).fetchall()
    return render_template('show_tags.html', tags=results)

@webapp.route('/delete_tag/<int:tag_id>')
def delete_tag(tag_id):
    # Deletes Tag with Tag ID = tag_id
    db_connection = connect_to_database()
    query = 'DELETE FROM Tags WHERE tag_id = %s;'
    data = (tag_id,)
    result = execute_query(db_connection, query, data)
    return redirect('/show_tags')

@webapp.route('/add_tag', methods=['POST', 'GET'])
def add_tag():
    # Handles requests to show form to create a Tag and
    # inserts the data into the Tags table
    db_connection = connect_to_database()
    if request.method == 'GET':
        return render_template('add_tag.html', form_action='/add_tag')

    elif request.method == 'POST':
        # Inserts the new Tag's info to the Tags table
        print('Adding a Tag...')
        tag_name = request.form['tag_name']
        query = 'INSERT INTO Tags(name) VALUES (%s);'
        data = (tag_name,)
        try:
            execute_query(db_connection, query, data)
        except (mariadb.Error, mariadb.Warning):
            return render_template('error.html')
        return redirect('/show_tags')

@webapp.route('/update_tag/<int:tag_id>', methods=['POST', 'GET'])
def update_tag(tag_id):
    # Handles requests to update Tag with Tag ID = tag_id
    # It shows a form to update the tag and updates the Tags table
    db_connection = connect_to_database()
    if request.method == 'GET':
        # Show the form to update the Tag
        query = "SELECT tag_id, name FROM Tags WHERE tag_id = %s;"
        data = (tag_id,)
        results = execute_query(db_connection, query, data).fetchall()
        return render_template('add_tag.html', tag_data=results, form_action='/update_tag/' + str(tag_id))

    elif request.method == 'POST':
        # Performs SQL query to update the task
        print('Updating Tag', tag_id, '...')
        tag_name = request.form['tag_name']
        query = 'UPDATE Tags SET name = %s WHERE tag_id = %s;'
        data = (tag_name, tag_id)
        try:
            execute_query(db_connection, query, data)
        except (mariadb.Error, mariadb.Warning):
            return render_template('error.html')
        return redirect('/show_tags')


# app routes for Tasks_Tags page

@webapp.route('/show_tasks_tags')
def show_tasks_tags():
    # Shows all the Tasks_Tags table
    db_connection = connect_to_database()
    query = 'SELECT tk_id AS task_id, tg_id AS tag_id, tasks.name AS Task, tags.name AS Tag FROM Tasks_Tags t_t JOIN Tasks tasks ON t_t.tk_id = tasks.task_id JOIN Tags tags ON t_t.tg_id = tags.tag_id ORDER BY tk_id;'
    results = execute_query(db_connection, query).fetchall()
    return render_template('show_tasks_tags.html', tasks_tags_data=results)

@webapp.route('/delete_task_tag/<int:task_id>/<int:tag_id>')
def delete_task_tag(task_id, tag_id):
    # Deletes a Task-Tag entry
    db_connection = connect_to_database()
    query = 'DELETE FROM Tasks_Tags WHERE tk_id = %s AND tg_id = %s;'
    data = (task_id, tag_id)
    execute_query(db_connection, query, data)
    return redirect('/show_tasks_tags')

@webapp.route('/add_task_tag', methods=['POST', 'GET'])
def add_task_tag():
    # Handles request to create a Task-Tag entry
    # Shows the form to do this and inserts the Data to Database
    db_connection = connect_to_database()
    if request.method == 'GET':
        # Show the form to create Task-Tag entry
        db_connection = connect_to_database()
        query = 'SELECT task_id, name FROM Tasks;'
        tasks = execute_query(db_connection, query).fetchall()
        query = 'SELECT tag_id, name FROM Tags;'
        tags = execute_query(db_connection, query).fetchall()
        return render_template('add_task_tag.html', tasks=tasks, tags=tags, form_action='/add_task_tag')

    elif request.method == 'POST':
        # Inserts the data to Tasks_Tags
        print('Assigning a Task to a Tag...')
        task_id = request.form['selected_task']
        tag_id = request.form['selected_tag']
        query = 'INSERT INTO Tasks_Tags(tk_id, tg_id) VALUES (%s, %s);'
        data = (task_id, tag_id)
        execute_query(db_connection, query, data)
        return redirect('/show_tasks_tags')
