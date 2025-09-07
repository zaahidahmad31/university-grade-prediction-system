CREATE DATABASE  IF NOT EXISTS `university_grade_prediction_test_1` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `university_grade_prediction_test_1`;
-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: university_grade_prediction_test_1
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `academic_terms`
--

DROP TABLE IF EXISTS `academic_terms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `academic_terms` (
  `term_id` int NOT NULL AUTO_INCREMENT,
  `term_name` varchar(50) NOT NULL,
  `term_code` varchar(20) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `is_current` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`term_id`),
  UNIQUE KEY `term_code` (`term_code`),
  KEY `idx_dates` (`start_date`,`end_date`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `academic_terms`
--

LOCK TABLES `academic_terms` WRITE;
/*!40000 ALTER TABLE `academic_terms` DISABLE KEYS */;
INSERT INTO `academic_terms` VALUES (1,'Fall 2024','FALL2024','2024-09-01','2024-12-20',0),(2,'Spring 2025','SPRING2025','2025-01-15','2025-05-15',1);
/*!40000 ALTER TABLE `academic_terms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alert_types`
--

DROP TABLE IF EXISTS `alert_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alert_types` (
  `type_id` int NOT NULL AUTO_INCREMENT,
  `type_name` varchar(50) NOT NULL,
  `severity` enum('info','warning','critical') NOT NULL,
  `description` text,
  PRIMARY KEY (`type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alert_types`
--

LOCK TABLES `alert_types` WRITE;
/*!40000 ALTER TABLE `alert_types` DISABLE KEYS */;
INSERT INTO `alert_types` VALUES (12,'at_risk_prediction','critical','Student identified as at-risk by prediction model'),(13,'Failing Grade Risk','critical','Predicted grade: Fail with 97% confidence'),(14,'Low Engagement','info','LMS activity is 0.0 per day (course average: 10.0)');
/*!40000 ALTER TABLE `alert_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alerts`
--

DROP TABLE IF EXISTS `alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alerts` (
  `alert_id` int NOT NULL AUTO_INCREMENT,
  `enrollment_id` int NOT NULL,
  `type_id` int NOT NULL,
  `triggered_date` datetime NOT NULL,
  `alert_message` text NOT NULL,
  `severity` enum('info','warning','critical') NOT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `read_date` datetime DEFAULT NULL,
  `is_resolved` tinyint(1) DEFAULT '0',
  `resolved_date` datetime DEFAULT NULL,
  `resolved_by` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`alert_id`),
  KEY `type_id` (`type_id`),
  KEY `idx_enrollment` (`enrollment_id`),
  KEY `idx_unread` (`is_read`,`enrollment_id`),
  KEY `idx_severity` (`severity`),
  CONSTRAINT `alerts_ibfk_1` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`),
  CONSTRAINT `alerts_ibfk_2` FOREIGN KEY (`type_id`) REFERENCES `alert_types` (`type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=170 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alerts`
--

LOCK TABLES `alerts` WRITE;
/*!40000 ALTER TABLE `alerts` DISABLE KEYS */;
INSERT INTO `alerts` VALUES (157,394,12,'2025-06-15 20:22:32','Student predicted to Fail with high risk level','critical',1,'2025-06-15 22:55:22',0,NULL,NULL),(158,394,13,'2025-06-15 20:24:00','Predicted grade: Fail with 97% confidence','critical',1,'2025-06-15 22:55:22',0,NULL,NULL),(159,394,12,'2025-06-15 20:59:20','Student predicted to Fail with high risk level','critical',1,'2025-06-15 22:55:19',0,NULL,NULL),(160,394,12,'2025-06-15 22:56:33','Student predicted to Fail with high risk level','critical',1,'2025-06-16 00:04:49',0,NULL,NULL),(161,394,14,'2025-06-16 00:00:30','LMS activity is 0.0 per day (course average: 10.0)','info',1,'2025-06-16 00:04:50',0,NULL,NULL),(162,394,12,'2025-06-16 00:10:13','Student predicted to Fail with high risk level','critical',0,NULL,0,NULL,NULL),(163,394,12,'2025-06-16 00:43:06','Student predicted to Fail with high risk level','critical',0,NULL,0,NULL,NULL),(164,394,12,'2025-06-16 01:35:38','Student predicted to Pass with high risk level','critical',0,NULL,0,NULL,NULL),(165,394,12,'2025-06-16 01:41:26','Student predicted to Pass with high risk level','critical',0,NULL,0,NULL,NULL),(166,394,12,'2025-06-16 01:41:49','Student predicted to Pass with high risk level','critical',1,'2025-06-16 02:20:04',0,NULL,NULL),(167,394,12,'2025-06-16 02:25:51','Student predicted to Fail with medium risk level','critical',1,'2025-06-16 02:47:32',0,NULL,NULL),(168,394,12,'2025-06-16 02:35:29','Student predicted to Fail with medium risk level','critical',1,'2025-06-16 02:47:33',0,NULL,NULL),(169,394,12,'2025-06-16 02:39:30','Student predicted to Fail with medium risk level','critical',1,'2025-06-16 02:47:40',0,NULL,NULL);
/*!40000 ALTER TABLE `alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assessment_submissions`
--

DROP TABLE IF EXISTS `assessment_submissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assessment_submissions` (
  `submission_id` int NOT NULL AUTO_INCREMENT,
  `enrollment_id` int NOT NULL,
  `assessment_id` int NOT NULL,
  `submission_date` datetime NOT NULL,
  `score` decimal(6,2) DEFAULT NULL,
  `percentage` decimal(5,2) DEFAULT NULL,
  `is_late` tinyint(1) DEFAULT '0',
  `late_penalty` decimal(5,2) DEFAULT '0.00',
  `graded_date` datetime DEFAULT NULL,
  `graded_by` varchar(20) DEFAULT NULL,
  `feedback` text,
  `attempt_number` int DEFAULT '1',
  `submission_text` text,
  `file_path` varchar(500) DEFAULT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  `file_size` int DEFAULT NULL,
  `mime_type` varchar(100) DEFAULT NULL,
  `submission_type` varchar(50) DEFAULT 'text',
  PRIMARY KEY (`submission_id`),
  UNIQUE KEY `unique_submission` (`enrollment_id`,`assessment_id`,`attempt_number`),
  KEY `idx_enrollment` (`enrollment_id`),
  KEY `idx_assessment` (`assessment_id`),
  CONSTRAINT `assessment_submissions_ibfk_1` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`),
  CONSTRAINT `assessment_submissions_ibfk_2` FOREIGN KEY (`assessment_id`) REFERENCES `assessments` (`assessment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=978 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assessment_submissions`
--

LOCK TABLES `assessment_submissions` WRITE;
/*!40000 ALTER TABLE `assessment_submissions` DISABLE KEYS */;
INSERT INTO `assessment_submissions` VALUES (971,394,243,'2025-06-15 14:43:44',18.00,90.00,0,0.00,'2025-06-15 14:44:36','FACC495E345',NULL,1,'this is the answer',NULL,NULL,NULL,NULL,'text'),(972,394,244,'2025-06-15 14:47:24',25.00,83.33,0,0.00,'2025-06-15 14:48:14','FACC495E345',NULL,1,'this is the answer for assignment 1',NULL,NULL,NULL,NULL,'text'),(973,394,245,'2025-06-15 14:50:29',85.00,85.00,0,0.00,'2025-06-15 14:52:04','FACC495E345',NULL,1,'this is the answers for final exam',NULL,NULL,NULL,NULL,'text'),(974,394,246,'2025-06-15 19:09:52',16.00,80.00,0,0.00,'2025-06-15 19:12:18','FACC495E345',NULL,1,'this is the answer',NULL,NULL,NULL,NULL,'text'),(975,394,247,'2025-06-15 19:09:59',28.00,93.33,0,0.00,'2025-06-15 19:12:46','FACC495E345',NULL,1,'this is the answer',NULL,NULL,NULL,NULL,'text'),(976,394,248,'2025-06-15 19:10:06',45.00,90.00,0,0.00,'2025-06-15 19:12:32','FACC495E345',NULL,1,'this is the answer',NULL,NULL,NULL,NULL,'text'),(977,394,249,'2025-06-15 20:55:27',NULL,NULL,0,0.00,NULL,NULL,NULL,1,'this is the answer',NULL,NULL,NULL,NULL,'text');
/*!40000 ALTER TABLE `assessment_submissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assessment_types`
--

DROP TABLE IF EXISTS `assessment_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assessment_types` (
  `type_id` int NOT NULL AUTO_INCREMENT,
  `type_name` varchar(50) NOT NULL,
  `weight_percentage` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`type_id`),
  CONSTRAINT `assessment_types_chk_1` CHECK (((`weight_percentage` >= 0) and (`weight_percentage` <= 100)))
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assessment_types`
--

LOCK TABLES `assessment_types` WRITE;
/*!40000 ALTER TABLE `assessment_types` DISABLE KEYS */;
INSERT INTO `assessment_types` VALUES (1,'Quiz',20.00),(2,'Assignment',30.00),(3,'Midterm Exam',20.00),(4,'Final Exam',25.00),(5,'Participation',5.00),(6,'CMA',30.00),(7,'TMA',50.00),(8,'Exam',20.00);
/*!40000 ALTER TABLE `assessment_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assessments`
--

DROP TABLE IF EXISTS `assessments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assessments` (
  `assessment_id` int NOT NULL AUTO_INCREMENT,
  `offering_id` int NOT NULL,
  `type_id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `max_score` decimal(6,2) NOT NULL,
  `due_date` datetime DEFAULT NULL,
  `weight` decimal(5,2) DEFAULT NULL,
  `description` text,
  `is_published` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `assessment_type_mapped` enum('CMA','TMA','Exam','Assignment','Quiz') DEFAULT 'Assignment',
  PRIMARY KEY (`assessment_id`),
  KEY `type_id` (`type_id`),
  KEY `idx_offering` (`offering_id`),
  KEY `idx_due_date` (`due_date`),
  CONSTRAINT `assessments_ibfk_1` FOREIGN KEY (`offering_id`) REFERENCES `course_offerings` (`offering_id`),
  CONSTRAINT `assessments_ibfk_2` FOREIGN KEY (`type_id`) REFERENCES `assessment_types` (`type_id`),
  CONSTRAINT `assessments_chk_1` CHECK (((`weight` >= 0) and (`weight` <= 100)))
) ENGINE=InnoDB AUTO_INCREMENT=250 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assessments`
--

LOCK TABLES `assessments` WRITE;
/*!40000 ALTER TABLE `assessments` DISABLE KEYS */;
INSERT INTO `assessments` VALUES (243,58,1,'Quiz-1',20.00,'2025-06-22 18:29:00',20.00,'this is your first quiz',1,'2025-06-15 09:12:21','Assignment'),(244,58,2,'Assignment 1',30.00,'2025-06-19 18:29:00',30.00,'this is the first assignment',1,'2025-06-15 09:15:51','Assignment'),(245,58,4,'Final Exam',100.00,'2025-06-30 18:29:00',25.00,'this is the final exam',1,'2025-06-15 09:19:26','Assignment'),(246,58,6,'CMA 1',20.00,'2025-06-23 18:29:00',30.00,'This is cms 1',1,'2025-06-15 13:38:19','Assignment'),(247,58,7,'TMA 1',30.00,'2025-06-23 18:29:00',50.00,'This is TMA 1',1,'2025-06-15 13:38:47','Assignment'),(248,58,8,'Exam 1',50.00,'2025-06-23 18:29:00',20.00,'This is Exam 1',1,'2025-06-15 13:39:16','Assignment'),(249,58,6,'CMA 2',35.00,'2025-06-23 18:29:00',30.00,'This is CMS 2',1,'2025-06-15 15:24:38','Assignment');
/*!40000 ALTER TABLE `assessments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `attendance_id` int NOT NULL AUTO_INCREMENT,
  `enrollment_id` int NOT NULL,
  `attendance_date` date NOT NULL,
  `status` enum('present','absent','late','excused') NOT NULL,
  `check_in_time` time DEFAULT NULL,
  `check_out_time` time DEFAULT NULL,
  `duration_minutes` int DEFAULT NULL,
  `recorded_by` varchar(50) DEFAULT NULL,
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`attendance_id`),
  KEY `idx_enrollment_date` (`enrollment_id`,`attendance_date`),
  KEY `idx_date` (`attendance_date`),
  KEY `idx_status` (`status`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8035 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (8033,394,'2025-06-15','present',NULL,NULL,NULL,'FACC495E345',NULL,'2025-06-15 09:09:07'),(8034,394,'2025-06-16','present',NULL,NULL,NULL,'FACC495E345',NULL,'2025-06-15 15:22:21');
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_log`
--

DROP TABLE IF EXISTS `audit_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_log` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `table_name` varchar(50) DEFAULT NULL,
  `record_id` int DEFAULT NULL,
  `old_values` json DEFAULT NULL,
  `new_values` json DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  KEY `idx_created` (`created_at`),
  KEY `idx_user` (`user_id`),
  KEY `idx_action` (`action`),
  CONSTRAINT `audit_log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_log`
--

LOCK TABLES `audit_log` WRITE;
/*!40000 ALTER TABLE `audit_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `audit_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_offerings`
--

DROP TABLE IF EXISTS `course_offerings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_offerings` (
  `offering_id` int NOT NULL AUTO_INCREMENT,
  `course_id` varchar(20) NOT NULL,
  `term_id` int NOT NULL,
  `faculty_id` varchar(20) DEFAULT NULL,
  `section_number` varchar(10) DEFAULT NULL,
  `capacity` int DEFAULT NULL,
  `enrolled_count` int DEFAULT '0',
  `meeting_pattern` varchar(50) DEFAULT NULL,
  `location` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`offering_id`),
  UNIQUE KEY `unique_offering` (`course_id`,`term_id`,`section_number`),
  KEY `faculty_id` (`faculty_id`),
  KEY `idx_term_course` (`term_id`,`course_id`),
  CONSTRAINT `course_offerings_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`),
  CONSTRAINT `course_offerings_ibfk_2` FOREIGN KEY (`term_id`) REFERENCES `academic_terms` (`term_id`),
  CONSTRAINT `course_offerings_ibfk_3` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`faculty_id`),
  CONSTRAINT `course_offerings_chk_1` CHECK ((`capacity` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_offerings`
--

LOCK TABLES `course_offerings` WRITE;
/*!40000 ALTER TABLE `course_offerings` DISABLE KEYS */;
INSERT INTO `course_offerings` VALUES (58,'INTE 0001',2,'FACC495E345','001',20,2,'8.00-10.00','R-1');
/*!40000 ALTER TABLE `course_offerings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `course_id` varchar(20) NOT NULL,
  `course_code` varchar(20) NOT NULL,
  `course_name` varchar(100) NOT NULL,
  `credits` int NOT NULL,
  `department` varchar(100) DEFAULT NULL,
  `description` text,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`course_id`),
  KEY `idx_course_code` (`course_code`),
  KEY `idx_department` (`department`),
  CONSTRAINT `courses_chk_1` CHECK ((`credits` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES ('INTE 0001','INTE 0001','Web Application Development',2,NULL,'This code include basic web application development tools and techniques',1,'2025-06-15 09:02:27');
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enrollments`
--

DROP TABLE IF EXISTS `enrollments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enrollments` (
  `enrollment_id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(20) NOT NULL,
  `offering_id` int NOT NULL,
  `enrollment_date` date NOT NULL,
  `enrollment_status` enum('enrolled','dropped','completed','withdrawn') DEFAULT 'enrolled',
  `final_grade` varchar(2) DEFAULT NULL,
  `grade_points` decimal(3,2) DEFAULT NULL,
  PRIMARY KEY (`enrollment_id`),
  UNIQUE KEY `unique_enrollment` (`student_id`,`offering_id`),
  KEY `offering_id` (`offering_id`),
  KEY `idx_student_offering` (`student_id`,`offering_id`),
  KEY `idx_status` (`enrollment_status`),
  CONSTRAINT `enrollments_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`),
  CONSTRAINT `enrollments_ibfk_2` FOREIGN KEY (`offering_id`) REFERENCES `course_offerings` (`offering_id`)
) ENGINE=InnoDB AUTO_INCREMENT=396 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enrollments`
--

LOCK TABLES `enrollments` WRITE;
/*!40000 ALTER TABLE `enrollments` DISABLE KEYS */;
INSERT INTO `enrollments` VALUES (394,'STU3ECD87A0',58,'2025-06-15','enrolled','B',3.00),(395,'STU300F95FB',58,'2025-06-15','enrolled',NULL,NULL);
/*!40000 ALTER TABLE `enrollments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculty`
--

DROP TABLE IF EXISTS `faculty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty` (
  `faculty_id` varchar(20) NOT NULL,
  `user_id` int DEFAULT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `department` varchar(100) DEFAULT NULL,
  `position` varchar(50) DEFAULT NULL,
  `office_location` varchar(50) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`faculty_id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `idx_department` (`department`),
  CONSTRAINT `faculty_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty`
--

LOCK TABLES `faculty` WRITE;
/*!40000 ALTER TABLE `faculty` DISABLE KEYS */;
INSERT INTO `faculty` VALUES ('FACC495E345',151,'kaushalya','wickramasinhge','industrial management',NULL,NULL,NULL,'2025-06-15 08:59:14');
/*!40000 ALTER TABLE `faculty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feature_cache`
--

DROP TABLE IF EXISTS `feature_cache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feature_cache` (
  `cache_id` int NOT NULL AUTO_INCREMENT,
  `enrollment_id` int NOT NULL,
  `feature_date` date NOT NULL,
  `attendance_rate` decimal(5,2) DEFAULT NULL,
  `avg_session_duration` decimal(8,2) DEFAULT NULL,
  `login_frequency` decimal(8,2) DEFAULT NULL,
  `resource_access_rate` decimal(5,2) DEFAULT NULL,
  `assignment_submission_rate` decimal(5,2) DEFAULT NULL,
  `avg_assignment_score` decimal(5,2) DEFAULT NULL,
  `forum_engagement_score` decimal(8,2) DEFAULT NULL,
  `study_consistency_score` decimal(5,2) DEFAULT NULL,
  `last_login_days_ago` int DEFAULT NULL,
  `total_study_minutes` int DEFAULT NULL,
  `calculated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cache_id`),
  UNIQUE KEY `unique_cache` (`enrollment_id`,`feature_date`),
  KEY `idx_date` (`feature_date`),
  CONSTRAINT `feature_cache_ibfk_1` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=288 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feature_cache`
--

LOCK TABLES `feature_cache` WRITE;
/*!40000 ALTER TABLE `feature_cache` DISABLE KEYS */;
INSERT INTO `feature_cache` VALUES (285,394,'2025-06-15',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-06-15 09:09:22'),(286,394,'2025-06-16',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-06-15 13:00:30'),(287,395,'2025-06-16',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-06-15 13:07:14');
/*!40000 ALTER TABLE `feature_cache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interventions`
--

DROP TABLE IF EXISTS `interventions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interventions` (
  `intervention_id` int NOT NULL AUTO_INCREMENT,
  `enrollment_id` int NOT NULL,
  `alert_id` int DEFAULT NULL,
  `faculty_id` varchar(20) NOT NULL,
  `intervention_date` datetime NOT NULL,
  `intervention_type` varchar(50) DEFAULT NULL,
  `description` text,
  `outcome` text,
  `follow_up_date` date DEFAULT NULL,
  `is_successful` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`intervention_id`),
  KEY `alert_id` (`alert_id`),
  KEY `faculty_id` (`faculty_id`),
  KEY `idx_enrollment` (`enrollment_id`),
  CONSTRAINT `interventions_ibfk_1` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`),
  CONSTRAINT `interventions_ibfk_2` FOREIGN KEY (`alert_id`) REFERENCES `alerts` (`alert_id`),
  CONSTRAINT `interventions_ibfk_3` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`faculty_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interventions`
--

LOCK TABLES `interventions` WRITE;
/*!40000 ALTER TABLE `interventions` DISABLE KEYS */;
/*!40000 ALTER TABLE `interventions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lms_activities`
--

DROP TABLE IF EXISTS `lms_activities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lms_activities` (
  `activity_id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `enrollment_id` int NOT NULL,
  `activity_type` enum('resource_view','forum_post','forum_reply','assignment_view','quiz_attempt','video_watch','file_download','page_view') NOT NULL,
  `activity_timestamp` timestamp NOT NULL,
  `resource_id` varchar(50) DEFAULT NULL,
  `resource_name` varchar(255) DEFAULT NULL,
  `duration_seconds` int DEFAULT NULL,
  `details` json DEFAULT NULL,
  PRIMARY KEY (`activity_id`),
  KEY `session_id` (`session_id`),
  KEY `idx_enrollment_timestamp` (`enrollment_id`,`activity_timestamp`),
  KEY `idx_type` (`activity_type`),
  CONSTRAINT `lms_activities_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `lms_sessions` (`session_id`),
  CONSTRAINT `lms_activities_ibfk_2` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8084 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lms_activities`
--

LOCK TABLES `lms_activities` WRITE;
/*!40000 ALTER TABLE `lms_activities` DISABLE KEYS */;
INSERT INTO `lms_activities` VALUES (8019,1491,394,'page_view','2025-06-15 15:19:57','/student/predictions.html','My Predictions - University Grade Prediction System',NULL,'null'),(8020,1491,394,'page_view','2025-06-15 15:20:24','/student/dashboard.html','Student Dashboard - University Grade Prediction System',NULL,'null'),(8021,1491,394,'page_view','2025-06-15 15:20:25','/student/courses.html','My Courses - Student Portal',NULL,'null'),(8022,1491,394,'page_view','2025-06-15 15:21:01','/student/attendance.html','My Attendance - Student Portal',NULL,'null'),(8023,1491,394,'page_view','2025-06-15 15:22:33','/student/dashboard.html','Student Dashboard - University Grade Prediction System',NULL,'null'),(8024,1491,394,'page_view','2025-06-15 15:22:38','/student/courses.html','My Courses - Student Portal',NULL,'null'),(8025,1491,394,'page_view','2025-06-15 15:24:51','/student/dashboard.html','Student Dashboard - University Grade Prediction System',NULL,'null'),(8026,1491,394,'page_view','2025-06-15 15:25:09','/student/predictions.html','My Predictions - University Grade Prediction System',NULL,'null'),(8027,1491,394,'page_view','2025-06-15 15:25:13','/student/assessments.html','My Assessments - University Grade Prediction System',NULL,'null'),(8028,1491,394,'page_view','2025-06-15 15:25:15','/student/assessment-submit.html','Submit Assessment - University Grade Prediction System',NULL,'null'),(8029,1491,394,'assignment_view','2025-06-15 15:25:15','assessment_249','CMA 2',NULL,'null'),(8030,1491,394,'page_view','2025-06-15 15:25:29','/student/assessments.html','My Assessments - University Grade Prediction System',NULL,'null'),(8031,1491,394,'page_view','2025-06-15 15:25:34','/student/grades.html','My Grades - University Grade Prediction System',NULL,'null'),(8032,1491,394,'page_view','2025-06-15 15:25:48','/student/predictions.html','My Predictions - University Grade Prediction System',NULL,'null'),(8033,1491,394,'page_view','2025-06-15 15:34:00','/student/grades.html','My Grades - University Grade Prediction System',NULL,'null'),(8034,1491,394,'page_view','2025-06-15 15:34:16','/student/courses.html','My Courses - Student Portal',NULL,'null'),(8035,1491,394,'page_view','2025-06-15 15:34:18','/student/dashboard.html','Student Dashboard - University Grade Prediction System',NULL,'null'),(8036,1491,394,'page_view','2025-06-15 15:34:20','/student/courses.html','My Courses - Student Portal',NULL,'null'),(8037,1491,394,'page_view','2025-06-15 15:34:20','/student/attendance.html','My Attendance - Student Portal',NULL,'null'),(8038,1491,394,'page_view','2025-06-15 15:34:35','/student/courses.html','My Courses - Student Portal',NULL,'null'),(8039,1491,394,'page_view','2025-06-15 15:34:41','/student/grades.html','My Grades - University Grade Prediction System',NULL,'null'),(8040,1491,394,'page_view','2025-06-15 15:34:48','/student/predictions.html','My Predictions - University Grade Prediction System',NULL,'null'),(8041,1491,394,'page_view','2025-06-15 15:34:53','/student/attendance.html','My Attendance - Student Portal',NULL,'null'),(8042,1491,394,'page_view','2025-06-15 15:35:27','/student/predictions.html','My Predictions - University Grade Prediction System',NULL,'null'),(8043,1491,394,'page_view','2025-06-15 15:39:25','/student/predictions.html','My Predictions - University Grade Prediction System',NULL,'null'),(8044,1491,394,'page_view','2025-06-15 15:39:33','/student/courses.html','My Courses - Student Portal',NULL,'null'),(8045,1491,394,'page_view','2025-06-15 15:40:41','/student/dashboard.html','Student Dashboard - University Grade Prediction System',NULL,'null'),(8046,1491,394,'page_view','2025-06-15 15:40:44','/student/dashboard.html','Student Dashboard - University Grade Prediction System',NULL,'null'),(8047,1491,394,'page_view','2025-06-15 15:41:00','/student/predictions.html','My Predictions - University Grade Prediction System',NULL,'null'),(8048,1491,394,'page_view','2025-06-15 15:41:03','/student/grades.html','My Grades - University Grade Prediction System',NULL,'null'),(8049,1491,394,'page_view','2025-06-15 15:41:05','/student/predictions.html','My Predictions - University Grade Prediction System',NULL,'null'),(8050,1491,394,'page_view','2025-06-15 15:41:12','/student/grades.html','My Grades - University Grade Prediction System',NULL,'null'),(8051,1491,394,'page_view','2025-06-15 15:41:18','/student/courses.html','My Courses - Student Portal',NULL,'null'),(8052,1491,394,'page_view','2025-06-15 15:41:54','/student/dashboard.html','Student Dashboard - University Grade Prediction System',NULL,'null'),(8053,1491,394,'page_view','2025-06-15 15:46:54','/student/dashboard.html','Student Dashboard - University Grade Prediction System',NULL,'null'),(8054,1491,394,'page_view','2025-06-15 15:47:18','/student/assessments.html','My Assessments - University Grade Prediction System',NULL,'null'),(8055,1491,394,'page_view','2025-06-15 15:47:46','/student/assessments.html','My Assessments - University Grade Prediction System',NULL,'null'),(8056,1491,394,'page_view','2025-06-15 15:52:32','/student/dashboard.html','Student Dashboard - University Grade Prediction System',NULL,'null'),(8057,1491,394,'page_view','2025-06-15 15:52:39','/student/predictions.html','My Predictions - University Grade Prediction System',NULL,'null'),(8058,1491,394,'page_view','2025-06-15 15:54:08','/student/predictions.html','My Predictions - University Grade Prediction System',NULL,'null'),(8059,1491,394,'page_view','2025-06-15 15:54:36','/student/dashboard.html','Student Dashboard - University Grade Prediction System',NULL,'null'),(8060,1492,394,'page_view','2025-06-15 16:35:42','/student/dashboard.html','Student Dashboard - University Grade Prediction System',NULL,'null'),(8061,1492,394,'page_view','2025-06-15 16:35:58','/student/dashboard.html','Learing Management System',NULL,'null'),(8062,1492,394,'page_view','2025-06-15 16:36:15','/student/dashboard.html','Learing Management System',NULL,'null'),(8063,1492,394,'page_view','2025-06-15 16:36:28','/student/dashboard.html','Learing Management System',NULL,'null'),(8064,1492,394,'page_view','2025-06-15 16:36:37','/student/dashboard.html','Learing Management System',NULL,'null'),(8065,1492,394,'page_view','2025-06-15 16:36:46','/student/dashboard.html','Learing Management System',NULL,'null'),(8066,1492,394,'page_view','2025-06-15 16:36:48','/student/dashboard.html','Learing Management System',NULL,'null'),(8067,1492,394,'page_view','2025-06-15 16:36:57','/student/dashboard.html','Learing Management System',NULL,'null'),(8068,1492,394,'page_view','2025-06-15 16:37:05','/student/dashboard.html','Learing Management System',NULL,'null'),(8069,1492,394,'page_view','2025-06-15 16:37:15','/student/dashboard.html','Learing Management System',NULL,'null'),(8070,1492,394,'page_view','2025-06-15 16:37:16','/student/dashboard.html','Learing Management System',NULL,'null'),(8071,1492,394,'page_view','2025-06-15 16:37:24','/student/dashboard.html','Learing Management System',NULL,'null'),(8072,1492,394,'page_view','2025-06-15 16:37:29','/student/dashboard.html','Learing Management System',NULL,'null'),(8073,1492,394,'page_view','2025-06-15 16:37:31','/student/courses.html','Learing Management System',NULL,'null'),(8074,1492,394,'page_view','2025-06-15 16:37:33','/student/attendance.html','Learing Management System',NULL,'null'),(8075,1492,394,'page_view','2025-06-15 16:37:34','/student/assessments.html','Learing Management System',NULL,'null'),(8076,1492,394,'page_view','2025-06-15 16:37:35','/student/grades.html','Learing Management System',NULL,'null'),(8077,1492,394,'page_view','2025-06-15 16:37:36','/student/predictions.html','Learing Management System',NULL,'null'),(8078,1492,394,'page_view','2025-06-15 16:37:37','/student/grades.html','Learing Management System',NULL,'null'),(8079,1492,394,'page_view','2025-06-15 16:37:39','/student/predictions.html','Learing Management System',NULL,'null'),(8080,1492,394,'page_view','2025-06-15 16:37:40','/student/assessments.html','Learing Management System',NULL,'null'),(8081,1492,394,'page_view','2025-06-15 16:37:43','/student/attendance.html','Learing Management System',NULL,'null'),(8082,1492,394,'page_view','2025-06-15 16:37:46','/student/courses.html','Learing Management System',NULL,'null'),(8083,1492,394,'page_view','2025-06-15 16:37:49','/student/dashboard.html','Learing Management System',NULL,'null');
/*!40000 ALTER TABLE `lms_activities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lms_daily_summary`
--

DROP TABLE IF EXISTS `lms_daily_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lms_daily_summary` (
  `summary_id` int NOT NULL AUTO_INCREMENT,
  `enrollment_id` int NOT NULL,
  `summary_date` date NOT NULL,
  `total_minutes` int DEFAULT '0',
  `login_count` int DEFAULT '0',
  `resource_views` int DEFAULT '0',
  `forum_posts` int DEFAULT '0',
  `forum_replies` int DEFAULT '0',
  `files_downloaded` int DEFAULT '0',
  `videos_watched` int DEFAULT '0',
  `pages_viewed` int DEFAULT '0',
  PRIMARY KEY (`summary_id`),
  UNIQUE KEY `unique_daily` (`enrollment_id`,`summary_date`),
  KEY `idx_date` (`summary_date`),
  CONSTRAINT `lms_daily_summary_ibfk_1` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=445 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lms_daily_summary`
--

LOCK TABLES `lms_daily_summary` WRITE;
/*!40000 ALTER TABLE `lms_daily_summary` DISABLE KEYS */;
INSERT INTO `lms_daily_summary` VALUES (444,394,'2025-06-15',0,3,0,0,0,0,0,65);
/*!40000 ALTER TABLE `lms_daily_summary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lms_sessions`
--

DROP TABLE IF EXISTS `lms_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lms_sessions` (
  `session_id` int NOT NULL AUTO_INCREMENT,
  `enrollment_id` int NOT NULL,
  `login_time` timestamp NOT NULL,
  `logout_time` timestamp NULL DEFAULT NULL,
  `duration_minutes` int DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`session_id`),
  KEY `idx_enrollment` (`enrollment_id`),
  KEY `idx_login_time` (`login_time`),
  CONSTRAINT `lms_sessions_ibfk_1` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1493 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lms_sessions`
--

LOCK TABLES `lms_sessions` WRITE;
/*!40000 ALTER TABLE `lms_sessions` DISABLE KEYS */;
INSERT INTO `lms_sessions` VALUES (1490,394,'2025-06-15 11:50:55',NULL,NULL,NULL,NULL),(1491,394,'2025-06-15 15:19:57',NULL,NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0'),(1492,394,'2025-06-15 16:35:42',NULL,NULL,'127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0');
/*!40000 ALTER TABLE `lms_sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ml_feature_staging`
--

DROP TABLE IF EXISTS `ml_feature_staging`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ml_feature_staging` (
  `staging_id` int NOT NULL AUTO_INCREMENT,
  `enrollment_id` int NOT NULL,
  `calculation_date` date NOT NULL,
  `feature_data` json NOT NULL,
  `is_processed` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`staging_id`),
  KEY `idx_enrollment_date` (`enrollment_id`,`calculation_date`),
  CONSTRAINT `ml_feature_staging_ibfk_1` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=142 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ml_feature_staging`
--

LOCK TABLES `ml_feature_staging` WRITE;
/*!40000 ALTER TABLE `ml_feature_staging` DISABLE KEYS */;
/*!40000 ALTER TABLE `ml_feature_staging` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `model_versions`
--

DROP TABLE IF EXISTS `model_versions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `model_versions` (
  `version_id` int NOT NULL AUTO_INCREMENT,
  `version_name` varchar(50) NOT NULL,
  `model_file_path` varchar(255) DEFAULT NULL,
  `accuracy` decimal(5,2) DEFAULT NULL,
  `precision_score` decimal(5,2) DEFAULT NULL,
  `recall_score` decimal(5,2) DEFAULT NULL,
  `f1_score` decimal(5,2) DEFAULT NULL,
  `training_date` date DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '0',
  `feature_list` json DEFAULT NULL,
  `hyperparameters` json DEFAULT NULL,
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`version_id`),
  UNIQUE KEY `version_name` (`version_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `model_versions`
--

LOCK TABLES `model_versions` WRITE;
/*!40000 ALTER TABLE `model_versions` DISABLE KEYS */;
/*!40000 ALTER TABLE `model_versions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `predictions`
--

DROP TABLE IF EXISTS `predictions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `predictions` (
  `prediction_id` int NOT NULL AUTO_INCREMENT,
  `enrollment_id` int NOT NULL,
  `prediction_date` datetime NOT NULL,
  `predicted_grade` varchar(10) DEFAULT NULL,
  `confidence_score` decimal(3,2) DEFAULT NULL,
  `risk_level` enum('low','medium','high') NOT NULL,
  `model_version` varchar(50) DEFAULT NULL,
  `feature_snapshot` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `model_accuracy` decimal(5,2) DEFAULT NULL,
  `feature_version` varchar(20) DEFAULT 'v1.0',
  PRIMARY KEY (`prediction_id`),
  KEY `idx_enrollment_date` (`enrollment_id`,`prediction_date`),
  KEY `idx_risk_level` (`risk_level`),
  CONSTRAINT `predictions_ibfk_1` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollments` (`enrollment_id`),
  CONSTRAINT `predictions_chk_1` CHECK (((`confidence_score` >= 0) and (`confidence_score` <= 1)))
) ENGINE=InnoDB AUTO_INCREMENT=214 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `predictions`
--

LOCK TABLES `predictions` WRITE;
/*!40000 ALTER TABLE `predictions` DISABLE KEYS */;
INSERT INTO `predictions` VALUES (203,394,'2025-06-15 20:22:32','Fail',0.97,'high','2025-06-06T20:40:18.205446','{\"avg_score\": 42.666666666666664, \"days_active\": 1.0, \"total_clicks\": 30.0, \"activity_rate\": 100.0, \"avg_score_cma\": 0.0, \"avg_score_tma\": 0.0, \"activity_trend\": 0.0, \"avg_days_early\": 8.666666666666666, \"avg_score_exam\": 0.0, \"has_disability\": 0.0, \"studied_credits\": 60.0, \"submission_rate\": 100.0, \"age_band_encoded\": 0.0, \"unique_materials\": 1.0, \"last_activity_day\": 151.0, \"first_activity_day\": 151.0, \"activity_regularity\": 0.0, \"on_time_submissions\": 3.0, \"weekly_activity_std\": 0.0, \"num_of_prev_attempts\": 0.0, \"late_submission_count\": 0.0, \"submitted_assessments\": 3.0, \"longest_inactivity_gap\": 0.0, \"weekend_activity_ratio\": 0.0, \"avg_clicks_per_active_day\": 30.0, \"highest_education_encoded\": 2.0}','2025-06-15 09:22:32',NULL,'v1.0'),(204,394,'2025-06-15 20:59:20','Fail',0.97,'high','2025-06-06T20:40:18.205446','{\"avg_score\": 42.666666666666664, \"days_active\": 1.0, \"total_clicks\": 30.0, \"activity_rate\": 100.0, \"avg_score_cma\": 0.0, \"avg_score_tma\": 0.0, \"activity_trend\": 0.0, \"avg_days_early\": 8.666666666666666, \"avg_score_exam\": 0.0, \"has_disability\": 0.0, \"studied_credits\": 60.0, \"submission_rate\": 100.0, \"age_band_encoded\": 0.0, \"unique_materials\": 1.0, \"last_activity_day\": 151.0, \"first_activity_day\": 151.0, \"activity_regularity\": 0.0, \"on_time_submissions\": 3.0, \"weekly_activity_std\": 0.0, \"num_of_prev_attempts\": 0.0, \"late_submission_count\": 0.0, \"submitted_assessments\": 3.0, \"longest_inactivity_gap\": 0.0, \"weekend_activity_ratio\": 0.0, \"avg_clicks_per_active_day\": 30.0, \"highest_education_encoded\": 2.0}','2025-06-15 09:59:20',NULL,'v1.0'),(205,394,'2025-06-15 22:56:33','Fail',0.97,'high','2025-06-06T20:40:18.205446','{\"avg_score\": 42.666666666666664, \"days_active\": 1.0, \"total_clicks\": 30.0, \"activity_rate\": 100.0, \"avg_score_cma\": 0.0, \"avg_score_tma\": 0.0, \"activity_trend\": 0.0, \"avg_days_early\": 8.666666666666666, \"avg_score_exam\": 0.0, \"has_disability\": 0.0, \"studied_credits\": 60.0, \"submission_rate\": 100.0, \"age_band_encoded\": 0.0, \"unique_materials\": 1.0, \"last_activity_day\": 151.0, \"first_activity_day\": 151.0, \"activity_regularity\": 0.0, \"on_time_submissions\": 3.0, \"weekly_activity_std\": 0.0, \"num_of_prev_attempts\": 0.0, \"late_submission_count\": 0.0, \"submitted_assessments\": 3.0, \"longest_inactivity_gap\": 0.0, \"weekend_activity_ratio\": 0.0, \"avg_clicks_per_active_day\": 30.0, \"highest_education_encoded\": 2.0}','2025-06-15 11:56:33',NULL,'v1.0'),(206,394,'2025-06-16 00:10:13','Fail',0.97,'high','2025-06-06T20:40:18.205446','{\"avg_score\": 42.666666666666664, \"days_active\": 1.0, \"total_clicks\": 30.0, \"activity_rate\": 100.0, \"avg_score_cma\": 0.0, \"avg_score_tma\": 0.0, \"activity_trend\": 0.0, \"avg_days_early\": 8.666666666666666, \"avg_score_exam\": 0.0, \"has_disability\": 0.0, \"studied_credits\": 60.0, \"submission_rate\": 100.0, \"age_band_encoded\": 0.0, \"unique_materials\": 1.0, \"last_activity_day\": 151.0, \"first_activity_day\": 151.0, \"activity_regularity\": 0.0, \"on_time_submissions\": 3.0, \"weekly_activity_std\": 0.0, \"num_of_prev_attempts\": 0.0, \"late_submission_count\": 0.0, \"submitted_assessments\": 3.0, \"longest_inactivity_gap\": 0.0, \"weekend_activity_ratio\": 0.0, \"avg_clicks_per_active_day\": 30.0, \"highest_education_encoded\": 2.0}','2025-06-15 13:10:13',NULL,'v1.0'),(207,394,'2025-06-16 00:43:06','Fail',0.93,'high','2025-06-06T20:40:18.205446','{\"avg_score\": 36.166666666666664, \"days_active\": 1.0, \"total_clicks\": 30.0, \"activity_rate\": 100.0, \"avg_score_cma\": 0.0, \"avg_score_tma\": 0.0, \"activity_trend\": 0.0, \"avg_days_early\": 7.833333333333333, \"avg_score_exam\": 0.0, \"has_disability\": 0.0, \"studied_credits\": 60.0, \"submission_rate\": 100.0, \"age_band_encoded\": 0.0, \"unique_materials\": 1.0, \"last_activity_day\": 151.0, \"first_activity_day\": 151.0, \"activity_regularity\": 0.0, \"on_time_submissions\": 6.0, \"weekly_activity_std\": 0.0, \"num_of_prev_attempts\": 0.0, \"late_submission_count\": 0.0, \"submitted_assessments\": 6.0, \"longest_inactivity_gap\": 0.0, \"weekend_activity_ratio\": 0.0, \"avg_clicks_per_active_day\": 30.0, \"highest_education_encoded\": 2.0}','2025-06-15 13:43:06',NULL,'v1.0'),(208,394,'2025-06-16 01:35:38','Pass',0.56,'high','2025-06-06T20:40:18.205446','{\"avg_score\": 36.166666666666664, \"days_active\": 1.0, \"total_clicks\": 30.0, \"activity_rate\": 100.0, \"avg_score_cma\": 21.5, \"avg_score_tma\": 22.0, \"activity_trend\": 0.0, \"avg_days_early\": 7.833333333333333, \"avg_score_exam\": 65.0, \"has_disability\": 0.0, \"studied_credits\": 60.0, \"submission_rate\": 100.0, \"age_band_encoded\": 0.0, \"unique_materials\": 1.0, \"last_activity_day\": 151.0, \"first_activity_day\": 151.0, \"activity_regularity\": 0.0, \"on_time_submissions\": 6.0, \"weekly_activity_std\": 0.0, \"num_of_prev_attempts\": 0.0, \"late_submission_count\": 0.0, \"submitted_assessments\": 6.0, \"longest_inactivity_gap\": 0.0, \"weekend_activity_ratio\": 0.0, \"avg_clicks_per_active_day\": 30.0, \"highest_education_encoded\": 2.0}','2025-06-15 14:35:38',NULL,'v1.0'),(209,394,'2025-06-16 01:41:26','Pass',0.56,'high','2025-06-06T20:40:18.205446','{\"avg_score\": 36.166666666666664, \"days_active\": 1.0, \"total_clicks\": 30.0, \"activity_rate\": 100.0, \"avg_score_cma\": 21.5, \"avg_score_tma\": 22.0, \"activity_trend\": 0.0, \"avg_days_early\": 7.833333333333333, \"avg_score_exam\": 65.0, \"has_disability\": 0.0, \"studied_credits\": 60.0, \"submission_rate\": 100.0, \"age_band_encoded\": 0.0, \"unique_materials\": 1.0, \"last_activity_day\": 151.0, \"first_activity_day\": 151.0, \"activity_regularity\": 0.0, \"on_time_submissions\": 6.0, \"weekly_activity_std\": 0.0, \"num_of_prev_attempts\": 0.0, \"late_submission_count\": 0.0, \"submitted_assessments\": 6.0, \"longest_inactivity_gap\": 0.0, \"weekend_activity_ratio\": 0.0, \"avg_clicks_per_active_day\": 30.0, \"highest_education_encoded\": 2.0}','2025-06-15 14:41:26',NULL,'v1.0'),(210,394,'2025-06-16 01:41:49','Pass',0.56,'high','2025-06-06T20:40:18.205446','{\"avg_score\": 36.166666666666664, \"days_active\": 1.0, \"total_clicks\": 30.0, \"activity_rate\": 100.0, \"avg_score_cma\": 19.666666666666668, \"avg_score_tma\": 28.0, \"activity_trend\": 0.0, \"avg_days_early\": 7.833333333333333, \"avg_score_exam\": 65.0, \"has_disability\": 0.0, \"studied_credits\": 60.0, \"submission_rate\": 100.0, \"age_band_encoded\": 0.0, \"unique_materials\": 1.0, \"last_activity_day\": 151.0, \"first_activity_day\": 151.0, \"activity_regularity\": 0.0, \"on_time_submissions\": 6.0, \"weekly_activity_std\": 0.0, \"num_of_prev_attempts\": 0.0, \"late_submission_count\": 0.0, \"submitted_assessments\": 6.0, \"longest_inactivity_gap\": 0.0, \"weekend_activity_ratio\": 0.0, \"avg_clicks_per_active_day\": 30.0, \"highest_education_encoded\": 2.0}','2025-06-15 14:41:49',NULL,'v1.0'),(211,394,'2025-06-16 02:25:51','Fail',0.65,'medium','2025-06-06T20:40:18.205446','{\"avg_score\": 36.166666666666664, \"days_active\": 2.0, \"total_clicks\": 75.0, \"activity_rate\": 100.0, \"avg_score_cma\": 19.666666666666668, \"avg_score_tma\": 28.0, \"activity_trend\": -14.999999999999751, \"avg_days_early\": 7.714285714285714, \"avg_score_exam\": 65.0, \"has_disability\": 0.0, \"studied_credits\": 60.0, \"submission_rate\": 100.0, \"age_band_encoded\": 0.0, \"unique_materials\": 10.0, \"last_activity_day\": 152.0, \"first_activity_day\": 151.0, \"activity_regularity\": 50.0, \"on_time_submissions\": 7.0, \"weekly_activity_std\": 0.0, \"num_of_prev_attempts\": 0.0, \"late_submission_count\": 0.0, \"submitted_assessments\": 7.0, \"longest_inactivity_gap\": 1.0, \"weekend_activity_ratio\": 50.0, \"avg_clicks_per_active_day\": 37.5, \"highest_education_encoded\": 2.0}','2025-06-15 15:25:51',NULL,'v1.0'),(212,394,'2025-06-16 02:35:29','Fail',0.65,'medium','2025-06-06T20:40:18.205446','{\"avg_score\": 36.166666666666664, \"days_active\": 2.0, \"total_clicks\": 85.0, \"activity_rate\": 100.0, \"avg_score_cma\": 19.666666666666668, \"avg_score_tma\": 28.0, \"activity_trend\": -24.99999999999959, \"avg_days_early\": 7.714285714285714, \"avg_score_exam\": 65.0, \"has_disability\": 0.0, \"studied_credits\": 60.0, \"submission_rate\": 100.0, \"age_band_encoded\": 0.0, \"unique_materials\": 10.0, \"last_activity_day\": 152.0, \"first_activity_day\": 151.0, \"activity_regularity\": 50.0, \"on_time_submissions\": 7.0, \"weekly_activity_std\": 0.0, \"num_of_prev_attempts\": 0.0, \"late_submission_count\": 0.0, \"submitted_assessments\": 7.0, \"longest_inactivity_gap\": 1.0, \"weekend_activity_ratio\": 50.0, \"avg_clicks_per_active_day\": 42.5, \"highest_education_encoded\": 2.0}','2025-06-15 15:35:29',NULL,'v1.0'),(213,394,'2025-06-16 02:39:30','Fail',0.65,'medium','2025-06-06T20:40:18.205446','{\"avg_score\": 36.166666666666664, \"days_active\": 2.0, \"total_clicks\": 86.0, \"activity_rate\": 100.0, \"avg_score_cma\": 21.5, \"avg_score_tma\": 22.0, \"activity_trend\": -25.999999999999577, \"avg_days_early\": 7.714285714285714, \"avg_score_exam\": 65.0, \"has_disability\": 0.0, \"studied_credits\": 60.0, \"submission_rate\": 100.0, \"age_band_encoded\": 0.0, \"unique_materials\": 10.0, \"last_activity_day\": 152.0, \"first_activity_day\": 151.0, \"activity_regularity\": 50.0, \"on_time_submissions\": 7.0, \"weekly_activity_std\": 0.0, \"num_of_prev_attempts\": 0.0, \"late_submission_count\": 0.0, \"submitted_assessments\": 7.0, \"longest_inactivity_gap\": 1.0, \"weekend_activity_ratio\": 50.0, \"avg_clicks_per_active_day\": 43.0, \"highest_education_encoded\": 2.0}','2025-06-15 15:39:30',NULL,'v1.0');
/*!40000 ALTER TABLE `predictions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `student_id` varchar(20) NOT NULL,
  `user_id` int DEFAULT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `gender` enum('M','F','Other') DEFAULT NULL,
  `program_code` varchar(20) DEFAULT NULL,
  `year_of_study` int DEFAULT NULL,
  `enrollment_date` date NOT NULL,
  `expected_graduation` date DEFAULT NULL,
  `gpa` decimal(3,2) DEFAULT NULL,
  `status` enum('active','inactive','graduated','withdrawn') DEFAULT 'active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `profile_photo` varchar(255) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `address` text,
  `age_band` enum('0-35','35-55','55+') DEFAULT '0-35',
  `highest_education` enum('No Formal quals','Lower Than A Level','A Level or Equivalent','HE Qualification','Post Graduate Qualification') DEFAULT 'A Level or Equivalent',
  `num_of_prev_attempts` int DEFAULT '0',
  `studied_credits` int DEFAULT '60',
  `has_disability` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `idx_program` (`program_code`),
  KEY `idx_status` (`status`),
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `students_chk_1` CHECK ((`year_of_study` between 1 and 6)),
  CONSTRAINT `students_chk_2` CHECK (((`gpa` >= 0) and (`gpa` <= 4.0)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES ('STU300F95FB',152,'student','stu',NULL,NULL,NULL,NULL,'2025-06-15',NULL,NULL,'active','2025-06-15 13:06:07','2025-06-15 13:06:07',NULL,NULL,NULL,'0-35','A Level or Equivalent',0,60,0),('STU3ECD87A0',150,'lakshitha','sampath',NULL,NULL,NULL,NULL,'2025-06-15',NULL,3.00,'active','2025-06-15 08:56:54','2025-06-15 15:40:23',NULL,NULL,NULL,'0-35','A Level or Equivalent',0,60,0);
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_config`
--

DROP TABLE IF EXISTS `system_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_config` (
  `config_id` int NOT NULL AUTO_INCREMENT,
  `config_key` varchar(50) NOT NULL,
  `config_value` text,
  `description` text,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`config_id`),
  UNIQUE KEY `config_key` (`config_key`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_config`
--

LOCK TABLES `system_config` WRITE;
/*!40000 ALTER TABLE `system_config` DISABLE KEYS */;
/*!40000 ALTER TABLE `system_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `user_type` enum('student','faculty','admin') NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_user_type` (`user_type`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=153 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin@university.edu','pbkdf2:sha256:600000$IgF6W7qYgtf22FoW$b999c5225ec0ade36f15192a55779d999a4769007dcf4fb8f05dc946b16bf55b','admin',1,'2025-06-14 12:03:35','2025-06-15 16:32:40'),(150,'lakshitha','lakshitha@gmail.com','pbkdf2:sha256:600000$IgF6W7qYgtf22FoW$b999c5225ec0ade36f15192a55779d999a4769007dcf4fb8f05dc946b16bf55b','student',1,'2025-06-15 08:56:54','2025-06-15 16:35:42'),(151,'kaushalya','kaushalya@gmail.com','pbkdf2:sha256:600000$lIZAbsOmxo3m5ic8$938b422b917192cf27bea1abceefd32833c1e78572204c4f07ac8046f63637f0','faculty',1,'2025-06-15 08:59:14','2025-06-15 16:37:57'),(152,'student1','student1@gmail.com','pbkdf2:sha256:600000$jYJpQrgJIPSJFzjT$342244c23ee44427e97b32af74f106f320495ae796b069dc838921146ea07414','student',1,'2025-06-15 13:06:07','2025-06-15 14:22:57');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `v_at_risk_students`
--

DROP TABLE IF EXISTS `v_at_risk_students`;
/*!50001 DROP VIEW IF EXISTS `v_at_risk_students`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_at_risk_students` AS SELECT 
 1 AS `enrollment_id`,
 1 AS `student_id`,
 1 AS `first_name`,
 1 AS `last_name`,
 1 AS `course_code`,
 1 AS `course_name`,
 1 AS `predicted_grade`,
 1 AS `confidence_score`,
 1 AS `risk_level`,
 1 AS `prediction_date`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_current_enrollments`
--

DROP TABLE IF EXISTS `v_current_enrollments`;
/*!50001 DROP VIEW IF EXISTS `v_current_enrollments`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_current_enrollments` AS SELECT 
 1 AS `enrollment_id`,
 1 AS `student_id`,
 1 AS `first_name`,
 1 AS `last_name`,
 1 AS `course_code`,
 1 AS `course_name`,
 1 AS `section_number`,
 1 AS `instructor_first`,
 1 AS `instructor_last`,
 1 AS `term_name`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `v_at_risk_students`
--

/*!50001 DROP VIEW IF EXISTS `v_at_risk_students`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_at_risk_students` AS select `p`.`enrollment_id` AS `enrollment_id`,`e`.`student_id` AS `student_id`,`s`.`first_name` AS `first_name`,`s`.`last_name` AS `last_name`,`c`.`course_code` AS `course_code`,`c`.`course_name` AS `course_name`,`p`.`predicted_grade` AS `predicted_grade`,`p`.`confidence_score` AS `confidence_score`,`p`.`risk_level` AS `risk_level`,`p`.`prediction_date` AS `prediction_date` from ((((`predictions` `p` join `enrollments` `e` on((`p`.`enrollment_id` = `e`.`enrollment_id`))) join `students` `s` on((`e`.`student_id` = `s`.`student_id`))) join `course_offerings` `co` on((`e`.`offering_id` = `co`.`offering_id`))) join `courses` `c` on((`co`.`course_id` = `c`.`course_id`))) where ((`p`.`risk_level` in ('medium','high')) and `p`.`prediction_id` in (select max(`predictions`.`prediction_id`) from `predictions` group by `predictions`.`enrollment_id`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_current_enrollments`
--

/*!50001 DROP VIEW IF EXISTS `v_current_enrollments`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_current_enrollments` AS select `e`.`enrollment_id` AS `enrollment_id`,`e`.`student_id` AS `student_id`,`s`.`first_name` AS `first_name`,`s`.`last_name` AS `last_name`,`c`.`course_code` AS `course_code`,`c`.`course_name` AS `course_name`,`co`.`section_number` AS `section_number`,`f`.`first_name` AS `instructor_first`,`f`.`last_name` AS `instructor_last`,`at`.`term_name` AS `term_name` from (((((`enrollments` `e` join `students` `s` on((`e`.`student_id` = `s`.`student_id`))) join `course_offerings` `co` on((`e`.`offering_id` = `co`.`offering_id`))) join `courses` `c` on((`co`.`course_id` = `c`.`course_id`))) left join `faculty` `f` on((`co`.`faculty_id` = `f`.`faculty_id`))) join `academic_terms` `at` on((`co`.`term_id` = `at`.`term_id`))) where ((`e`.`enrollment_status` = 'enrolled') and (`at`.`is_current` = true)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-16  4:05:36
