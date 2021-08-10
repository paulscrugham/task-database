-- phpMyAdmin SQL Dump
-- version 5.1.1-1.el7.remi
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Aug 10, 2021 at 01:00 AM
-- Server version: 10.4.20-MariaDB-log
-- PHP Version: 7.4.22

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cs340_scrughap`
--

-- --------------------------------------------------------

--
-- Table structure for table `Badges`
--

CREATE TABLE `Badges` (
  `badge_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `tg_id` int(11) DEFAULT NULL,
  `criteria` int(4) NOT NULL CHECK (`criteria` >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Badges`
--

INSERT INTO `Badges` (`badge_id`, `name`, `tg_id`, `criteria`) VALUES
(1, 'Complete 10 High Priority Pomodoros', 1, 10),
(2, 'Complete 5 School Pomodoros', 3, 5),
(3, 'Complete 20 Work Pomodoros', 4, 20),
(4, 'Complete 50 Pomorodos', NULL, 50);

-- --------------------------------------------------------

--
-- Table structure for table `Tags`
--

CREATE TABLE `Tags` (
  `tag_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Tags`
--

INSERT INTO `Tags` (`tag_id`, `name`) VALUES
(1, 'High Priority'),
(2, 'Low Priority'),
(5, 'Personal'),
(3, 'School'),
(4, 'Work');

-- --------------------------------------------------------

--
-- Table structure for table `Tasks`
--

CREATE TABLE `Tasks` (
  `task_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `assigned_user` int(11) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `due_date` datetime NOT NULL,
  `pomodoros` int(4) NOT NULL CHECK (`pomodoros` >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Tasks`
--

INSERT INTO `Tasks` (`task_id`, `name`, `assigned_user`, `status`, `due_date`, `pomodoros`) VALUES
(1, 'Complete homework assignment #4', 2, 0, '2021-08-01 08:30:00', 4),
(2, 'Finish project requirements document', 2, 0, '2021-08-10 11:30:00', 10),
(3, 'Write another book', 1, 0, '2021-07-20 12:30:00', 1);

-- --------------------------------------------------------

--
-- Table structure for table `Tasks_Tags`
--

CREATE TABLE `Tasks_Tags` (
  `tk_id` int(11) NOT NULL,
  `tg_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Tasks_Tags`
--

INSERT INTO `Tasks_Tags` (`tk_id`, `tg_id`) VALUES
(2, 1),
(2, 4),
(3, 2),
(3, 5);

-- --------------------------------------------------------

--
-- Table structure for table `Users`
--

CREATE TABLE `Users` (
  `user_id` int(11) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Users`
--

INSERT INTO `Users` (`user_id`, `first_name`, `last_name`) VALUES
(1, 'Frodo', 'Baggins'),
(2, 'Pomo', 'Doro'),
(3, 'Bilbo', 'Baggins'),
(4, 'Smaug', 'The Magnificent');

-- --------------------------------------------------------

--
-- Table structure for table `Users_Badges`
--

CREATE TABLE `Users_Badges` (
  `ur_id` int(11) NOT NULL,
  `be_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Users_Badges`
--

INSERT INTO `Users_Badges` (`ur_id`, `be_id`) VALUES
(1, 1),
(1, 3),
(2, 2),
(2, 3);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Badges`
--
ALTER TABLE `Badges`
  ADD PRIMARY KEY (`badge_id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `tg_id` (`tg_id`);

--
-- Indexes for table `Tags`
--
ALTER TABLE `Tags`
  ADD PRIMARY KEY (`tag_id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `Tasks`
--
ALTER TABLE `Tasks`
  ADD PRIMARY KEY (`task_id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `assigned_user` (`assigned_user`);

--
-- Indexes for table `Tasks_Tags`
--
ALTER TABLE `Tasks_Tags`
  ADD PRIMARY KEY (`tk_id`,`tg_id`),
  ADD KEY `tg_id` (`tg_id`);

--
-- Indexes for table `Users`
--
ALTER TABLE `Users`
  ADD PRIMARY KEY (`user_id`);

--
-- Indexes for table `Users_Badges`
--
ALTER TABLE `Users_Badges`
  ADD PRIMARY KEY (`ur_id`,`be_id`),
  ADD KEY `be_id` (`be_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Badges`
--
ALTER TABLE `Badges`
  MODIFY `badge_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `Tags`
--
ALTER TABLE `Tags`
  MODIFY `tag_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `Tasks`
--
ALTER TABLE `Tasks`
  MODIFY `task_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `Users`
--
ALTER TABLE `Users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Badges`
--
ALTER TABLE `Badges`
  ADD CONSTRAINT `Badges_ibfk_1` FOREIGN KEY (`tg_id`) REFERENCES `Tags` (`tag_id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `Tasks`
--
ALTER TABLE `Tasks`
  ADD CONSTRAINT `Tasks_ibfk_1` FOREIGN KEY (`assigned_user`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `Tasks_Tags`
--
ALTER TABLE `Tasks_Tags`
  ADD CONSTRAINT `Tasks_Tags_ibfk_1` FOREIGN KEY (`tk_id`) REFERENCES `Tasks` (`task_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `Tasks_Tags_ibfk_2` FOREIGN KEY (`tg_id`) REFERENCES `Tags` (`tag_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `Users_Badges`
--
ALTER TABLE `Users_Badges`
  ADD CONSTRAINT `Users_Badges_ibfk_1` FOREIGN KEY (`ur_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `Users_Badges_ibfk_2` FOREIGN KEY (`be_id`) REFERENCES `Badges` (`badge_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
