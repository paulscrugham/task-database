-- Landing Page Search Query for User
SELECT first_name, last_name FROM Users
WHERE CONCAT(first_name, last_name) LIKE :userInput

-- SELECT Query for all columns, Tasks Table (Table-Specific Query)
SELECT * FROM Tasks;

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
