-- Landing Page Search Query for User
SELECT first_name, last_name FROM Users
WHERE CONCAT(first_name, last_name) LIKE CONCAT('%', :userInput, '%');

-- SELECT Query for all columns, Tasks Table (Table-Specific Query)
SELECT t.task_id, t.name, t.status,	t.due_date, t.pomodoros,
       u.first_name, u.last_name
FROM Tasks t LEFT JOIN Users u ON t.assigned_user = u.user_id;

-- SELECT Query for In-Progress Tasks and associated Tags
SELECT * FROM Tasks 
JOIN Tasks_Tags t_t ON Tasks.task_id = t_t.tk_id 
JOIN Tags ON t_t.tg_id = Tags.tag_id 
WHERE assigned_user = 2 AND status = 0;

-- INSERT Query, Tasks Table (Table-Specific Query)
-- FIXME: How to use the search bar?
INSERT INTO Tasks(name, status, due_date, pomodoros, assigned_user)
VALUES (:nameInput, :statusInput, :dateInput, :pomodorosInput,
        (SELECT user_id FROM Users
         WHERE CONCAT(first_name, last_name) = :userInput));

-- UPDATE Query, Tasks Table (Table-Specific Query)
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

-- SELECT Query for all columns, Tags Table (Table-Specific Query)
SELECT * FROM Tags;

-- INSERT Query, Tags Table (Table-Specific Query)
INSERT INTO Tags(name) VALUES (:nameInput);

-- UPDATE Query, Tags Table (Table-Specific Query)
UPDATE Tags SET name = :nameInput WHERE tag_id = :selected_Tag_id;

-- DELETE Query, Tags Table (Table-Specific Query)
DELETE FROM Tags WHERE tag_id = :selected_Tag_id;

-- SELECT Query for all columns, Tasks_Tags Table (Table-Specific Query)
SELECT tasks.name AS Task, tags.name AS Tag FROM Tasks_Tags t_t
JOIN Tasks tasks ON t_t.tk_id = tasks.task_id
JOIN Tags tags ON t_t.tg_id = tags.tag_id;

-- INSERT Query, Tasks_Tags Table (Table-Specific Query)
INSERT INTO Tasks_Tags(tk_id, tg_id) VALUES (:task_id_Input, :tag_id_Input);

-- UPDATE Query, Tasks_Tags Table (Table-Specific Query)
UPDATE Tasks_Tags SET tk_id = :task_id_Input, tg_id = :tag_id_Input
WHERE tag_id = :selected_Tag_id;

-- DELETE Query, Tasks_Tags Table (Table-Specific Query)
DELETE FROM Tags WHERE tk_id = :selected_task_id AND tg_id = :selected_tag_id;

-- SELECT query for a User's earned badges
SELECT b.* FROM Badges b INNER JOIN Users_Badges u_b
	ON u_b.be_id = b.badge_id
WHERE u_b.ur_id = :selected_User_id
GROUP BY b.badge_id;

-- UPDATE query on the Task's status: mark it as complete
UPDATE Tasks SET status = 1 WHERE task_id = :completed_task_id;

-- SELECT Query, Users Table (Table-Specific Query)
SELECT * FROM Users;

-- INSERT Query, Users Table (Table-Specific Query)
INSERT INTO Users(first_name, last_name) VALUES (:first_nameInput, :last_nameInput);

-- UPDATE Query, Users Table (Table-Specific Query)
UPDATE Users SET first_name = :first_nameInput, last_name = :last_nameInput WHERE user_id = :selected_user_id;

-- DELETE Query, Users Table (Table-Specific Query)
DELETE FROM Users WHERE user_id = :selected_user_id;

-- SELECT Query, Badges Table (Table-Specific Query)
SELECT b.badge_id, b.name, t.name, b.criteria FROM Badges b LEFT JOIN Tags t ON b.tg_id = t.tag_id;

-- INSERT Query, Badges Table (Table-Specific Query)
INSERT INTO Badges(name, tg_id, criteria) VALUES (:nameInput, (SELECT tag_id FROM Tags WHERE tag_id = :userInput), :criteriaInput);

-- UPDATE Query, Badges Table (Table-Specific Query)
UPDATE Users SET first_name = :first_nameInput, last_name = :last_nameInput WHERE user_id = :selected_user_id;

-- DELETE Query, Badges Table (Table-Specific Query)
DELETE FROM Users WHERE user_id = :selected_user_id;

-- SELECT Query, Users_Badges Table (Table-Specific Query)
SELECT users.first_name AS User, badges.name AS Badge FROM Users_Badges u_b
JOIN Users users ON u_b.ur_id = users.user_id
JOIN Badges badges ON u_b.be_id = badges.badge_id;

-- INSERT Query, Users_Badges Table (Table-Specific Query)
INSERT INTO Users_Badges(ur_id, be_id) VALUES (:user_id_Input, :badge_id_Input);

-- UPDATE Query, Users_Badges Table (Table-Specific Query)
UPDATE Users_Badges SET ur_id = :user_id_Input, be_id = :badge_id_Input
WHERE badge_id = :selected_badge_id;

-- DELETE Query, Users_Badges Table (Table-Specific Query)
DELETE FROM Users_Badges WHERE ur_id = :selected_user_id AND be_id = :selected_badge_id;




