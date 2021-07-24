-- Landing Page Search Query for User
SELECT first_name, last_name FROM Users
WHERE CONCAT(first_name, last_name) LIKE CONCAT('%', :userInput, '%');

-- SELECT Query for all columns, Tasks Table (Table-Specific Query)
SELECT t.task_id, t.name, t.status,	t.due_date, t.pomodoros,
       u.first_name, u.last_name
FROM Tasks t LEFT JOIN Users u ON t.assigned_user = u.user_id;

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

-- SELECT query for a User's earned badges
SELECT b.* FROM Badges b INNER JOIN Users_Badges u_b
	ON u_b.be_id = b.badge_id
WHERE u_b.ur_id = :selected_User_id
GROUP BY b.badge_id;

-- UPDATE query on the Task's status: mark it as complete
UPDATE Tasks SET status = 1 WHERE task_id = :completed_task_id;

-- SELECT Query for Users table (Table-Specific Query)
SELECT * FROM Users;

-- SELECT Query for Badges Table (Table-Specific Query)
SELECT b.badge_id, b.name, t.name, b.criteria FROM Badges b LEFT JOIN Tags t ON b.tg_id = t.tag_id;

