-- Query to create the Users table
CREATE TABLE `Users` (
    `user_id` int(11) NOT NULL AUTO_INCREMENT,
    `first_name` varchar(30) NOT NULL,
    `last_name` varchar(30) NOT NULL,
    PRIMARY KEY (`user_id`)
) ENGINE=InnoDB;

-- Query to create the Tasks table
CREATE TABLE `Tasks` (
    `task_id` INT(11) AUTO_INCREMENT NOT NULL UNIQUE PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL,
    `assigned_user` INT(11) NOT NULL,
    `status` BOOL NOT NULL,
    `due_date` DATETIME NOT NULL,
    `pomodoros` INT(4) NOT NULL,
    FOREIGN KEY (`assigned_user`) REFERENCES Users (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Query to create the Tags table
CREATE TABLE `Tags` (
    `tag_id` INT(11) AUTO_INCREMENT NOT NULL UNIQUE PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- Query to create the Badges table
CREATE TABLE `Badges` (
    `badge_id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(50) NOT NULL,
    `tg_id` int(11) DEFAULT NULL,
    `criteria` int(4) NOT NULL,
    -- add FK constraint for tg_id
    PRIMARY KEY (`badge_id`),
    FOREIGN KEY (`tg_id`) REFERENCES `Tags` (`tag_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Query to create the Users_Badges table
CREATE TABLE `Users_Badges` (
    `ur_id` int(11) NOT NULL,
    `be_id` int(11) NOT NULL,
    PRIMARY KEY (`ur_id`, `be_id`),
    FOREIGN KEY (`ur_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`be_id`) REFERENCES `Badges` (`badge_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Query to create the Tasks_Tags table
CREATE TABLE `Tasks_Tags` (
    `tk_id` INT(11) NOT NULL,
    `tg_id` INT(11) NOT NULL,
    PRIMARY KEY(`tk_id`, `tg_id`),
    FOREIGN KEY (`tk_id`) REFERENCES Tasks (`task_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`tg_id`) REFERENCES Tags (`tag_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


-- Sample data

-- Users Table
INSERT INTO Users(first_name, last_name) VALUES ("Frodo", "Baggins"), ("Pomo", "Doro");

-- Tags Table
INSERT INTO Tags(name) VALUES ("High Priority"), ("Low Priority"), ("School"), ("Work"), ("Personal");

-- Badges Table
INSERT INTO Badges (name, tg_id, criteria) VALUES 
    ("Complete 10 High Priority Pomodoros", (SELECT tag_id FROM Tags WHERE name="High Priority"), 10),
    ("Complete 5 School Pomodoros", (SELECT tag_id FROM Tags WHERE name="School"), 5),
    ("Complete 20 Work Pomodoros", (SELECT tag_id FROM Tags WHERE name="School"), 20);

-- Tasks Table
INSERT INTO Tasks(name, status, due_date, pomodoros, assigned_user) VALUES 
    ("Complete homework assignment #4", 0, "2021-08-01 08:30:00", 4, (SELECT user_id FROM Users WHERE first_name="Pomo" AND last_name="Doro")),
    ("Finish project requirements document", 0, "2021-08-10 11:30:00", 10, (SELECT user_id FROM Users WHERE first_name="Pomo" AND last_name="Doro"));