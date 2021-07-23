-- Query to create the Tasks table
CREATE TABLE Tasks(
    task_id INT(11) AUTO_INCREMENT NOT NULL UNIQUE PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    assigned_user INT(11) NOT NULL,
    status BOOL NOT NULL,
    due_date DATETIME NOT NULL,
    pomodoros INT(4) NOT NULL,
    FOREIGN KEY (assigned_user) REFERENCES Users (user_id)
);

-- Query to create the Tags table
CREATE TABLE Tags(
    tag_id INT(11) AUTO_INCREMENT NOT NULL UNIQUE PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Query to create the Tasks_Tags table
CREATE TABLE Tasks_Tags(
    tk_id INT(11) NOT NULL,
    tg_id INT(11) NOT NULL,
    PRIMARY KEY(tk_id, tg_id),
    FOREIGN KEY (tk_id) REFERENCES Tasks (task_id),
    FOREIGN KEY (tg_id) REFERENCES Tags (tag_id)
);
