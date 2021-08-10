-- GENERAL NOTE: all variables with a preceding ':' indicate user or app provided input for the query

-- ***LANDING PAGE QUERIES***

-- Landing Page Search Query for User
-- note: the webserver performs the task of adding "%" chars to 
--      the :userInput as variable length wildcards for SQL
SELECT first_name, last_name FROM Users
WHERE CONCAT(first_name, ' ', last_name) LIKE CONCAT('%', :userInput, '%');


-- ***USER MAIN PAGE QUERIES***

-- SELECT Query for In-Progress Tasks and associated Tags
SELECT Tasks.name, Tags.name, Tasks.task_id, Tasks.due_date FROM Tasks 
LEFT JOIN Tasks_Tags t_t ON Tasks.task_id = t_t.tk_id 
LEFT JOIN Tags ON t_t.tg_id = Tags.tag_id 
WHERE assigned_user = :userInput AND status = 0 
ORDER BY due_date ASC;

-- SELECT Query for all of a User's tasks
SELECT task_id, name, due_date FROM Tasks WHERE assigned_user = :userInput ORDER BY due_date;

-- SELECT query for a User's earned badges
SELECT badges.name AS Badge FROM Users_Badges u_b 
JOIN Users users ON u_b.ur_id = users.user_id 
JOIN Badges badges ON u_b.be_id = badges.badge_id 
WHERE users.user_id=:userInput;


-- ***TIMER PAGE QUERIES***

-- UPDATE query on the Task's status: mark it as complete
UPDATE Tasks SET status = 1 WHERE task_id = :completed_task_id;


-- ***TASK PAGE QUERIES***

-- SELECT Query for all columns, Tasks Table (Table-Specific Query)
SELECT t.task_id, t.name, t.status,	t.due_date, t.pomodoros,
       u.first_name, u.last_name
FROM Tasks t LEFT JOIN Users u ON t.assigned_user = u.user_id;

-- INSERT Query, Tasks Table (Table-Specific Query)
-- FIXME: How to use the search bar/get a user?
INSERT INTO Tasks(name, status, due_date, pomodoros, assigned_user)
VALUES (:nameInput, :statusInput, :dateInput, :pomodorosInput,
        (SELECT user_id FROM Users
         WHERE CONCAT(first_name, last_name) = :userInput));

-- UPDATE Query, Tasks Table (Table-Specific Query)
-- FIXME: How to use the search bar/get a user?
UPDATE Tasks
SET
    name = :nameInput,
    status = :statusInput,
    due_date = :dateInput,
    pomodoros = :pomodorosInput,
    assigned_user = (SELECT user_id FROM Users
                    WHERE CONCAT(first_name, last_name) = :userInput)
WHERE task_id = :selected_Task_id;

-- DELETE Query, Tasks Table (Table-Specific Query)
DELETE FROM Tasks WHERE task_id = :selected_Task_id;


-- ***TAGS PAGE QUERIES***

-- SELECT Query for all columns, Tags Table (Table-Specific Query)
SELECT tag_id, name FROM Tags;

-- INSERT Query, Tags Table (Table-Specific Query)
INSERT INTO Tags(name) VALUES (:nameInput);

-- UPDATE Query, Tags Table (Table-Specific Query)
UPDATE Tags SET name = :nameInput WHERE tag_id = :selected_Tag_id;

-- DELETE Query, Tags Table (Table-Specific Query)
DELETE FROM Tags WHERE tag_id = :selected_Tag_id;


-- ***TASKS_TAGS PAGE QUERIES***

-- SELECT Query for all columns, Tasks_Tags Table (Table-Specific Query)
SELECT tasks.name AS Task, tags.name AS Tag FROM Tasks_Tags t_t
JOIN Tasks tasks ON t_t.tk_id = tasks.task_id
JOIN Tags tags ON t_t.tg_id = tags.tag_id;

-- INSERT Query, Tasks_Tags Table (Table-Specific Query)
INSERT INTO Tasks_Tags(tk_id, tg_id) VALUES (:task_id_Input, :tag_id_Input);

-- DELETE Query, Tasks_Tags Table (Table-Specific Query)
DELETE FROM Tags WHERE tk_id = :selected_task_id AND tg_id = :selected_tag_id;


-- ***USERS PAGE QUERIES***

-- SELECT Query, Users Table (Table-Specific Query)
SELECT user_id, first_name, last_name FROM Users;

-- INSERT Query, Users Table (Table-Specific Query)
INSERT INTO Users(first_name, last_name) VALUES (:first_nameInput, :last_nameInput);

-- UPDATE Query, Users Table (Table-Specific Query)
UPDATE Users SET first_name = :first_nameInput, last_name = :last_nameInput WHERE user_id = :selected_user_id;

-- DELETE Query, Users Table (Table-Specific Query)
DELETE FROM Users WHERE user_id = :selected_user_id;


-- ***BADGES PAGE QUERIES***

-- SELECT Query, Badges Table (Table-Specific Query)
SELECT b.badge_id, b.name, t.name, b.criteria FROM Badges b LEFT JOIN Tags t ON b.tg_id = t.tag_id;

-- SELECT Query to get Tag names for the Badge create/edit HTML form
SELECT tag_id, name from Tags;

-- INSERT Query, Badges Table (Table-Specific Query)
INSERT INTO Badges(name, tg_id, criteria) VALUES (:nameInput, :tagIDInput, :criteriaInput);

-- UPDATE Query, Badges Table (Table-Specific Query)
UPDATE Badges SET name = :nameInput, tag_id = :tag_idInput, criteria = :criteriaInput WHERE badge_id = :selected_badge_id;

-- DELETE Query, Badges Table (Table-Specific Query)
DELETE FROM Badges WHERE badge_id = :selected_badge_id;


-- ***USERS_BADGES PAGE QUERIES***

-- SELECT Query, Users_Badges Table (Table-Specific Query)
SELECT users.first_name, badges.name, users.user_id, badges.badge_id FROM Users_Badges u_b
JOIN Users users ON u_b.ur_id = users.user_id
JOIN Badges badges ON u_b.be_id = badges.badge_id;

-- INSERT Query, Users_Badges Table (Table-Specific Query)
INSERT INTO Users_Badges(ur_id, be_id) VALUES (:user_id_Input, :badge_id_Input);

-- DELETE Query, Users_Badges Table (Table-Specific Query)
DELETE FROM Users_Badges WHERE ur_id = :selected_user_id AND be_id = :selected_badge_id;




