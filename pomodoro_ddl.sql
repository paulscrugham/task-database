CREATE TABLE `Users` (
    `user_id` int(11) NOT NULL AUTO_INCREMENT,
    `first_name` varchar(30) NOT NULL,
    `last_name` varchar(30) NOT NULL,
    PRIMARY KEY (`user_id`)
    ) ENGINE=InnoDB

CREATE TABLE `Badges` (
    `badge_id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(50) NOT NULL,
    `tg_id` int(11) DEFAULT NULL,
    `criteria` int(4) NOT NULL,
    -- add FK constraint for tg_id
    PRIMARY KEY (`badge_id`),
    FOREIGN KEY (`tg_id`) REFERENCES `Tags` (`tag_id`) ON DELETE SET NULL ON UPDATE CASCADE
    ) ENGINE=InnoDB

CREATE TABLE `Users_Badges` (
    `ur_id` int(11) NOT NULL,
    `be_id` int(11) NOT NULL,
    PRIMARY KEY (`ur_id`, `be_id`),
    FOREIGN KEY (`ur_id`) REFERENCES `Users` (`user_id`) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (`be_id`) REFERENCES `Badges` (`badge_id`) ON DELETE SET NULL ON UPDATE CASCADE
    ) ENGINE=InnoDB