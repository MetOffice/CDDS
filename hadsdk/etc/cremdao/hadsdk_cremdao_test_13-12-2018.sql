-- (C) British Crown Copyright 2016-2018, Met Office.
-- Please see LICENSE.rst for license details.

-- phpMyAdmin SQL Dump
-- version 4.8.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Dec 13, 2018 at 12:18 PM
-- Server version: 10.1.34-MariaDB
-- PHP Version: 5.6.37

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `hadsdk_cremdao_test`
--

-- --------------------------------------------------------

--
-- Table structure for table `at_audit_log`
--

CREATE TABLE IF NOT EXISTS `at_audit_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tablename` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tid` int(11) NOT NULL,
  `action` varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci,
  `datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `at_audit_log`
--

INSERT INTO `at_audit_log` (`id`, `tablename`, `tid`, `action`, `description`, `datetime`, `user`) VALUES
(1, 'rt_history', 336, 'insert', '{"status_value": "IP", "host": "exxar5h3", "requestid": 999, "process_status": "processing started", "uid": "1234", "notes": "", "upd_by": "test_crem", "pid": "23456", "process_type": "extract", "user": "hadel"}', '2017-05-23 14:28:15', 'test_crem'),
(2, 'rt_history', 336, 'update', '{"notes": " | Note 1 - found missing file at 1234", "upd_by": "test_crem", "process_status": ""}', '2017-05-23 14:28:15', 'test_crem'),
(3, 'rt_history', 336, 'update', '{"notes": " | Note 1 - found missing file at 1234 | Note 2 - found missing file at 5678", "upd_by": "test_crem", "process_status": "Update at milestone 1"}', '2017-05-23 14:28:15', 'test_crem'),
(4, 'rt_history', 336, 'update', '{"notes": " | Note 1 - found missing file at 1234 | Note 2 - found missing file at 5678 | Note 3 - found missing file at 90", "upd_by": "test_crem"}', '2017-05-23 14:28:15', 'test_crem'),
(5, 'pt_project', 1001, 'insert', '{"foo": "bar"}', '2017-05-23 14:28:15', 'piotrflorek'),
(6, 'rt_file_manifest', 2, 'insert', '{"create_date": "2017-11-01", "end_date": "2017-10-01", "start_date": "2007-10-01", "upd_by": "cremdao-test", "filename": "myTestFile", "transfer_date": "2017-12-01"}', '2017-05-23 14:28:15', 'cremdao-test'),
(7, 'rt_file_manifest', 2, 'update', '{"create_date": "2017-11-01", "end_date": "2017-10-01", "projectid": 999, "start_date": "2007-10-01", "upd_by": "cremdao-test", "filename": "myTestFile", "transfer_date": "2017-12-01", "requestid": 99}', '2017-05-23 14:28:15', 'cremdao-test'),
(8, 'pt_project', 10014, 'insert', '{"sname": "test", "dataowner": 1, "name": "Test Project", "programmeid": 10001, "upd_by": "pamv"}', '2017-05-23 14:28:15', 'pamv'),
(9, 'pt_project', 10014, 'update', '{"sname": "test", "name": "Foo", "dataowner": 1, "programmeid": 10001, "upd_date": "2017-05-23 15:28:15", "upd_by": "pamv"}', '2017-05-23 14:28:15', 'pamv'),
(10, 'pt_project', 10014, 'delete', NULL, '2017-05-23 14:28:15', 'NA'),
(11, 'rt_request', 10002, 'insert', '{"source_loc": "2", "name": "test_request_name", "input_format": "DF-PP", "request_date": "2017-05-23", "projectid": "5", "simulationid": "728", "process_loc": "2", "upd_by": "test-cremdao", "experimentid": "226", "owner_institute": "1"}', '2017-05-23 14:28:15', 'test-cremdao'),
(12, 'rt_requestdata', 10331, 'insert', '{"stream": "apa", "upd_by": "test-cremdao", "streamtype": "pp", "runid": 23, "simulationid": 728, "streaminit": 240, "start_date": "1980-01-01", "requestid": 10002}', '2017-05-23 14:28:15', 'test-cremdao'),
(13, 'rt_requestdata', 10332, 'insert', '{"stream": "apm", "end_date": "1990-01-30", "upd_by": "test-cremdao", "streamtype": "pp", "runid": 23, "simulationid": 728, "streaminit": 720, "requestid": 10002}', '2017-05-23 14:28:15', 'test-cremdao'),
(14, 'rt_requestdata', 10333, 'insert', '{"stream": "opm", "upd_by": "test-cremdao", "streamtype": "pp", "requestid": 10002, "simulationid": 728, "streaminit": 720, "runid": 23}', '2017-05-23 14:28:15', 'test-cremdao'),
(15, 'rt_history', 337, 'insert', '{"status_value": "IP", "host": "exxar5h3", "requestid": 999, "process_status": "processing started", "uid": "1234", "notes": "", "upd_by": "test_crem", "pid": "23456", "process_type": "extract", "user": "hadel"}', '2017-06-08 15:57:10', 'test_crem'),
(16, 'rt_history', 337, 'update', '{"notes": " | Note 1 - found missing file at 1234", "upd_by": "test_crem", "process_status": ""}', '2017-06-08 15:57:10', 'test_crem'),
(17, 'rt_history', 337, 'update', '{"notes": " | Note 1 - found missing file at 1234 | Note 2 - found missing file at 5678", "upd_by": "test_crem", "process_status": "Update at milestone 1"}', '2017-06-08 15:57:10', 'test_crem'),
(18, 'rt_history', 337, 'update', '{"notes": " | Note 1 - found missing file at 1234 | Note 2 - found missing file at 5678 | Note 3 - found missing file at 90", "upd_by": "test_crem"}', '2017-06-08 15:57:10', 'test_crem'),
(19, 'pt_project', 1001, 'insert', '{"foo": "bar"}', '2017-06-08 15:57:10', 'piotrflorek'),
(20, 'rt_file_manifest', 3, 'insert', '{"create_date": "2017-11-01", "end_date": "2017-10-01", "start_date": "2007-10-01", "upd_by": "cremdao-test", "filename": "myTestFile", "transfer_date": "2017-12-01"}', '2017-06-08 15:57:10', 'cremdao-test'),
(21, 'rt_file_manifest', 3, 'update', '{"create_date": "2017-11-01", "end_date": "2017-10-01", "projectid": 999, "start_date": "2007-10-01", "upd_by": "cremdao-test", "filename": "myTestFile", "transfer_date": "2017-12-01", "requestid": 99}', '2017-06-08 15:57:10', 'cremdao-test'),
(22, 'rt_request', 10003, 'insert', '{"source_loc": "2", "name": "test_request_name", "input_format": "DF-PP", "request_date": "2017-06-08", "projectid": "5", "simulationid": "728", "process_loc": "2", "upd_by": "test-cremdao", "experimentid": "226", "owner_institute": "1"}', '2017-06-08 15:57:10', 'test-cremdao'),
(23, 'rt_requestdata', 10334, 'insert', '{"stream": "apa", "upd_by": "test-cremdao", "streamtype": "pp", "runid": 23, "simulationid": 728, "streaminit": 240, "start_date": "1980-01-01", "requestid": 10003}', '2017-06-08 15:57:10', 'test-cremdao'),
(24, 'rt_requestdata', 10335, 'insert', '{"stream": "apm", "end_date": "1990-01-30", "upd_by": "test-cremdao", "streamtype": "pp", "runid": 23, "simulationid": 728, "streaminit": 720, "requestid": 10003}', '2017-06-08 15:57:10', 'test-cremdao'),
(25, 'rt_requestdata', 10336, 'insert', '{"stream": "opm", "upd_by": "test-cremdao", "streamtype": "pp", "requestid": 10003, "simulationid": 728, "streaminit": 720, "runid": 23}', '2017-06-08 15:57:10', 'test-cremdao'),
(356, 'rt_history', 335, 'insert', '{"status_value": "IP", "host": "exxar5h3", "requestid": 999, "process_status": "processing started", "uid": "1234", "notes": "", "upd_by": "test_crem", "pid": "23456", "process_type": "extract", "user": "hadel"}', '2017-06-08 16:03:29', 'test_crem'),
(357, 'rt_history', 335, 'update', '{"notes": " | Note 1 - found missing file at 1234", "upd_by": "test_crem", "process_status": ""}', '2017-06-08 16:03:29', 'test_crem'),
(358, 'rt_history', 335, 'update', '{"notes": " | Note 1 - found missing file at 1234 | Note 2 - found missing file at 5678", "upd_by": "test_crem", "process_status": "Update at milestone 1"}', '2017-06-08 16:03:29', 'test_crem'),
(359, 'rt_history', 335, 'update', '{"notes": " | Note 1 - found missing file at 1234 | Note 2 - found missing file at 5678 | Note 3 - found missing file at 90", "upd_by": "test_crem"}', '2017-06-08 16:03:29', 'test_crem'),
(360, 'pt_project', 1001, 'insert', '{"foo": "bar"}', '2017-06-08 16:03:29', 'piotrflorek'),
(361, 'rt_file_manifest', 1, 'insert', '{"create_date": "2017-11-01", "end_date": "2017-10-01", "start_date": "2007-10-01", "upd_by": "cremdao-test", "filename": "myTestFile", "transfer_date": "2017-12-01"}', '2017-06-08 16:03:29', 'cremdao-test'),
(362, 'rt_file_manifest', 1, 'update', '{"create_date": "2017-11-01", "end_date": "2017-10-01", "projectid": 999, "start_date": "2007-10-01", "upd_by": "cremdao-test", "filename": "myTestFile", "transfer_date": "2017-12-01", "requestid": 99}', '2017-06-08 16:03:29', 'cremdao-test'),
(363, 'pt_project', 10013, 'insert', '{"sname": "test", "dataowner": 1, "name": "Test Project", "programmeid": 10001, "upd_by": "pamv"}', '2017-06-08 16:03:29', 'pamv'),
(364, 'pt_project', 10013, 'update', '{"sname": "test", "name": "Foo", "dataowner": 1, "programmeid": 10001, "upd_date": "2017-06-08 17:03:29", "upd_by": "pamv"}', '2017-06-08 16:03:29', 'pamv'),
(365, 'pt_project', 10013, 'delete', NULL, '2017-06-08 16:03:29', 'NA'),
(366, 'rt_request', 10001, 'insert', '{"source_loc": "2", "name": "test_request_name", "input_format": "DF-PP", "request_date": "2017-06-08", "projectid": "5", "simulationid": "728", "process_loc": "2", "upd_by": "test-cremdao", "experimentid": "226", "owner_institute": "1"}', '2017-06-08 16:03:29', 'test-cremdao'),
(367, 'rt_requestdata', 10328, 'insert', '{"stream": "apa", "upd_by": "test-cremdao", "streamtype": "pp", "runid": 23, "simulationid": 728, "streaminit": 240, "start_date": "1980-01-01", "requestid": 10001}', '2017-06-08 16:03:29', 'test-cremdao'),
(368, 'rt_requestdata', 10329, 'insert', '{"stream": "apm", "end_date": "1990-01-30", "upd_by": "test-cremdao", "streamtype": "pp", "runid": 23, "simulationid": 728, "streaminit": 720, "requestid": 10001}', '2017-06-08 16:03:29', 'test-cremdao'),
(369, 'rt_requestdata', 10330, 'insert', '{"stream": "opm", "upd_by": "test-cremdao", "streamtype": "pp", "requestid": 10001, "simulationid": 728, "streaminit": 720, "runid": 23}', '2017-06-08 16:03:29', 'test-cremdao'),
(370, 'pt_project', 1001, 'insert', '{"foo": "bar"}', '2018-12-13 11:47:14', 'piotrflorek'),
(371, 'rt_history', 336, 'insert', '{"status_value": "IP", "host": "dummyhost", "requestid": 999, "process_status": "processing started", "uid": "1234", "notes": "", "upd_by": "test_crem", "pid": "23456", "process_type": "extract", "user": "hadel"}', '2018-12-13 11:47:14', 'test_crem'),
(372, 'rt_history', 336, 'update', '{"notes": " | Note 1 - found missing file at 1234", "upd_by": "test_crem", "process_status": ""}', '2018-12-13 11:47:14', 'test_crem'),
(373, 'rt_history', 336, 'update', '{"notes": " | Note 1 - found missing file at 1234 | Note 2 - found missing file at 5678", "upd_by": "test_crem", "process_status": "Update at milestone 1"}', '2018-12-13 11:47:14', 'test_crem'),
(374, 'rt_history', 336, 'update', '{"notes": " | Note 1 - found missing file at 1234 | Note 2 - found missing file at 5678 | Note 3 - found missing file at 90", "upd_by": "test_crem"}', '2018-12-13 11:47:14', 'test_crem'),
(375, 'rt_file_manifest', 10000, 'insert', '{"create_date": "2017-11-01", "end_date": "2017-10-01", "start_date": "2007-10-01", "upd_by": "cremdao-test", "variable": "dummy", "filename": "myTestFile", "transfer_date": "2017-12-01"}', '2018-12-13 11:47:14', 'cremdao-test'),
(376, 'rt_file_manifest', 10000, 'update', '{"create_date": "2017-11-01", "end_date": "2017-10-01", "projectid": 999, "start_date": "2007-10-01", "upd_by": "cremdao-test", "variable": "dummy", "filename": "myTestFile", "transfer_date": "2017-12-01", "requestid": 99}', '2018-12-13 11:47:14', 'cremdao-test'),
(377, 'pt_project', 10014, 'insert', '{"sname": "test", "dataowner": 1, "name": "Test Project", "programmeid": 10001, "upd_by": "pamv"}', '2018-12-13 11:47:14', 'pamv'),
(378, 'pt_project', 10014, 'update', '{"sname": "test", "name": "Foo", "dataowner": 1, "programmeid": 10001, "upd_date": "2018-12-13 11:47:14", "upd_by": "pamv"}', '2018-12-13 11:47:14', 'pamv'),
(379, 'pt_project', 10014, 'delete', NULL, '2018-12-13 11:47:14', 'NA'),
(380, 'rt_request', 10088, 'insert', '{"input_format": "DF-PP", "projectid": "5", "source_loc": "2", "upd_by": "test-cremdao", "name": "test_request_name", "owner_institute": "1", "package": "subset_1", "process_loc": "2", "experimentid": "226", "simulationid": "728", "request_date": "2018-12-13"}', '2018-12-13 11:47:14', 'test-cremdao'),
(381, 'rt_requestdata', 10331, 'insert', '{"stream": "apa", "upd_by": "test-cremdao", "streamtype": "pp", "runid": 10001, "simulationid": 728, "streaminit": 240, "start_date": "1980-01-01", "requestid": 10088}', '2018-12-13 11:47:14', 'test-cremdao'),
(382, 'rt_requestdata', 10332, 'insert', '{"stream": "apm", "end_date": "1990-01-30", "upd_by": "test-cremdao", "streamtype": "pp", "runid": 10001, "simulationid": 728, "streaminit": 720, "requestid": 10088}', '2018-12-13 11:47:14', 'test-cremdao'),
(383, 'rt_requestdata', 10333, 'insert', '{"stream": "opm", "upd_by": "test-cremdao", "streamtype": "pp", "requestid": 10088, "simulationid": 728, "streaminit": 720, "runid": 10001}', '2018-12-13 11:47:14', 'test-cremdao'),
(384, 'pt_project', 1001, 'insert', '{"foo": "bar"}', '2018-12-13 11:59:32', 'piotrflorek'),
(385, 'rt_history', 337, 'insert', '{"status_value": "IP", "host": "dummyhost", "requestid": 999, "process_status": "processing started", "uid": "1234", "notes": "", "upd_by": "test_crem", "pid": "23456", "process_type": "extract", "user": "hadel"}', '2018-12-13 11:59:32', 'test_crem'),
(386, 'rt_history', 337, 'update', '{"notes": " | Note 1 - found missing file at 1234", "upd_by": "test_crem", "process_status": ""}', '2018-12-13 11:59:32', 'test_crem'),
(387, 'rt_history', 337, 'update', '{"notes": " | Note 1 - found missing file at 1234 | Note 2 - found missing file at 5678", "upd_by": "test_crem", "process_status": "Update at milestone 1"}', '2018-12-13 11:59:32', 'test_crem'),
(388, 'rt_history', 337, 'update', '{"notes": " | Note 1 - found missing file at 1234 | Note 2 - found missing file at 5678 | Note 3 - found missing file at 90", "upd_by": "test_crem"}', '2018-12-13 11:59:32', 'test_crem'),
(389, 'rt_file_manifest', 10001, 'insert', '{"create_date": "2017-11-01", "end_date": "2017-10-01", "start_date": "2007-10-01", "upd_by": "cremdao-test", "variable": "dummy", "filename": "myTestFile", "transfer_date": "2017-12-01"}', '2018-12-13 11:59:32', 'cremdao-test'),
(390, 'rt_file_manifest', 10001, 'update', '{"create_date": "2017-11-01", "end_date": "2017-10-01", "projectid": 999, "start_date": "2007-10-01", "upd_by": "cremdao-test", "variable": "dummy", "filename": "myTestFile", "transfer_date": "2017-12-01", "requestid": 99}', '2018-12-13 11:59:32', 'cremdao-test'),
(391, 'pt_project', 10015, 'insert', '{"sname": "test", "dataowner": 1, "name": "Test Project", "programmeid": 10001, "upd_by": "pamv"}', '2018-12-13 11:59:32', 'pamv'),
(392, 'pt_project', 10015, 'update', '{"sname": "test", "name": "Foo", "dataowner": 1, "programmeid": 10001, "upd_date": "2018-12-13 11:59:32", "upd_by": "pamv"}', '2018-12-13 11:59:32', 'pamv');

-- --------------------------------------------------------

--
-- Table structure for table `at_data_exchange`
--

CREATE TABLE IF NOT EXISTS `at_data_exchange` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `operation_type` smallint(6) NOT NULL,
  `status` smallint(6) NOT NULL,
  `started` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `finished` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `user` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `at_data_log`
--

CREATE TABLE IF NOT EXISTS `at_data_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` smallint(6) NOT NULL,
  `datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `data_exchange_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `at_data_log_data_exchange_id` (`data_exchange_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cremadmin_audit`
--

CREATE TABLE IF NOT EXISTS `cremadmin_audit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `datetime` datetime NOT NULL,
  `ip` varchar(40) NOT NULL,
  `user` varchar(300) DEFAULT NULL,
  `table` varchar(300) DEFAULT NULL,
  `action` varchar(250) NOT NULL,
  `description` mediumtext,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Change log table';

-- --------------------------------------------------------

--
-- Table structure for table `cremadmin_uggroups`
--

CREATE TABLE IF NOT EXISTS `cremadmin_uggroups` (
  `GroupID` int(11) NOT NULL AUTO_INCREMENT,
  `Label` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`GroupID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='user permissions groups';

--
-- Dumping data for table `cremadmin_uggroups`
--

INSERT INTO `cremadmin_uggroups` (`GroupID`, `Label`) VALUES
(1, 'project'),
(2, 'process'),
(3, 'model'),
(4, 'reader');

-- --------------------------------------------------------

--
-- Table structure for table `cremadmin_ugmembers`
--

CREATE TABLE IF NOT EXISTS `cremadmin_ugmembers` (
  `UserName` varchar(300) NOT NULL,
  `GroupID` int(11) NOT NULL,
  PRIMARY KEY (`UserName`(50),`GroupID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='user group members';

--
-- Dumping data for table `cremadmin_ugmembers`
--

INSERT INTO `cremadmin_ugmembers` (`UserName`, `GroupID`) VALUES
('markelk', -1),
('modeluser', 3),
('pamv', 1),
('pamv', 2),
('pamv', 3),
('processuser', 2),
('projectuser', 1),
('readeruser', 4),
('markelk', 1),
('markelk', 2),
('markelk', 3),
('markelk', 4),
('emmah', 1),
('emmah', 2),
('emmah', 3),
('emmah', 4),
('emmah', -1),
('admin', -1),
('pamv', -1),
('pamv', 4),
('piotrf', 1),
('piotrf', 2),
('piotrf', 3),
('piotrf', 4),
('guest', 4);

-- --------------------------------------------------------

--
-- Table structure for table `cremadmin_ugrights`
--

CREATE TABLE IF NOT EXISTS `cremadmin_ugrights` (
  `TableName` varchar(300) NOT NULL,
  `GroupID` int(11) NOT NULL,
  `AccessMask` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`TableName`(50),`GroupID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='permissions';

--
-- Dumping data for table `cremadmin_ugrights`
--

INSERT INTO `cremadmin_ugrights` (`TableName`, `GroupID`, `AccessMask`) VALUES
('admin_members', -1, 'ADESPIM'),
('admin_rights', -1, 'ADESPIM'),
('admin_users', -1, 'ADESPIM'),
('ct_codelist', -1, 'ADESPIM'),
('ct_codelist', 1, 'SP'),
('ct_codelist', 2, 'SP'),
('ct_codelist', 3, 'SP'),
('ct_codes', -1, 'ADESPIM'),
('ct_codes', 1, 'SP'),
('ct_codes', 2, 'SP'),
('ct_codes', 3, 'SP'),
('ct_config', -1, 'ADESPIM'),
('ct_config', 1, 'SP'),
('ct_config', 2, 'SP'),
('ct_config', 3, 'SP'),
('ct_users', -1, 'ADESPIM'),
('gt_set', -3, 'S'),
('gt_set', -1, 'ADESPIM'),
('gt_set', 1, 'S'),
('gt_set', 2, 'S'),
('gt_set', 3, 'AEDS'),
('gt_set', 4, 'S'),
('gt_system', -3, 'S'),
('gt_system', -1, 'ADESPIM'),
('gt_system', 1, 'S'),
('gt_system', 2, 'S'),
('gt_system', 3, 'AEDS'),
('gt_system', 4, 'S'),
('mt_algorithm', -3, 'S'),
('mt_algorithm', -1, 'ADESPIM'),
('mt_algorithm', 1, 'S'),
('mt_algorithm', 2, 'S'),
('mt_algorithm', 3, 'AEDS'),
('mt_algorithm', 4, 'S'),
('mt_coupledmodel', -3, 'S'),
('mt_coupledmodel', -1, 'ADESPIM'),
('mt_coupledmodel', 1, 'AESP'),
('mt_coupledmodel', 2, 'S'),
('mt_coupledmodel', 3, 'AEDS'),
('mt_coupledmodel', 4, 'S'),
('mt_coupling', -3, 'S'),
('mt_coupling', -1, 'ADESPIM'),
('mt_coupling', 1, 'AES'),
('mt_coupling', 2, 'S'),
('mt_coupling', 3, 'AEDS'),
('mt_coupling', 4, 'S'),
('mt_domain', -3, 'S'),
('mt_domain', -1, 'ADESPIM'),
('mt_domain', 1, 'AESP'),
('mt_domain', 2, 'S'),
('mt_domain', 3, 'AEDS'),
('mt_domain', 4, 'S'),
('mt_model', -3, 'S'),
('mt_model', -1, 'ADESPIM'),
('mt_model', 1, 'AESP'),
('mt_model', 2, 'S'),
('mt_model', 3, 'AEDS'),
('mt_model', 4, 'S'),
('mt_process', -3, 'S'),
('mt_process', -1, 'ADESPIM'),
('mt_process', 1, 'S'),
('mt_process', 2, 'S'),
('mt_process', 3, 'AEDS'),
('mt_process', 4, 'S'),
('mt_processdetail', -3, 'S'),
('mt_processdetail', -1, 'ADESPIM'),
('mt_processdetail', 1, 'S'),
('mt_processdetail', 2, 'S'),
('mt_processdetail', 3, 'AEDS'),
('mt_processdetail', 4, 'S'),
('mt_property', -3, 'S'),
('mt_property', -1, 'ADESPIM'),
('mt_property', 1, 'ES'),
('mt_property', 2, 'S'),
('mt_property', 3, 'AEDS'),
('mt_property', 4, 'S'),
('mt_subprocess', -3, 'S'),
('mt_subprocess', -1, 'ADESPIM'),
('mt_subprocess', 1, 'S'),
('mt_subprocess', 2, 'S'),
('mt_subprocess', 3, 'AEDS'),
('mt_subprocess', 4, 'S'),
('pt_ancillary', -3, 'S'),
('pt_ancillary', -1, 'ADESPIM'),
('pt_ancillary', 1, 'AEDS'),
('pt_ancillary', 2, 'S'),
('pt_ancillary', 3, 'S'),
('pt_ancillary', 4, 'S'),
('pt_conformance', -3, 'S'),
('pt_conformance', -1, 'ADESPIM'),
('pt_conformance', 1, 'AEDSP'),
('pt_conformance', 2, 'SP'),
('pt_conformance', 3, 'SP'),
('pt_conformance', 4, 'S'),
('pt_domain', -3, 'S'),
('pt_domain', -1, 'ADESPIM'),
('pt_domain', 1, 'AES'),
('pt_domain', 2, 'S'),
('pt_domain', 3, 'S'),
('pt_domain', 4, 'S'),
('pt_experiment', -3, 'S'),
('pt_experiment', -1, 'ADESPIM'),
('pt_experiment', 1, 'AESP'),
('pt_experiment', 2, 'S'),
('pt_experiment', 3, 'S'),
('pt_experiment', 4, 'S'),
('pt_forcing', -3, 'S'),
('pt_forcing', -1, 'ADESPIM'),
('pt_forcing', 1, 'AEDS'),
('pt_forcing', 2, 'S'),
('pt_forcing', 3, 'S'),
('pt_forcing', 4, 'S'),
('pt_links', -3, 'S'),
('pt_links', -1, 'ADESPIM'),
('pt_links', 1, 'AESP'),
('pt_links', 2, 'S'),
('pt_links', 3, 'S'),
('pt_links', 4, 'S'),
('pt_modelrun', -3, 'S'),
('pt_modelrun', -1, 'ADESPIM'),
('pt_modelrun', 1, 'AES'),
('pt_modelrun', 2, 'S'),
('pt_modelrun', 3, 'S'),
('pt_modelrun', 4, 'S'),
('pt_programme', -3, 'S'),
('pt_programme', -1, 'ADESPIM'),
('pt_programme', 1, 'AES'),
('pt_programme', 2, 'S'),
('pt_programme', 3, 'S'),
('pt_programme', 4, 'S'),
('pt_project', -3, 'S'),
('pt_project', -1, 'ADESPIM'),
('pt_project', 1, 'AESP'),
('pt_project', 2, 'S'),
('pt_project', 3, 'S'),
('pt_project', 4, 'S'),
('pt_requirement', -3, 'S'),
('pt_requirement', -1, 'ADESPIM'),
('pt_requirement', 1, 'AESP'),
('pt_requirement', 2, 'SP'),
('pt_requirement', 3, 'SP'),
('pt_requirement', 4, 'S'),
('pt_simulation', -3, 'S'),
('pt_simulation', -1, 'ADESPIM'),
('pt_simulation', 1, 'AESP'),
('pt_simulation', 2, 'S'),
('pt_simulation', 3, 'S'),
('pt_simulation', 4, 'S'),
('rt_history', -3, 'S'),
('rt_history', -1, 'ADESPIM'),
('rt_history', 1, 'S'),
('rt_history', 2, 'S'),
('rt_history', 3, 'S'),
('rt_history', 4, 'S'),
('rt_process', -3, 'S'),
('rt_process', -1, 'ADESPIM'),
('rt_process', 1, 'S'),
('rt_process', 2, 'S'),
('rt_process', 3, 'S'),
('rt_request', -3, 'S'),
('rt_request', -1, 'ADESPIM'),
('rt_request', 1, 'AES'),
('rt_request', 2, 'AEDS'),
('rt_request', 3, 'S'),
('rt_request', 4, 'S'),
('rt_requestdata', -3, 'S'),
('rt_requestdata', -1, 'ADESPIM'),
('rt_requestdata', 1, 'S'),
('rt_requestdata', 2, 'AEDS'),
('rt_requestdata', 3, 'S'),
('rt_requestdata', 4, 'S'),
('rt_status', -3, 'S'),
('rt_status', -1, 'ADESPIM'),
('rt_status', 1, 'S'),
('rt_status', 2, 'ES'),
('rt_status', 3, 'S'),
('rt_status', 4, 'S'),
('ut_comments', -3, 'S'),
('ut_comments', -1, 'ADESPIM'),
('ut_comments', 1, 'AESP'),
('ut_comments', 2, 'AEDS'),
('ut_comments', 3, 'AES'),
('ut_comments', 4, 'S'),
('ut_commontxt', -1, 'ADESPIM'),
('ut_institute', -3, 'S'),
('ut_institute', -1, 'ADESPIM'),
('ut_institute', 1, 'AESP'),
('ut_institute', 2, 'AESP'),
('ut_institute', 3, 'AESP'),
('ut_institute', 4, 'S'),
('ut_locations', -3, 'S'),
('ut_locations', -1, 'ADESPIM'),
('ut_locations', 1, 'AES'),
('ut_locations', 2, 'S'),
('ut_locations', 3, 'S'),
('ut_locations', 4, 'S'),
('ut_person', -3, 'S'),
('ut_person', -1, 'ADESPIM'),
('ut_person', 1, 'AESP'),
('ut_person', 2, 'AESP'),
('ut_person', 3, 'SP'),
('ut_person', 4, 'S'),
('ut_reference', -3, 'S'),
('ut_reference', -1, 'ADESPIM'),
('ut_reference', 1, 'AESP'),
('ut_reference', 2, 'AES'),
('ut_reference', 3, 'AES'),
('ut_reference', 4, 'S'),
('ut_referencelist', -3, 'S'),
('ut_referencelist', -1, 'ADESPIM'),
('ut_referencelist', 1, 'ASP'),
('ut_referencelist', 2, 'S'),
('ut_referencelist', 3, 'ADS'),
('ut_referencelist', 4, 'S'),
('ut_tickets', -3, 'S'),
('ut_tickets', -1, 'ADESPIM'),
('ut_tickets', 1, 'AESP'),
('ut_tickets', 2, 'AESP'),
('ut_tickets', 3, 'AESP'),
('ut_tickets', 4, 'S'),
('gt_grid', -1, 'AEDSPI'),
('gt_datum', -1, 'AEDSPI'),
('gt_coordaxis', -1, 'AEDSPI'),
('pt_region', -1, 'AEDSPI'),
('ut_quality', -1, 'AEDSPI'),
('ut_qualitydetail', -1, 'AEDSPI'),
('mt_topic', -1, 'AESP'),
('mt_topic_sub', -1, 'AESP'),
('mt_detail', -1, 'ADESPIM'),
('ut_contactrole', -1, 'ADESPIM'),
('pt_eratta', -1, 'ADESPIM'),
('mt_propenum', -1, 'AES'),
('mt_subtopic', -1, 'ESP'),
('ut_contactrole', 1, 'AES'),
('mt_propenum', 1, 'S'),
('mt_subtopic', 1, 'ESP'),
('mt_topic', 1, 'ESP'),
('pt_reqt_attribute', -1, 'SP'),
('pt_reqt_attribute', 4, 'S'),
('ct_codelist', 4, 'S'),
('ut_contactrole', 4, 'S'),
('rt_process', 4, 'S'),
('ct_codes', 4, 'S'),
('mt_propenum', 4, 'S'),
('mt_subtopic', 4, 'S'),
('mt_topic', 4, 'S'),
('mt_grid', -1, 'AEDS');

-- --------------------------------------------------------

--
-- Table structure for table `ct_codelist`
--

CREATE TABLE IF NOT EXISTS `ct_codelist` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for code value',
  `codetype` varchar(30) NOT NULL COMMENT ' codetype (from ct_codes)',
  `project` varchar(100) DEFAULT NULL COMMENT 'list of specialisations that this code list is relevant to',
  `value` varchar(200) NOT NULL COMMENT 'value of code',
  `label` varchar(200) NOT NULL COMMENT 'label for code (appears in forms etc.)',
  `default` tinyint(1) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL COMMENT 'order in which to present codes',
  `upd_by` char(20) NOT NULL COMMENT 'person/process responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='values for each code type - may be project or expt specific';

--
-- Dumping data for table `ct_codelist`
--

INSERT INTO `ct_codelist` (`id`, `codetype`, `project`, `value`, `label`, `default`, `rank`, `upd_by`, `upd_date`) VALUES
(1, 'calendar_type', NULL, '360_day', '360 day', 1, 5, 'marke', '2016-09-30 13:15:36'),
(2, 'calendar_type', NULL, '365_day', '365 day', 0, 10, 'marke', '2016-09-30 13:15:36'),
(3, 'calendar_type', NULL, '366_day', '366 day', 0, 15, 'marke', '2016-09-30 13:15:36'),
(4, 'calendar_type', NULL, 'proleptic_gregorian', 'extended Gregorian', 0, 20, 'marke', '2016-09-30 13:15:36'),
(5, 'calendar_type', NULL, 'gregorian', 'mixed Gregorian/Julian', 0, 25, 'marke', '2016-09-30 13:15:36'),
(6, 'calendar_type', NULL, 'noleap', 'gregorian - no leap years', 0, 30, 'marke', '2016-09-30 13:15:36'),
(7, 'calendar_type', NULL, 'allleap', 'gregorian - all leap years', 0, 35, 'marke', '2016-09-30 13:15:36'),
(8, 'calendar_type', NULL, 'julian', 'Julian calendar', 0, 40, 'marke', '2016-09-30 13:15:36'),
(9, 'calendar_type', NULL, 'none', 'perpetual time axis', 0, 45, 'marke', '2016-09-30 13:15:36'),
(10, 'cardinality', NULL, '0.1', 'zero or one selections permitted', 0, 1, 'marke', '2016-09-30 13:15:36'),
(11, 'cardinality', NULL, '0.N', 'zero or many selections permitted', 0, 2, 'marke', '2016-09-30 13:15:36'),
(12, 'cardinality', NULL, '1.1', 'one and only one selection required', 0, 3, 'marke', '2016-09-30 13:15:36'),
(13, 'cardinality', NULL, '1.N', 'one or many selections required', 0, 4, 'marke', '2016-09-30 13:15:36'),
(14, 'coupling_method', NULL, 'OASIS', 'OASIS coupler', 0, 10, 'marke', '2016-09-30 13:15:36'),
(15, 'coupling_method', NULL, 'OASIS3-MCT', 'OASIS - MCT variant', 0, 15, 'marke', '2016-09-30 13:15:36'),
(16, 'coupling_method', NULL, 'ESMF', 'Vanilla ESM Framework', 0, 20, 'marke', '2016-09-30 13:15:36'),
(17, 'coupling_method', NULL, 'NUOPC', 'NUOPC coupler', 0, 25, 'marke', '2016-09-30 13:15:36'),
(18, 'coupling_method', NULL, 'bespoke', 'customised coupler', 0, 30, 'marke', '2016-09-30 13:15:36'),
(19, 'coupling_method', NULL, 'unknown', 'not known', 0, 35, 'marke', '2016-09-30 13:15:36'),
(20, 'coupling_method', NULL, 'none', 'no coupler used', 0, 40, 'marke', '2016-09-30 13:15:36'),
(21, 'conformance_type', NULL, 'conformed', 'conformed', 1, 5, 'marke', '2016-09-30 13:15:36'),
(22, 'conformance_type', NULL, 'partially conformed', 'partially conformed', 0, 10, 'marke', '2016-09-30 13:15:36'),
(23, 'conformance_type', NULL, 'not conformed', 'not conformed', 0, 15, 'marke', '2016-09-30 13:15:36'),
(24, 'conformance_type', NULL, 'not applicable', 'not applicable', 0, 20, 'marke', '2016-09-30 13:15:36'),
(25, 'delivery_type', NULL, 'MASS', 'MASS', 1, 1, 'marke', '2016-09-30 13:15:36'),
(26, 'delivery_type', NULL, 'ftp', 'ftp', 0, 5, 'marke', '2016-09-30 13:15:36'),
(27, 'delivery_type', NULL, 'media', 'media', 0, 10, 'marke', '2016-09-30 13:15:36'),
(28, 'ensemble_type', NULL, 'perturbed physics', 'nonedifferent physics', 0, 5, 'marke', '2016-09-30 13:15:36'),
(29, 'ensemble_type', NULL, 'initialisation method', 'different initialisation', 0, 10, 'marke', '2016-09-30 13:15:36'),
(30, 'ensemble_type', NULL, 'realisation', 'different initial conditions', 0, 15, 'marke', '2016-09-30 13:15:36'),
(31, 'ensemble_type', NULL, 'start date', 'different start dates', 0, 20, 'marke', '2016-09-30 13:15:36'),
(32, 'ensemble_type', NULL, 'forced', 'different forcing data', 0, 25, 'marke', '2016-09-30 13:15:36'),
(33, 'ensemble_type', NULL, 'resolution', 'different resolution', 0, 30, 'marke', '2016-09-30 13:15:36'),
(34, 'ensemble_type', NULL, 'driven', 'different driving models', 0, 35, 'marke', '2016-09-30 13:15:36'),
(35, 'experiment_relation', NULL, 'control_for', 'control for experiment', 0, 5, 'marke', '2016-09-30 13:15:36'),
(36, 'experiment_relation', NULL, 'initialisation_for', 'initialistion for experiment', 0, 10, 'marke', '2016-09-30 13:15:36'),
(37, 'experiment_relation', NULL, 'provides_constraints', 'provides constraints ', 0, 15, 'marke', '2016-09-30 13:15:36'),
(38, 'experiment_relation', NULL, 'is_sibling', 'is sibling of experiment', 0, 20, 'marke', '2016-09-30 13:15:36'),
(39, 'forcing_type', NULL, 'historical', 'historical (actual state)', 0, 5, 'marke', '2016-09-30 13:15:36'),
(40, 'forcing_type', NULL, 'idealised', 'idealised (e.g. 1%CO2)', 0, 5, 'marke', '2016-09-30 13:15:36'),
(41, 'forcing_type', NULL, 'scenario', 'scenario (future state)', 0, 5, 'marke', '2016-09-30 13:15:36'),
(42, 'forcing_type', NULL, 'driven', 'driven (anothersimulation)', 0, 5, 'marke', '2016-09-30 13:15:36'),
(43, 'frequency_type', NULL, 'yr', 'yearly', 0, 5, 'marke', '2016-09-30 13:15:36'),
(44, 'frequency_type', NULL, 'mon', 'monthly', 0, 10, 'marke', '2016-09-30 13:15:36'),
(45, 'frequency_type', NULL, 'day', 'daily', 0, 15, 'marke', '2016-09-30 13:15:36'),
(46, 'frequency_type', NULL, '6hr', '6 hourly', 0, 20, 'marke', '2016-09-30 13:15:36'),
(47, 'frequency_type', NULL, '3hr', '3 hourly', 0, 25, 'marke', '2016-09-30 13:15:36'),
(48, 'frequency_type', NULL, '1hr', '1 hourly', 0, 30, 'marke', '2016-09-30 13:15:36'),
(49, 'frequency_type', NULL, 'subhr', 'sub hourly', 0, 35, 'marke', '2016-09-30 13:15:36'),
(50, 'frequency_type', NULL, 'monClim', 'climate monthly mean', 0, 40, 'marke', '2016-09-30 13:15:36'),
(51, 'frequency_type', NULL, 'fx', 'fixed - time independent', 0, 45, 'marke', '2016-09-30 13:15:36'),
(52, 'link_category', NULL, 'project', 'external - project', 0, 1, 'marke', '2016-09-30 13:15:36'),
(53, 'link_category', NULL, 'general', 'external - general', 0, 2, 'marke', '2016-09-30 13:15:36'),
(54, 'link_category', NULL, 'internal', 'internal', 0, 3, 'marke', '2016-09-30 13:15:36'),
(55, 'model_type', '', 'AER', 'AER', 0, 15, 'admin', '2017-03-08 11:22:01'),
(56, 'model_type', '', 'AGCM', 'Atmosphere GCM', 0, 4, 'admin', '2017-03-08 11:22:00'),
(57, 'model_type', '', 'AOGCM', 'Atmosphere Ocean GCM', 0, 2, 'admin', '2017-03-08 11:22:00'),
(58, 'model_type', '', 'BGC', 'BGC', 0, 20, 'admin', '2017-03-08 11:22:01'),
(59, 'model_type', '', 'CHEM', 'Atm Chemistry Model', 0, 25, 'admin', '2017-03-08 11:22:01'),
(63, 'model_type', '', 'ISM', 'Ice Sheet Model', 0, 45, 'admin', '2017-03-08 11:22:01'),
(64, 'model_type', '', 'LAND', 'Land Model', 0, 50, 'admin', '2017-03-08 11:22:00'),
(65, 'model_type', '', 'OGCM', 'Ocean GCM', 0, 6, 'admin', '2017-03-08 11:22:00'),
(66, 'model_type', '', 'RAD', 'Radiation Model', 0, 60, 'admin', '2017-03-08 11:22:00'),
(68, 'model_type', '', 'SLAB', 'Ocean Slab Model', 0, 70, 'admin', '2017-03-08 11:22:01'),
(69, 'null_reason', NULL, 'nil:inapplicable', 'not applicable', 1, 5, 'marke', '2016-09-30 13:15:36'),
(70, 'null_reason', NULL, 'nil:template', 'answer later', 0, 10, 'marke', '2016-09-30 13:15:36'),
(71, 'null_reason', NULL, 'nil:unknown', 'unknown - can find out', 0, 15, 'marke', '2016-09-30 13:15:36'),
(72, 'null_reason', NULL, 'nil:missing', 'unknown - may not exist', 0, 20, 'marke', '2016-09-30 13:15:36'),
(73, 'null_reason', NULL, 'nil:withheld', 'answer withheld', 0, 25, 'marke', '2016-09-30 13:15:36'),
(74, 'party_role', NULL, 'principal investigator', 'principal investigator', 0, 5, 'marke', '2016-09-30 13:15:36'),
(75, 'party_role', NULL, 'originator', 'originator', 0, 10, 'marke', '2016-09-30 13:15:36'),
(76, 'party_role', NULL, 'author', 'author', 0, 15, 'marke', '2016-09-30 13:15:36'),
(77, 'party_role', NULL, 'collaborator', 'collaborator', 0, 20, 'marke', '2016-09-30 13:15:36'),
(78, 'party_role', NULL, 'publisher', 'publisher', 0, 25, 'marke', '2016-09-30 13:15:36'),
(79, 'party_role', NULL, 'owner', 'owner', 0, 30, 'marke', '2016-09-30 13:15:36'),
(80, 'party_role', NULL, 'processor', 'processor', 0, 35, 'marke', '2016-09-30 13:15:36'),
(81, 'party_role', NULL, 'distributor', 'distributor', 0, 40, 'marke', '2016-09-30 13:15:36'),
(82, 'party_role', NULL, 'sponsor', 'sponsor / funder', 0, 45, 'marke', '2016-09-30 13:15:36'),
(83, 'party_role', NULL, 'user', 'user', 0, 50, 'marke', '2016-09-30 13:15:36'),
(84, 'party_role', NULL, 'point of contact', 'point of contact', 0, 55, 'marke', '2016-09-30 13:15:36'),
(85, 'party_role', NULL, 'resource provider', 'resource provider', 0, 60, 'marke', '2016-09-30 13:15:36'),
(86, 'party_role', NULL, 'custodian', 'custodian', 0, 65, 'marke', '2016-09-30 13:15:36'),
(87, 'party_role', NULL, 'metadata_reviewer', 'metadata reviewer', 0, 70, 'marke', '2016-09-30 13:15:36'),
(88, 'party_role', NULL, 'metadata_author', 'metadata author', 0, 75, 'marke', '2016-09-30 13:15:36'),
(89, 'outputdata_format', NULL, 'netcdf_4', 'netCDF4', 1, 1, 'marke', '2016-09-30 13:15:36'),
(90, 'outputdata_format', NULL, 'netcdf_3', 'netCDF3', 0, 5, 'marke', '2016-09-30 13:15:36'),
(91, 'parent_type', NULL, 'n/a', 'not applicable', 0, 1, 'marke', '2016-09-30 13:15:36'),
(92, 'parent_type', NULL, 'continuation', 'continuation', 0, 2, 'marke', '2016-09-30 13:15:36'),
(93, 'parent_type', NULL, 'parallel', 'parallel', 0, 3, 'marke', '2016-09-30 13:15:36'),
(94, 'process_status', NULL, 'NS', 'not started', 0, 5, 'marke', '2016-09-30 13:15:36'),
(95, 'process_status', NULL, 'IP', 'in progress', 0, 10, 'marke', '2016-09-30 13:15:36'),
(96, 'process_status', NULL, 'SP', 'suspended', 0, 15, 'marke', '2016-09-30 13:15:36'),
(97, 'process_status', NULL, 'CF', 'failed', 0, 20, 'marke', '2016-09-30 13:15:36'),
(98, 'process_status', NULL, 'CQ', 'complete with issues', 0, 25, 'marke', '2016-09-30 13:15:36'),
(99, 'process_status', NULL, 'CS', 'complete', 0, 30, 'marke', '2016-09-30 13:15:36'),
(100, 'process_type', '', 'extract', 'extract', 0, 5, 'admin', '2017-02-22 17:02:46'),
(101, 'process_type', '', 'config', 'config', 0, 10, 'admin', '2017-02-22 17:02:46'),
(102, 'process_type', '', 'transform', 'transform', 0, 15, 'admin', '2017-02-22 17:02:46'),
(103, 'process_type', '', 'verify', 'QC verification', 0, 20, 'admin', '2017-02-22 17:02:47'),
(104, 'process_type', '', 'archive', 'archive/transfer', 0, 25, 'admin', '2017-02-22 17:02:46'),
(105, 'process_type', '', 'teardown', 'teardown', 0, 30, 'admin', '2017-02-22 17:02:46'),
(106, 'programming_language', NULL, 'fortran', 'Fortran', 0, 5, 'marke', '2016-09-30 13:15:36'),
(107, 'programming_language', NULL, 'C', 'C', 0, 10, 'marke', '2016-09-30 13:15:36'),
(108, 'programming_language', NULL, 'C++', 'C++', 0, 15, 'marke', '2016-09-30 13:15:36'),
(109, 'programming_language', NULL, 'python', 'python', 0, 20, 'marke', '2016-09-30 13:15:36'),
(110, 'realm_type', NULL, 'atmos', 'atmosphere', 0, 5, 'marke', '2016-09-30 13:15:36'),
(111, 'realm_type', NULL, 'ocean', 'ocean', 0, 10, 'marke', '2016-09-30 13:15:36'),
(112, 'realm_type', NULL, 'land', 'land', 0, 15, 'marke', '2016-09-30 13:15:36'),
(113, 'realm_type', NULL, 'landIce', 'land ice', 0, 20, 'marke', '2016-09-30 13:15:36'),
(114, 'realm_type', NULL, 'seaIce', 'sea ice', 0, 25, 'marke', '2016-09-30 13:15:36'),
(115, 'realm_type', NULL, 'aerosol', 'aerosol', 0, 30, 'marke', '2016-09-30 13:15:36'),
(116, 'realm_type', NULL, 'atmosChem', 'atmospheric chemistry', 0, 35, 'marke', '2016-09-30 13:15:36'),
(117, 'realm_type', NULL, 'ocnBgchem', 'ocean biogeochemistry', 0, 40, 'marke', '2016-09-30 13:15:36'),
(118, 'reference_context', NULL, 'reference', 'bibliographic reference', 0, 5, 'marke', '2016-09-30 13:15:36'),
(119, 'reference_context', NULL, 'citation', 'citation to be used', 0, 10, 'marke', '2016-09-30 13:15:36'),
(120, 'reference_context', NULL, 'internal', 'internal reference', 0, 15, 'marke', '2016-09-30 13:15:36'),
(122, 'spatial_average', NULL, 'zonalavg', 'zonal average', 0, 5, 'marke', '2016-09-30 13:15:36'),
(123, 'spatial_average', NULL, 'lnd-zonalavg', 'land zonal average', 0, 10, 'marke', '2016-09-30 13:15:36'),
(124, 'spatial_average', NULL, 'ocn-zonalavg', 'ocean zonal average', 0, 15, 'marke', '2016-09-30 13:15:36'),
(125, 'spatial_average', NULL, 'areaavg', 'regional average', 0, 20, 'marke', '2016-09-30 13:15:36'),
(126, 'spatial_average', NULL, 'lnd-areaavg', 'land regional average', 0, 25, 'marke', '2016-09-30 13:15:36'),
(127, 'spatial_average', NULL, 'ocn-areaavg', 'ocean regional average', 0, 30, 'marke', '2016-09-30 13:15:36'),
(128, 'specialisations', NULL, 'cmip6', 'CMIP6 project', 1, 5, 'marke', '2016-09-30 13:15:36'),
(129, 'specialisations', NULL, 'cmip5', 'CMIP5 project', 0, 10, 'marke', '2016-09-30 13:15:36'),
(130, 'stream_type', NULL, 'pp', 'pp format', 1, 5, 'marke', '2016-09-30 13:15:36'),
(131, 'stream_type', NULL, 'nc', 'nc format', 0, 10, 'marke', '2016-09-30 13:15:36'),
(132, 'time_units', NULL, 'years', 'years', 0, 5, 'marke', '2016-09-30 13:15:36'),
(133, 'time_units', NULL, 'months', 'months', 0, 10, 'marke', '2016-09-30 13:15:36'),
(134, 'time_units', NULL, 'days', 'days (86400 secs)', 0, 15, 'marke', '2016-09-30 13:15:36'),
(135, 'time_units', NULL, 'seconds', 'seconds', 0, 20, 'marke', '2016-09-30 13:15:36'),
(136, 'topic_type', NULL, 'process', 'science process', 1, 5, 'marke', '2016-09-30 13:15:36'),
(137, 'topic_type', NULL, 'subprocess', 'science subprocess', 0, 10, 'marke', '2016-09-30 13:15:36'),
(138, 'topic_type', NULL, 'key', 'key properties', 0, 15, 'marke', '2016-09-30 13:15:36'),
(139, 'topic_type', NULL, 'grid', 'grid properties', 0, 20, 'marke', '2016-09-30 13:15:36'),
(140, 'topic_type', NULL, 'core', 'core properties', 0, 25, 'marke', '2016-09-30 13:15:36'),
(141, 'topic_type', NULL, 'extent', 'extent', 0, 30, 'marke', '2016-09-30 13:15:36'),
(142, 'topic_type', NULL, 'resolution', 'resolution', 0, 35, 'marke', '2016-09-30 13:15:36'),
(143, 'topic_type', NULL, 'conservationproperties', 'conservation properties', 0, 40, 'marke', '2016-09-30 13:15:36'),
(144, 'topic_type', NULL, 'tuning', 'tuning', 0, 45, 'marke', '2016-09-30 13:15:36'),
(145, 'topic_type', NULL, 'discretisation', 'discretisation', 0, 50, 'marke', '2016-09-30 13:15:36'),
(146, 'topic_type', NULL, 'process', 'science process', 1, 5, 'marke', '2016-09-30 13:15:36'),
(147, 'topic_type', NULL, 'subprocess', 'science subprocess', 0, 10, 'marke', '2016-09-30 13:15:36'),
(148, 'topic_type', NULL, 'key', 'key properties', 0, 15, 'marke', '2016-09-30 13:15:36'),
(149, 'topic_type', NULL, 'grid', 'grid properties', 0, 20, 'marke', '2016-09-30 13:15:36'),
(150, 'units', NULL, 'W.m-2', 'Watts per square metre', 0, NULL, 'marke', '2016-09-30 13:15:36'),
(151, 'units', NULL, 'K', 'Kelvin', 0, NULL, 'marke', '2016-09-30 13:15:36'),
(152, 'visible_code', NULL, 'TT', 'internal/external', 1, 1, 'marke', '2016-09-30 13:15:36'),
(153, 'visible_code', NULL, 'TF', 'internal only', 0, 2, 'marke', '2016-09-30 13:15:36'),
(154, 'visible_code', NULL, 'FT', 'external only', 0, 3, 'marke', '2016-09-30 13:15:36'),
(155, 'visible_code', NULL, 'FF', 'not visible', 0, 4, 'marke', '2016-09-30 13:15:36'),
(156, 'conformance_method', NULL, 'model_configuration', 'model configuration', NULL, 5, 'marke', '2016-11-09 15:03:50'),
(157, 'conformance_method', NULL, 'forcing_data', 'forcing data', NULL, 10, 'marke', '2016-11-09 15:03:50'),
(158, 'conformance_method', NULL, 'TBC', 'to be completed', NULL, 15, 'marke', '2016-11-09 15:04:15'),
(161, 'coupling_method', NULL, 'integrated', 'integrated in model executable', NULL, 32, 'marke', '2016-11-09 15:28:08'),
(162, 'reference_type', '', 'peer reviewed article', 'peer reviewed article', 1, 1, 'admin', '2016-12-12 17:15:26'),
(163, 'reference_type', '', 'internal report', 'internal report', 0, 10, 'admin', '2016-12-12 17:15:26'),
(164, 'reference_type', '', 'other', 'other', 0, 15, 'admin', '2016-12-12 17:15:26'),
(165, 'reference_type', '', 'book', 'book', 0, 5, 'admin', '2016-12-12 17:15:27'),
(166, 'ticket_severity', '', 'high', 'high', 0, 5, 'admin', '2016-12-13 16:53:52'),
(167, 'ticket_severity', '', 'normal', 'normal', 1, 1, 'admin', '2016-12-13 16:53:52'),
(168, 'ticket_severity', '', 'low', 'low', 0, 10, 'admin', '2016-12-13 16:53:52'),
(169, 'ticket_classification', '', 'software', 'software', 0, 5, 'admin', '2016-12-13 17:00:05'),
(170, 'ticket_classification', '', 'model data', 'model data', 0, 10, 'admin', '2016-12-13 17:00:05'),
(171, 'ticket_classification', '', 'process', 'process', 0, 1, 'admin', '2016-12-13 17:00:06'),
(172, 'ticket_classification', '', 'metadata', 'metadata', 0, 15, 'admin', '2016-12-13 17:00:06'),
(173, 'ticket_status', '', 'new', 'new', 0, 1, 'admin', '2016-12-13 17:01:46'),
(174, 'ticket_status', '', 'in progress', 'in progress', 0, 5, 'admin', '2016-12-13 17:01:46'),
(175, 'ticket_status', '', 'closed', 'closed', 0, 15, 'admin', '2016-12-13 17:01:47'),
(176, 'ticket_status', '', 'resolved', 'resolved', 0, 10, 'admin', '2016-12-13 17:01:47'),
(177, 'ticket_status', '', 'reopened', 'reopened', 0, 20, 'admin', '2016-12-13 17:01:47');

-- --------------------------------------------------------

--
-- Table structure for table `ct_codes`
--

CREATE TABLE IF NOT EXISTS `ct_codes` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for code type',
  `codetype` char(30) NOT NULL COMMENT 'group name for codes of this type',
  `desc` varchar(100) DEFAULT NULL COMMENT 'description for this set of codes',
  `proj_spec` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'flag to indicate if codes of this type are project specific',
  `source` varchar(40) DEFAULT 'MOHC' COMMENT 'source (owner) of code list',
  `source_ver` varchar(20) DEFAULT NULL COMMENT 'latest version used',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` char(20) NOT NULL COMMENT 'person/process responsible for last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='code types - may be project or expt speci';

--
-- Dumping data for table `ct_codes`
--

INSERT INTO `ct_codes` (`id`, `codetype`, `desc`, `proj_spec`, `source`, `source_ver`, `upd_date`, `upd_by`) VALUES
(1, 'calendar_type', 'calendar definitions', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(2, 'cardinality', 'cardinality options', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(3, 'conformance_type', 'conformance status', 0, 'MOHC', NULL, '2017-02-22 12:46:32', 'admin'),
(4, 'coupling_method', 'model coupling interface type', 0, 'ESDOC', 'CIM2', '2018-11-16 10:30:06', 'marke'),
(5, 'delivery_type', 'delivery methods for data', 0, 'MOHC', NULL, '2018-11-16 10:31:59', 'marke'),
(6, 'ensemble_type', 'ensemble classification', 0, 'ESDOC', 'CIM2', '2018-11-16 10:32:10', 'marke'),
(7, 'experiment_relation', 'relationships between experiments', 0, 'ESDOC', 'CIM2', '2018-11-16 10:32:25', 'marke'),
(8, 'forcing_type', 'types of forcing agent', 0, 'ESDOC', 'CIM2', '2018-11-16 10:32:33', 'marke'),
(9, 'frequency_type', 'data frequency types', 0, 'CMIP6_frequency', '3.2.4', '2018-11-16 10:34:40', 'marke'),
(10, 'link_category', 'categories for project links', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(11, 'model_type', 'code for model/sub-model type', 0, 'CMIP6_source_type', '3.2.4', '2018-11-16 10:39:08', 'marke'),
(12, 'null_reason', 'reasons for not providing value for science property', 0, 'ESDOC', 'CIM2', '2018-11-16 10:32:50', 'marke'),
(13, 'outputdata_format', 'output data format', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(14, 'parent_type', 'branching methods', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(15, 'party_role', 'role for a responsible party', 0, 'ESDOC', 'CIM2', '2018-11-16 10:33:05', 'marke'),
(16, 'process_status', 'process state', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(17, 'process_type', 'CDDS process types', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(18, 'programming_language', 'programming languages', 0, 'ESDOC', 'CIM2', '2018-11-16 10:33:21', 'marke'),
(19, 'realm_type', 'codes for modelling realms', 0, 'CMIP6_realm', '3.2.4', '2018-11-16 10:35:25', 'marke'),
(20, 'reference_context', 'why reference was cited', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(21, 'requirement_type', 'requirement category', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(22, 'spatial_average', 'spatial averaging operators', 0, 'ESDOC', 'CIM2', '2018-11-16 10:33:36', 'marke'),
(23, 'specialisations', 'CIM project specific specialisations', 0, 'CMIP6_mip_era', '3.2.4', '2018-11-16 10:35:48', 'marke'),
(24, 'stream_type', 'data type for a run data stream', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(25, 'time_units', 'time units', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(26, 'topic_type', 'codes for groups of model properties', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(27, 'units', 'list of valid units', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(28, 'visible_code', 'defines where record is visible', 0, 'MOHC', NULL, '2016-09-30 13:17:11', 'marke'),
(29, 'conformance_method', 'method used to achieve conformance', 0, 'MOHC', NULL, '2016-11-09 14:59:23', 'marke'),
(30, 'reference_type', 'generic types of reference', 0, 'MOHC', NULL, '2016-12-12 17:13:13', 'admin'),
(31, 'ticket_classification', 'classification codes for tickets', 0, 'MOHC', NULL, '2016-12-13 16:51:12', 'admin'),
(32, 'ticket_severity', 'severity codes for tickets', 0, 'MOHC', NULL, '2016-12-13 16:51:49', 'admin'),
(33, 'ticket_status', 'status codes for tickets', 0, 'MOHC', NULL, '2016-12-13 16:52:18', 'admin'),
(34, 'nominal_resolution', 'standard spatial resolution codes', 0, 'CMIP6_nominal_resolution', '3.2.4', '2018-11-16 10:37:05', ''),
(35, 'forcing_species', 'codes used to described forcings applied', 0, 'CMIP5', 'cmip5', '2018-11-16 10:38:35', '');

-- --------------------------------------------------------

--
-- Table structure for table `ct_config`
--

CREATE TABLE IF NOT EXISTS `ct_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for configuration parameter',
  `project` varchar(40) NOT NULL DEFAULT 'ALL' COMMENT 'project scope for this item (expressed as project sname) - ALL if it is not project specific',
  `process` enum('extract','transform','transfer','archive','teardown','metadata','system') NOT NULL DEFAULT 'system' COMMENT 'process scope',
  `parameter` varchar(40) NOT NULL COMMENT 'config parameter name',
  `value` varchar(80) NOT NULL COMMENT 'value for config parameter',
  `info` varchar(200) NOT NULL COMMENT 'description for config parameter',
  `upd_by` varchar(20) NOT NULL COMMENT 'person/process responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  PRIMARY KEY (`id`),
  KEY `parameter` (`project`,`process`,`parameter`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='configuration - may be project or process specifi';

-- --------------------------------------------------------

--
-- Table structure for table `ct_users`
--

CREATE TABLE IF NOT EXISTS `ct_users` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(300) DEFAULT NULL,
  `password` varchar(300) DEFAULT NULL,
  `email` varchar(300) DEFAULT NULL,
  `fullname` varchar(300) DEFAULT NULL,
  `groupid` varchar(300) DEFAULT NULL,
  `active` tinyint(11) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `ct_users`
--

INSERT INTO `ct_users` (`ID`, `username`, `password`, `email`, `fullname`, `groupid`, `active`) VALUES
(15, 'piotrf', 'welcome', 'piotr.florek@metoffice.gov.uk', 'piotr florek', '', NULL),
(12, 'admin', 'admin', NULL, NULL, NULL, NULL),
(14, 'pamv', 'welcome', 'pam.vass@blueyonder.co.uk', 'pam vass', '', NULL),
(16, 'guest', 'welcome', 'guest@metoffice.gov.uk', '', '', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `mt_coupledmodel`
--

CREATE TABLE IF NOT EXISTS `mt_coupledmodel` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for model record',
  `sname` varchar(40) NOT NULL COMMENT 'short external code name for model as used for CMIP source_id attribute - will be registered with project',
  `name` varchar(60) DEFAULT NULL COMMENT 'internal name used for model - can be same as external name',
  `info` varchar(2000) NOT NULL COMMENT 'text definition of model as required by CMIP "source" attribute',
  `modeltype` varchar(40) NOT NULL COMMENT 'model type code',
  `timestep` int(10) DEFAULT NULL,
  `version` varchar(20) NOT NULL COMMENT 'version code',
  `releasedate` date NOT NULL COMMENT 'date model was released for use',
  `weblink` varchar(150) DEFAULT NULL COMMENT 'link to further information on the model',
  `specialisation` varchar(20) DEFAULT NULL COMMENT 'specialisation code',
  `upd_by` char(20) NOT NULL COMMENT 'person/process responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `o_type` enum('COUPLEDMODEL') NOT NULL DEFAULT 'COUPLEDMODEL' COMMENT 'object type',
  `esdoc_id` text COMMENT 'id from esdoc specialisation',
  `esdoc_hash` text COMMENT 'hash from esdoc specialisation',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='coupled model ';

--
-- Dumping data for table `mt_coupledmodel`
--

INSERT INTO `mt_coupledmodel` (`id`, `sname`, `name`, `info`, `modeltype`, `timestep`, `version`, `releasedate`, `weblink`, `specialisation`, `upd_by`, `upd_date`, `o_type`, `esdoc_id`, `esdoc_hash`) VALUES
(10001, 'HadGEM3-GC31-LL', 'HadGEM3-GC3.1-N96ORCA1', '"aerosol":"UKCA-GLOMAP-mode",\r\n"atmosphere":"MetUM-HadGEM3-GA7.1 (192 x 144 N96; 85 levels; top level 85km)",\r\n"atmospheric_chemistry":"None",\r\n"land_ice":"None",\r\n"land_surface":"JULES-HadGEM3-GL7.1",\r\n"ocean":"NEMO-HadGEM3-GO6.0 (ORCA1 tripolar primarily 1 deg latitude/longitude with meridional refinement down to 1/3 degree in the tropics; 75 levels; top grid cell 0-1m)",\r\n"ocean_biogeochemistry":"None",\r\n"sea_ice":"CICE-HadGEM3-GSI8 (ORCA1 tripolar primarily 1 deg latitude/longitude)",', '', NULL, '3.1', '2017-03-01', '', 'cmip6', 'admin', '2017-03-15 14:58:43', 'COUPLEDMODEL', '', ''),
(10002, 'HadGEM2-TEST', 'test model record', 'blah blah', 'AOGCM,CHEM,ISM,LAND', NULL, '2', '2017-05-31', '', 'cmip6', 'admin', '2017-05-18 15:02:28', 'COUPLEDMODEL', '', '');

-- --------------------------------------------------------

--
-- Table structure for table `mt_coupling`
--

CREATE TABLE IF NOT EXISTS `mt_coupling` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `coupledmodelid` int(11) NOT NULL COMMENT 'id for coupled model',
  `modelid` int(11) NOT NULL COMMENT 'id for model',
  `coupler` varchar(40) NOT NULL COMMENT 'code for coupler used',
  `coupled` text COMMENT 'Summary of variables that are coupled',
  `info` text COMMENT 'description of coupling / integration',
  `rank` int(2) DEFAULT '1' COMMENT 'display order',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `upd_by` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='many-to-many table for coupling modelsrelationship';

-- --------------------------------------------------------

--
-- Table structure for table `mt_domain`
--

CREATE TABLE IF NOT EXISTS `mt_domain` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for domain',
  `modelid` int(11) NOT NULL COMMENT 'id for model domain is associated with',
  `sname` varchar(40) NOT NULL COMMENT 'short name for domain (e.g. land)',
  `name` varchar(100) DEFAULT NULL COMMENT 'full name for domain',
  `info` varchar(20) DEFAULT NULL,
  `realm` varchar(20) DEFAULT NULL COMMENT 'realm code from specialisation',
  `specialisation` varchar(20) DEFAULT NULL,
  `upd_by` char(20) NOT NULL COMMENT 'updated by',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of update',
  `o_type` enum('DOMAIN') NOT NULL DEFAULT 'DOMAIN',
  `esdoc_id` text COMMENT 'id from esdoc specialisation',
  `esdoc_hash` text COMMENT 'hash from esdoc specialisation',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='used to handle CIM realm';

--
-- Dumping data for table `mt_domain`
--

INSERT INTO `mt_domain` (`id`, `modelid`, `sname`, `name`, `info`, `realm`, `specialisation`, `upd_by`, `upd_date`, `o_type`, `esdoc_id`, `esdoc_hash`) VALUES
(10002, 10001, 'ocean', 'ocean', '', 'ocean', 'cmip6', 'admin', '2017-02-02 15:47:34', 'DOMAIN', NULL, NULL),
(10003, 10002, 'ocean', 'ocean', '', 'ocean', 'cmip6', 'clone_10002', '2017-03-14 21:28:51', 'DOMAIN', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `mt_grid`
--

CREATE TABLE IF NOT EXISTS `mt_grid` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for grid records',
  `modelid` int(11) NOT NULL COMMENT 'model key',
  `sname` varchar(40) NOT NULL COMMENT 'mnemonic for grid',
  `name` varchar(40) NOT NULL COMMENT 'grid name',
  `info` varchar(1000) NOT NULL COMMENT 'description of grid to be used in CMIP[''grid'']',
  `cmip_label` varchar(10) NOT NULL COMMENT 'CMIP grid label (e.g. gn, gr2, gz etc.)',
  `horizontal_construction` varchar(100) DEFAULT NULL COMMENT 'horizontal construction method',
  `vertical_construction` varchar(100) DEFAULT NULL COMMENT 'vertical construction method',
  `dimensions` int(1) DEFAULT NULL COMMENT 'number of dimensions',
  `cells` varchar(20) DEFAULT NULL COMMENT 'resolution code e.g. N96L85',
  `horizontal_resolution` varchar(40) NOT NULL COMMENT 'approximate horizontal resolution used for CMIP[''nominal_resolution'']',
  `vertical_layers` int(3) DEFAULT NULL COMMENT 'No of vertical levels',
  `isuniform` tinyint(1) DEFAULT NULL COMMENT 'is grid regular',
  `isregular` tinyint(1) DEFAULT NULL COMMENT 'is grid uniform',
  `datum` varchar(100) DEFAULT NULL COMMENT 'datum for this grid (e.g. sphere)',
  `realms` varchar(200) DEFAULT NULL COMMENT 'list of realms reporting on this grid',
  `upd_by` varchar(20) NOT NULL COMMENT 'last update by',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'last update date',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `mt_grid`
--

INSERT INTO `mt_grid` (`id`, `modelid`, `sname`, `name`, `info`, `cmip_label`, `horizontal_construction`, `vertical_construction`, `dimensions`, `cells`, `horizontal_resolution`, `vertical_layers`, `isuniform`, `isregular`, `datum`, `realms`, `upd_by`, `upd_date`) VALUES
(1, 10002, 'MyGRID', 'Standard UM Grid', 'blah blah', 'N64L32', 'Arakawa', 'Charney', 3, '10000', '50km', 32, 1, 1, 'SPHERE', 'atmos,ocean,landIce', '', '2017-05-18 15:04:06');

-- --------------------------------------------------------

--
-- Table structure for table `mt_model`
--

CREATE TABLE IF NOT EXISTS `mt_model` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for model record',
  `sname` char(40) NOT NULL COMMENT 'short code name for submodel (e.g. JULES)',
  `name` varchar(200) NOT NULL COMMENT 'full text name of submodel',
  `info` text COMMENT 'text description of submodel',
  `version` varchar(20) NOT NULL COMMENT 'model version ',
  `code_repository` varchar(200) DEFAULT NULL COMMENT 'repository for model code',
  `code_language` varchar(60) DEFAULT NULL COMMENT 'coding language used for model',
  `tuning` text COMMENT 'description of tuning applied to model',
  `grid_id` int(11) DEFAULT NULL COMMENT 'id for grid record',
  `grid_code` varchar(40) DEFAULT NULL COMMENT 'code for cell resolution and levels (e.g. N96L38)',
  `grid_info` text COMMENT 'grid description',
  `modeltype` varchar(40) NOT NULL COMMENT 'code for model type',
  `releasedate` date DEFAULT NULL COMMENT 'date model was released for use',
  `weblink` varchar(150) DEFAULT NULL COMMENT 'url to model information',
  `upd_by` char(20) NOT NULL COMMENT 'person/process responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `o_type` enum('MODEL') NOT NULL DEFAULT 'MODEL' COMMENT 'object type',
  `esdoc_id` text COMMENT 'id from esdoc specialisation',
  `esdoc_hash` text COMMENT 'hash from esdoc specialisation',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='component models';

--
-- Dumping data for table `mt_model`
--

INSERT INTO `mt_model` (`id`, `sname`, `name`, `info`, `version`, `code_repository`, `code_language`, `tuning`, `grid_id`, `grid_code`, `grid_info`, `modeltype`, `releasedate`, `weblink`, `upd_by`, `upd_date`, `o_type`, `esdoc_id`, `esdoc_hash`) VALUES
(10001, 'NEMO - ORCA1', 'Nucleus for European Modelling of the Ocean', 'The ORCA1 ocean component is based on version 3.6 of the NEMO ocean model code (Madec, 2008). The horizontal grid is a tripolar Arakawa C-grid with a nominal 1° resolution. The vertical grid has 75 levels with thickness increasing over depth. The timestep size is 15 minutes. A full description can be found in Storkey et al. (in preparation, 2017). \r\n\r\nThe model bathymetry iis based on the ETOPO1 dataset (Amante and Eakins, 2009) with additional data in coastal regions from GEBCO (IOC, 2008) and the bathymetry on the Antarctic shelf based on IBSCO (Arndt et al., 2013). Bottom topography is represented as partial steps (Barnier et al. 2006). The derivation of DRAKKAR bathymetry data sets is described by Barnier et al. (2006): initially, each model grid cell is assigned the median of all observations falling within the boundaries of that grid cell. The initial estimate is then modified by application of two passes of a uniform Shapiro filter and, finally, hand editing is performed in a few key areas. Further smoothing is performed along the Antarctic coastline to remove single grid point inlets and avoid the spurious accumulation of sea ice here.\r\n\r\n[coupling notes to be added]\r\n', '3.6', NULL, NULL, NULL, NULL, '', NULL, 'OGCM', '2015-06-30', 'http://www.nemo-ocean.eu', 'admin', '2018-05-23 15:56:46', 'MODEL', NULL, NULL),
(10002, 'NEMO - ORCA025', 'Nucleus for European Modelling of the Ocean', 'The ORCA25 ocean component is based on version 3.6 of the NEMO ocean model code (Madec, 2008), and is closely related to the global DRAKKAR ORCA025 configuration (Barnier et al., 2006) sharing many of the same dynamics and physics choices. A full description can be found in Storkey et al. (in preparation, 2017). \r\n\r\nThe horizontal grid is an extended version of the ORCA025 tripolar Arakawa C-grid (Barnier et al., 2006). This has nominal 1/4° resolution (1442 x 1207 grid points) at global scale decreasing poleward (an isotropic Mercator grid in the southern hemisphere, matched to a quasi-isotropic bipolar grid in the northern hemisphere with poles at 107°W and 73°E). The reference ORCA025 grid has been extended southwards from 77°S to 85°S using the procedure of Mathiot et al. (submitted 2017) to permit the modelling of the circulation under ice shelves in Antarctica. The effective resolution is approximately 27.75 km at the equator but increases with latitude (for example, to 13.8 km at 60°S or 60°N). The vertical grid has 75 levels where the level thickness is a double tanh function of depth such that the grid spacing increases from 1 m near the surface to 200 m at 6000 m (Culverwell, 2009). This level set was chosen to provide high resolution near the surface for short to mid range forecasting purposes while retaining reasonable resolution at mid-depths for long term climate studies. The forward timestep size is 15 minutes.\r\n\r\nThe model bathymetry iis based on the ETOPO1 dataset (Amante and Eakins, 2009) with additional data in coastal regions from GEBCO (IOC, 2008) and the bathymetry on the Antarctic shelf based on IBSCO (Arndt et al., 2013). Bottom topography is represented as partial steps (Barnier et al. 2006). The derivation of DRAKKAR bathymetry data sets is described by Barnier et al. (2006): initially, each model grid cell is assigned the median of all observations falling within the boundaries of that grid cell. The initial estimate is then modified by application of two passes of a uniform Shapiro filter and, finally, hand editing is performed in a few key areas. Further smoothing is performed along the Antarctic coastline to remove single grid point inlets and avoid the spurious accumulation of sea ice here.\r\n\r\n[coupling notes to be added]\r\n', '3.6', '', '', '', NULL, '', '', 'OGCM', '2015-05-30', 'http://www.nemo-ocean.eu', 'hadel', '2018-05-23 15:56:27', 'MODEL', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `mt_propenum`
--

CREATE TABLE IF NOT EXISTS `mt_propenum` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key for enum values',
  `propertyid` varchar(200) NOT NULL COMMENT 'if for property',
  `s_value` varchar(100) NOT NULL COMMENT 'value to be returned',
  `s_label` varchar(100) NOT NULL COMMENT 'label for value',
  `s_desc` varchar(300) DEFAULT NULL COMMENT 'description',
  `extend` int(1) NOT NULL DEFAULT '0' COMMENT '0 if from specialisation, 1 if local extension value',
  `display` int(3) DEFAULT NULL,
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `upd_by` varchar(20) NOT NULL,
  `esdoc_id` text COMMENT 'id from esdoc specialisation',
  `esdoc_hash` text COMMENT 'hash from esdoc specialisation',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `mt_propenum`
--

INSERT INTO `mt_propenum` (`id`, `propertyid`, `s_value`, `s_label`, `s_desc`, `extend`, `display`, `upd_date`, `upd_by`, `esdoc_id`, `esdoc_hash`) VALUES
(10000, '10001', 'None', 'None', 'No diurnal cycle in ocean', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10001, '10001', 'Specific treatment', 'Specific treatment', 'Specific treament', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10002, '10001', 'Via coupling', 'Via coupling', 'Diurnal cycle via coupling frequency', 0, 2, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10003, '10002', 'AM3-LF (ROMS)', 'AM3-LF (ROMS)', 'AM3-LF used in ROMS', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10004, '10002', 'Forward operator', 'Forward operator', 'Forward operator scheme', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10005, '10002', 'Forward-backward', 'Forward-backward', 'Forward-backward scheme', 0, 2, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10006, '10002', 'Leap-frog + Asselin filter', 'Leap-frog + Asselin filter', 'Leap-frog scheme with Asselin filter', 0, 3, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10007, '10002', 'Leap-frog + Periodic Euler backward solver', 'Leap-frog + Periodic Euler backward solver', 'Leap-frog scheme with Periodic Euler backward solver', 0, 4, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10008, '10002', 'Predictor-corrector', 'Predictor-corrector', 'Predictor-corrector scheme', 0, 5, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10009, '10003', 'AM3-LF (ROMS)', 'AM3-LF (ROMS)', 'AM3-LF used in ROMS', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10010, '10003', 'Forward operator', 'Forward operator', 'Forward operator scheme', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10011, '10003', 'Forward-backward', 'Forward-backward', 'Forward-backward scheme', 0, 2, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10012, '10003', 'Leap-frog + Asselin filter', 'Leap-frog + Asselin filter', 'Leap-frog scheme with Asselin filter', 0, 3, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10013, '10003', 'Leap-frog + Periodic Euler backward solver', 'Leap-frog + Periodic Euler backward solver', 'Leap-frog scheme with Periodic Euler backward solver', 0, 4, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10014, '10003', 'Predictor-corrector', 'Predictor-corrector', 'Predictor-corrector scheme', 0, 5, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10015, '10004', 'Preconditioned conjugate gradient', 'Preconditioned conjugate gradient', '', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10016, '10004', 'Sub cyling', 'Sub cyling', '', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10017, '10005', 'AM3-LF (ROMS)', 'AM3-LF (ROMS)', 'AM3-LF used in ROMS', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10018, '10005', 'Forward operator', 'Forward operator', 'Forward operator scheme', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10019, '10005', 'Forward-backward', 'Forward-backward', 'Forward-backward scheme', 0, 2, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10020, '10005', 'Leap-frog + Asselin filter', 'Leap-frog + Asselin filter', 'Leap-frog scheme with Asselin filter', 0, 3, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10021, '10005', 'Leap-frog + Periodic Euler backward solver', 'Leap-frog + Periodic Euler backward solver', 'Leap-frog scheme with Periodic Euler backward solver', 0, 4, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10022, '10005', 'Predictor-corrector', 'Predictor-corrector', 'Predictor-corrector scheme', 0, 5, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10023, '10006', 'Flux form', 'Flux form', '', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10024, '10006', 'Vector form', 'Vector form', '', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10025, '10009', '3rd order upwind', '3rd order upwind', '', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10026, '10009', 'Centred 2nd order', 'Centred 2nd order', '', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10027, '10009', 'Centred 4th order', 'Centred 4th order', '', 0, 2, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10028, '10009', 'MUSCL', 'MUSCL', '', 0, 3, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10029, '10009', 'Piecewise Parabolic method', 'Piecewise Parabolic method', '', 0, 4, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10030, '10009', 'Prather 2nd moment (PSOM)', 'Prather 2nd moment (PSOM)', '', 0, 5, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10031, '10009', 'QUICKEST', 'QUICKEST', '', 0, 6, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10032, '10009', 'Sweby', 'Sweby', '', 0, 7, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10033, '10009', 'Total Variance Dissipation (TVD)', 'Total Variance Dissipation (TVD)', '', 0, 8, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10034, '10011', 'CFC 11', 'CFC 11', '', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10035, '10011', 'CFC 12', 'CFC 12', '', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10036, '10011', 'Ideal age', 'Ideal age', '', 0, 2, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10037, '10011', 'SF6', 'SF6', '', 0, 3, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10038, '10013', '3rd order upwind', '3rd order upwind', '', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10039, '10013', 'Centred 2nd order', 'Centred 2nd order', '', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10040, '10013', 'Centred 4th order', 'Centred 4th order', '', 0, 2, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10041, '10013', 'MUSCL', 'MUSCL', '', 0, 3, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10042, '10013', 'Piecewise Parabolic method', 'Piecewise Parabolic method', '', 0, 4, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10043, '10013', 'Prather 2nd moment (PSOM)', 'Prather 2nd moment (PSOM)', '', 0, 5, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10044, '10013', 'QUICKEST', 'QUICKEST', '', 0, 6, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10045, '10013', 'Sweby', 'Sweby', '', 0, 7, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10046, '10013', 'Total Variance Dissipation (TVD)', 'Total Variance Dissipation (TVD)', '', 0, 8, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10047, '10015', 'Eddy active', 'Eddy active', 'Full resolution of eddies', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10048, '10015', 'Eddy admitting', 'Eddy admitting', 'Some eddy activity permitted by resolution', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10049, '10015', 'None', 'None', 'No transient eddies in ocean', 0, 2, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10050, '10016', 'Geopotential', 'Geopotential', '', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10051, '10016', 'Horizontal', 'Horizontal', '', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10052, '10016', 'Iso-level', 'Iso-level', '', 0, 2, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10053, '10016', 'Isoneutral', 'Isoneutral', '', 0, 3, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10054, '10016', 'Isopycnal', 'Isopycnal', '', 0, 4, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10055, '10017', 'Bi-harmonic', 'Bi-harmonic', 'Fourth order', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10056, '10017', 'Harmonic', 'Harmonic', 'Second order', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10057, '10018', 'Flux limiter', 'Flux limiter', '', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10058, '10018', 'Higher order', 'Higher order', 'Higher order', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10059, '10018', 'Second order', 'Second order', 'Second order', 0, 2, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10060, '10019', 'Constant', 'Constant', '', 0, 0, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10061, '10019', 'Space varying', 'Space varying', '', 0, 1, '2017-02-02 15:57:00', 'realm_importer', NULL, NULL),
(10062, '10019', 'Time + space varying (Smagorinsky)', 'Time + space varying (Smagorinsky)', '', 0, 2, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10063, '10026', 'Geopotential', 'Geopotential', '', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10064, '10026', 'Horizontal', 'Horizontal', '', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10065, '10026', 'Iso-level', 'Iso-level', '', 0, 2, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10066, '10026', 'Isoneutral', 'Isoneutral', '', 0, 3, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10067, '10026', 'Isopycnal', 'Isopycnal', '', 0, 4, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10068, '10027', 'Bi-harmonic', 'Bi-harmonic', 'Fourth order', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10069, '10027', 'Harmonic', 'Harmonic', 'Second order', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10070, '10028', 'Flux limiter', 'Flux limiter', '', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10071, '10028', 'Higher order', 'Higher order', 'Higher order', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10072, '10028', 'Second order', 'Second order', 'Second order', 0, 2, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10073, '10029', 'Constant', 'Constant', '', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10074, '10029', 'Space varying', 'Space varying', '', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10075, '10029', 'Time + space varying (Smagorinsky)', 'Time + space varying (Smagorinsky)', '', 0, 2, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10076, '10034', 'GM', 'GM', 'Gent & McWilliams', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10077, '10039', 'Constant value', 'Constant value', '', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10078, '10039', 'Imbeded as isopycnic vertical coordinate', 'Imbeded as isopycnic vertical coordinate', '', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10079, '10039', 'Richardson number dependent - KT', 'Richardson number dependent - KT', '', 0, 2, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10080, '10039', 'Richardson number dependent - PP', 'Richardson number dependent - PP', '', 0, 3, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10081, '10039', 'Turbulent closure - Bulk Mixed Layer', 'Turbulent closure - Bulk Mixed Layer', '', 0, 4, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10082, '10039', 'Turbulent closure - KPP', 'Turbulent closure - KPP', '', 0, 5, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10083, '10039', 'Turbulent closure - Mellor-Yamada', 'Turbulent closure - Mellor-Yamada', '', 0, 6, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10084, '10039', 'Turbulent closure - TKE', 'Turbulent closure - TKE', '', 0, 7, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10085, '10043', 'Constant value', 'Constant value', '', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10086, '10043', 'Imbeded as isopycnic vertical coordinate', 'Imbeded as isopycnic vertical coordinate', '', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10087, '10043', 'Richardson number dependent - KT', 'Richardson number dependent - KT', '', 0, 2, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10088, '10043', 'Richardson number dependent - PP', 'Richardson number dependent - PP', '', 0, 3, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10089, '10043', 'Turbulent closure - Bulk Mixed Layer', 'Turbulent closure - Bulk Mixed Layer', '', 0, 4, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10090, '10043', 'Turbulent closure - KPP', 'Turbulent closure - KPP', '', 0, 5, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10091, '10043', 'Turbulent closure - Mellor-Yamada', 'Turbulent closure - Mellor-Yamada', '', 0, 6, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10092, '10043', 'Turbulent closure - TKE', 'Turbulent closure - TKE', '', 0, 7, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10093, '10047', 'Enhanced vertical diffusion', 'Enhanced vertical diffusion', '', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10094, '10047', 'Included in turbulence closure', 'Included in turbulence closure', '', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10095, '10047', 'Non-penetrative convective adjustment', 'Non-penetrative convective adjustment', '', 0, 2, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10096, '10051', 'Constant value', 'Constant value', '', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10097, '10051', 'Imbeded as isopycnic vertical coordinate', 'Imbeded as isopycnic vertical coordinate', '', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10098, '10051', 'Richardson number dependent - KT', 'Richardson number dependent - KT', '', 0, 2, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10099, '10051', 'Richardson number dependent - PP', 'Richardson number dependent - PP', '', 0, 3, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10100, '10051', 'Turbulent closure - Mellor-Yamada', 'Turbulent closure - Mellor-Yamada', '', 0, 4, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10101, '10051', 'Turbulent closure / TKE', 'Turbulent closure / TKE', '', 0, 5, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10102, '10055', 'Constant value', 'Constant value', '', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10103, '10055', 'Imbeded as isopycnic vertical coordinate', 'Imbeded as isopycnic vertical coordinate', '', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10104, '10055', 'Richardson number dependent - KT', 'Richardson number dependent - KT', '', 0, 2, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10105, '10055', 'Richardson number dependent - PP', 'Richardson number dependent - PP', '', 0, 3, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10106, '10055', 'Turbulent closure - Mellor-Yamada', 'Turbulent closure - Mellor-Yamada', '', 0, 4, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10107, '10055', 'Turbulent closure / TKE', 'Turbulent closure / TKE', '', 0, 5, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10108, '10059', 'Linear filtered', 'Linear filtered', '', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10109, '10059', 'Linear implicit', 'Linear implicit', '', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10110, '10059', 'Linear semi-explicit', 'Linear semi-explicit', '', 0, 2, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10111, '10059', 'Non-linear filtered', 'Non-linear filtered', '', 0, 3, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10112, '10059', 'Non-linear implicit', 'Non-linear implicit', '', 0, 4, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10113, '10059', 'Non-linear semi-explicit', 'Non-linear semi-explicit', '', 0, 5, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10114, '10061', 'Acvective', 'Acvective', '', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10115, '10061', 'Diffusive', 'Diffusive', '', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10116, '10070', 'Constant drag coefficient', 'Constant drag coefficient', '', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10117, '10070', 'Linear', 'Linear', '', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10118, '10070', 'Non-linear', 'Non-linear', '', 0, 2, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10119, '10070', 'Non-linear (drag function of speed of tides)', 'Non-linear (drag function of speed of tides)', '', 0, 3, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10120, '10070', 'None', 'None', '', 0, 4, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10121, '10071', 'Free-slip', 'Free-slip', '', 0, 0, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10122, '10071', 'No-slip', 'No-slip', '', 0, 1, '2017-02-02 15:57:01', 'realm_importer', NULL, NULL),
(10123, '10071', 'None', 'None', '', 0, 2, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10124, '10072', '1 extinction depth', '1 extinction depth', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10125, '10072', '2 extinction depth', '2 extinction depth', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10126, '10072', '3 extinction depth', '3 extinction depth', '', 0, 2, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10127, '10075', 'Freshwater flux', 'Freshwater flux', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10128, '10075', 'Virtual salt flux', 'Virtual salt flux', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10129, '10076', 'Freshwater flux', 'Freshwater flux', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10130, '10076', 'Real salt flux', 'Real salt flux', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10131, '10076', 'Virtual salt flux', 'Virtual salt flux', '', 0, 2, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10132, '10078', 'OGCM', 'OGCM', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10133, '10078', 'mixed layer ocean', 'mixed layer ocean', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10134, '10078', 'slab ocean', 'slab ocean', '', 0, 2, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10135, '10079', 'Boussinesq', 'Boussinesq', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10136, '10079', 'Non-hydrostatic', 'Non-hydrostatic', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10137, '10079', 'Primitive equations', 'Primitive equations', '', 0, 2, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10138, '10080', 'Conservative temperature', 'Conservative temperature', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10139, '10080', 'Potential temperature', 'Potential temperature', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10140, '10080', 'SSH', 'SSH', 'Sea Surface Height', 0, 2, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10141, '10080', 'Salinity', 'Salinity', '', 0, 3, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10142, '10080', 'U-velocity', 'U-velocity', '', 0, 4, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10143, '10080', 'V-velocity', 'V-velocity', '', 0, 5, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10144, '10080', 'W-velocity', 'W-velocity', '', 0, 6, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10145, '10081', 'Jackett et al. 2006', 'Jackett et al. 2006', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10146, '10081', 'Linear', 'Linear', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10147, '10081', 'Mc Dougall et al.', 'Mc Dougall et al.', '', 0, 2, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10148, '10081', 'TEOS 2010', 'TEOS 2010', '', 0, 3, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10149, '10082', 'Conservative temperature', 'Conservative temperature', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10150, '10082', 'Potential temperature', 'Potential temperature', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10151, '10083', 'Absolute salinity Sa', 'Absolute salinity Sa', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10152, '10083', 'Practical salinity Sp', 'Practical salinity Sp', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10153, '10084', 'Depth (meters)', 'Depth (meters)', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10154, '10084', 'Pressure (dbars)', 'Pressure (dbars)', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10155, '10085', 'TEOS 2010', 'TEOS 2010', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10156, '10088', '21000 years BP', '21000 years BP', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10157, '10088', '6000 years BP', '6000 years BP', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10158, '10088', 'LGM', 'LGM', 'Last Glacial Maximum', 0, 2, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10159, '10088', 'Pliocene', 'Pliocene', '', 0, 3, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10160, '10088', 'Present day', 'Present day', '', 0, 4, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10161, '10105', 'Energy', 'Energy', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10162, '10105', 'Enstrophy', 'Enstrophy', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10163, '10105', 'Momentum', 'Momentum', '', 0, 2, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10164, '10105', 'Salt', 'Salt', '', 0, 3, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10165, '10105', 'Volume of ocean', 'Volume of ocean', '', 0, 4, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10166, '10109', 'Hybrid / ALE', 'Hybrid / ALE', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10167, '10109', 'Hybrid / Z+S', 'Hybrid / Z+S', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10168, '10109', 'Hybrid / Z+isopycnic', 'Hybrid / Z+isopycnic', '', 0, 2, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10169, '10109', 'Hybrid / other', 'Hybrid / other', '', 0, 3, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10170, '10109', 'Isopycnic - other', 'Isopycnic - other', 'Other density-based coordinate', 0, 4, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10171, '10109', 'Isopycnic - sigma 0', 'Isopycnic - sigma 0', 'Density referenced to the surface', 0, 5, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10172, '10109', 'Isopycnic - sigma 2', 'Isopycnic - sigma 2', 'Density referenced to 2000 m', 0, 6, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10173, '10109', 'Isopycnic - sigma 4', 'Isopycnic - sigma 4', 'Density referenced to 4000 m', 0, 7, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10174, '10109', 'P*', 'P*', '', 0, 8, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10175, '10109', 'Pressure referenced (P)', 'Pressure referenced (P)', '', 0, 9, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10176, '10109', 'S-coordinate', 'S-coordinate', '', 0, 10, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10177, '10109', 'Z**', 'Z**', '', 0, 11, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10178, '10109', 'Z*-coordinate', 'Z*-coordinate', '', 0, 12, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10179, '10109', 'Z-coordinate', 'Z-coordinate', '', 0, 13, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10180, '10111', 'Lat-lon', 'Lat-lon', '', 0, 0, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10181, '10111', 'Rotated north pole', 'Rotated north pole', '', 0, 1, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10182, '10111', 'Two north poles (ORCA-style)', 'Two north poles (ORCA-style)', '', 0, 2, '2017-02-02 15:57:02', 'realm_importer', NULL, NULL),
(10183, '10112', 'Finite difference / Arakawa B-grid', 'Finite difference / Arakawa B-grid', '', 0, 0, '2017-02-02 15:57:03', 'realm_importer', NULL, NULL),
(10184, '10112', 'Finite difference / Arakawa C-grid', 'Finite difference / Arakawa C-grid', '', 0, 1, '2017-02-02 15:57:03', 'realm_importer', NULL, NULL),
(10185, '10112', 'Finite difference / Arakawa E-grid', 'Finite difference / Arakawa E-grid', '', 0, 2, '2017-02-02 15:57:03', 'realm_importer', NULL, NULL),
(10186, '10112', 'Finite elements', 'Finite elements', '', 0, 3, '2017-02-02 15:57:03', 'realm_importer', NULL, NULL),
(10187, '10112', 'Finite volumes', 'Finite volumes', '', 0, 4, '2017-02-02 15:57:03', 'realm_importer', NULL, NULL),
(10188, '10112', 'Unstructured grid', 'Unstructured grid', '', 0, 5, '2017-02-02 15:57:03', 'realm_importer', NULL, NULL),
(10189, '10034', 'HL', 'HL', 'Held and Larichev  (1996)', 1, 99, '2017-02-08 10:26:11', 'pamv', NULL, NULL),
(10190, '10061', 'Advective and Diffusive', 'Advective and Diffusive', 'Advective and diffusive bottom boundary layer type', 1, 99, '2017-02-09 08:13:54', 'pamv', NULL, NULL),
(10191, '10079', 'Boussinesq, Primitive equations', 'Boussinesq, Primitive equations', 'Boussinesq and primitive equations', 1, 99, '2017-02-10 15:08:11', 'pamv', NULL, NULL),
(10192, '10081', 'Polynomial EOS-80', 'Polynomial EOS-80', 'Polynomial EOS-80 EOS seawater type', 1, 99, '2017-02-10 15:24:56', 'pamv', NULL, NULL),
(10193, '10085', 'UNESCO, 1983', 'UNESCO, 1983', '', 1, 99, '2017-03-05 16:56:39', 'pamv', NULL, NULL),
(10194, '10105', 'Heat', 'Heat', '', 1, 99, '2017-03-05 17:15:20', 'pamv', NULL, NULL),
(10195, '10085', 'UNESCO 1983', 'UNESCO 1983', '', 1, 99, '2017-03-06 11:59:21', 'admin', NULL, NULL),
(10196, '10130', 'Bi-harmonic', 'Bi-harmonic', '', 1, 99, '2017-03-22 10:35:45', 'pamv', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `mt_property`
--

CREATE TABLE IF NOT EXISTS `mt_property` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for property record',
  `topicid` int(11) NOT NULL COMMENT 'id for topic that has this property',
  `s_group_id` varchar(100) DEFAULT NULL COMMENT 'id for detail ''group''',
  `s_group_label` varchar(100) DEFAULT NULL COMMENT 'label for detail ''group''',
  `s_group_description` varchar(100) DEFAULT NULL COMMENT 'description for detail ''group''',
  `s_id` varchar(200) NOT NULL COMMENT 'specialisation id for property',
  `s_display` int(3) NOT NULL DEFAULT '1' COMMENT 'display order for topic - uiOrdinal',
  `s_label` varchar(200) NOT NULL COMMENT 'specialisation label for property',
  `s_desc` varchar(500) DEFAULT NULL COMMENT 'specialisation description (question) for property',
  `s_cardinality` varchar(10) NOT NULL COMMENT 'cardinality for property - code list',
  `s_type` varchar(20) NOT NULL COMMENT 'specialisation property type - code list',
  `s_enum_id` varchar(200) DEFAULT NULL COMMENT 'specialisation enum identifier (if enum type)',
  `s_enum_lbl` varchar(200) DEFAULT NULL COMMENT 'specialisation label for enum (if enum type)',
  `s_enum_desc` varchar(500) DEFAULT NULL COMMENT 'specialisation enum description (if enum type)',
  `s_enum_open` tinyint(1) DEFAULT NULL COMMENT 'specialisation flag for extendible enum (if enum type)',
  `tmp_str` varchar(300) DEFAULT NULL COMMENT 'entry field for string, integer and float property types',
  `tmp_bool` varchar(10) DEFAULT NULL COMMENT 'entry field for boolean property types',
  `tmp_enum` varchar(100) DEFAULT NULL COMMENT 'entry field for enum property types',
  `tmp_enum_open` varchar(300) DEFAULT NULL COMMENT 'entry field for enum property - extendible enum',
  `value` varchar(300) DEFAULT NULL COMMENT 'property value for this model',
  `notes` varchar(1000) DEFAULT NULL COMMENT 'property notes for this model',
  `nullreason` varchar(30) DEFAULT NULL COMMENT 'reason for null response for this property (e.g. n/a) ',
  `specifiedby` int(11) DEFAULT NULL COMMENT 'person responsible for specifying property for this model',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` varchar(20) NOT NULL COMMENT 'person/process responsible for last update',
  `esdoc_id` text COMMENT 'id from esdoc specialisation',
  `esdoc_hash` text COMMENT 'hash from esdoc specialisation',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='used to describe properties across model descriptions';

--
-- Dumping data for table `mt_property`
--

INSERT INTO `mt_property` (`id`, `topicid`, `s_group_id`, `s_group_label`, `s_group_description`, `s_id`, `s_display`, `s_label`, `s_desc`, `s_cardinality`, `s_type`, `s_enum_id`, `s_enum_lbl`, `s_enum_desc`, `s_enum_open`, `tmp_str`, `tmp_bool`, `tmp_enum`, `tmp_enum_open`, `value`, `notes`, `nullreason`, `specifiedby`, `upd_date`, `upd_by`, `esdoc_id`, `esdoc_hash`) VALUES
(10000, 1, 'cmip6.ocean.timestepping_framework.timestepping_attributes', 'Timestepping Attributes', 'Properties of time stepping in ocean', 'cmip6.ocean.timestepping_framework.timestepping_attributes.time_step', 1, 'Time Step', 'Ocean time step in seconds', '1.1', 'int', NULL, NULL, NULL, NULL, '2700', '', '', '', '2700', '', '', 10000, '2017-02-10 15:43:07', 'pamv', NULL, NULL),
(10001, 1, 'cmip6.ocean.timestepping_framework.timestepping_attributes', 'Timestepping Attributes', 'Properties of time stepping in ocean', 'cmip6.ocean.timestepping_framework.timestepping_attributes.diurnal_cycle', 2, 'Diurnal Cycle', 'Diurnal cycle type', '1.1', 'enum', 'diurnal_cycle_types', 'diurnal_cycle_types', 'Types of diurnal cycle resolution in ocean', 1, '', '', '', 'Via coupling', 'Via coupling', '', '', 10000, '2017-02-06 17:05:15', 'pamv', NULL, NULL),
(10002, 1, 'cmip6.ocean.timestepping_framework.timestepping_tracers_scheme', 'Timestepping Tracers Scheme', 'Properties of tracers time stepping in ocean', 'cmip6.ocean.timestepping_framework.timestepping_tracers_scheme.tracers', 1, 'Tracers', 'Time stepping tracer scheme', '1.1', 'enum', 'ocean_timestepping_types', 'ocean_timestepping_types', 'Type of timestepping scheme in ocean', 1, '', '', '', 'Leap-frog + Asselin filter', 'Leap-frog + Asselin filter', '', '', 10000, '2017-02-10 15:44:17', 'pamv', NULL, NULL),
(10003, 1, 'cmip6.ocean.timestepping_framework.barotropic_solver_scheme', 'Barotropic Solver Scheme', 'Barotropic solver in ocean', 'cmip6.ocean.timestepping_framework.barotropic_solver_scheme.barotropic_solver', 1, 'Barotropic Solver', 'Barotropic solver scheme', '1.1', 'enum', 'ocean_timestepping_types', 'ocean_timestepping_types', 'Type of timestepping scheme in ocean', 1, '', '', '', 'Leap-frog + Asselin filter', 'Leap-frog + Asselin filter', '', '', 10000, '2017-02-10 15:45:04', 'pamv', NULL, NULL),
(10004, 1, 'cmip6.ocean.timestepping_framework.barotropic_solver_scheme', 'Barotropic Solver Scheme', 'Barotropic solver in ocean', 'cmip6.ocean.timestepping_framework.barotropic_solver_scheme.type', 2, 'Type', 'Barotropic solver type', '1.1', 'enum', 'barotropic_solver_types', 'barotropic_solver_types', 'Type of barotropic solver in ocean', 1, '', '', '', 'Preconditioned conjugate gradient', 'Preconditioned conjugate gradient', '', '', 10000, '2017-02-10 15:45:30', 'pamv', NULL, NULL),
(10005, 1, 'cmip6.ocean.timestepping_framework.barotropic_momentum_scheme', 'Barotropic Momentum Scheme', 'Barotropic momentum solver in ocean', 'cmip6.ocean.timestepping_framework.barotropic_momentum_scheme.barotropic_momentum', 1, 'Barotropic Momentum', 'Barotropic momentum scheme', '1.1', 'enum', 'ocean_timestepping_types', 'ocean_timestepping_types', 'Type of timestepping scheme in ocean', 1, '', '', '', 'Leap-frog + Asselin filter', 'Leap-frog + Asselin filter', '', '', 10000, '2017-02-10 15:44:44', 'pamv', NULL, NULL),
(10006, 3, '', '', '', 'cmip6.ocean.advection.momentum.type', 1, 'Type', 'Type of lateral momemtum advection scheme in ocean', '1.1', 'enum', 'adv_mom_scheme_types', 'adv_mom_scheme_types', 'Type of lateral momemtum advection scheme in ocean', 1, '', '', '', 'Vector form', 'Vector form', '', '', 10000, '2017-02-08 09:34:57', 'pamv', NULL, NULL),
(10007, 3, '', '', '', 'cmip6.ocean.advection.momentum.scheme_name', 2, 'Scheme Name', 'Name of ocean momemtum advection scheme', '1.1', 'str', NULL, NULL, NULL, NULL, 'Energy and ENstrophy conservative scheme (EEN)', '', '', '', 'Energy and ENstrophy conservative scheme (EEN)', '', '', 10000, '2017-03-05 16:09:53', 'pamv', NULL, NULL),
(10008, 3, '', '', '', 'cmip6.ocean.advection.momentum.ALE', 3, 'ALE', 'Using ALE for vertical advection ? (if vertical coordinates are sigma)', '0.1', 'bool', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-03-05 16:05:11', 'pamv', NULL, NULL),
(10009, 4, '', '', '', 'cmip6.ocean.advection.lateral_tracers.type', 1, 'Type', 'Type of lateral tracer advection scheme in ocean', '1.1', 'enum', 'adv_tra_scheme_types', 'adv_tra_scheme_types', 'Type of tracer advection scheme in ocean', 1, '', '', '', 'Total Variance Dissipation (TVD)', 'Total Variance Dissipation (TVD)', '', '', 10000, '2017-02-08 09:13:06', 'pamv', NULL, NULL),
(10010, 4, '', '', '', 'cmip6.ocean.advection.lateral_tracers.flux_limiter', 2, 'Flux Limiter', 'Monotonic flux limiter for vertical tracer advection scheme in ocean ?', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'false', '', '', 'false', '', '', 10000, '2017-02-08 09:13:41', 'pamv', NULL, NULL),
(10011, 4, '', '', '', 'cmip6.ocean.advection.lateral_tracers.passive_tracers', 3, 'Passive Tracers', 'Passive tracers advected', '0.N', 'enum', 'passive_tracers_list', 'passive_tracers_list', 'Passive tracers in ocean', 1, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-03-05 16:14:29', 'pamv', NULL, NULL),
(10012, 4, '', '', '', 'cmip6.ocean.advection.lateral_tracers.passive_tracers_advection', 4, 'Passive Tracers Advection', 'Is advection of passive tracers different than active ? if so, describe.', '0.1', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:unknown', 10000, '2017-03-05 16:15:30', 'pamv', NULL, NULL),
(10013, 5, '', '', '', 'cmip6.ocean.advection.vertical_tracers.type', 1, 'Type', 'Type of vertical tracer advection scheme in ocean', '1.1', 'enum', 'adv_tra_scheme_types', 'adv_tra_scheme_types', 'Type of tracer advection scheme in ocean', 1, '', '', '', 'Total Variance Dissipation (TVD)', 'Total Variance Dissipation (TVD)', '', '', 10000, '2017-02-08 09:40:05', 'pamv', NULL, NULL),
(10014, 5, '', '', '', 'cmip6.ocean.advection.vertical_tracers.flux_limiter', 2, 'Flux Limiter', 'Monotonic flux limiter for vertical tracer advection scheme in ocean ?', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'false', '', '', 'false', '', '', 10000, '2017-02-08 09:40:21', 'pamv', NULL, NULL),
(10015, 6, 'cmip6.ocean.lateral_physics.ocean_transient_eddy_representation', 'Ocean Transient Eddy Representation', 'Type of transient eddy representation in ocean', 'cmip6.ocean.lateral_physics.ocean_transient_eddy_representation.scheme', 1, 'Scheme', 'Type of transient eddy representation in ocean', '1.1', 'enum', 'latphys_transient_eddy_types', 'latphys_transient_eddy_types', 'Type of transient eddy representation in ocean', 1, '', '', '', 'None', 'None', '', '', 10000, '2017-02-08 14:41:37', 'pamv', NULL, NULL),
(10016, 7, 'cmip6.ocean.lateral_physics.momentum.operator', 'Operator', 'Properties of lateral physics operator for momentum in ocean', 'cmip6.ocean.lateral_physics.momentum.operator.direction', 1, 'Direction', 'Direction of lateral physics momemtum scheme in the ocean', '1.1', 'enum', 'latphys_operator_direc_types', 'latphys_operator_direc_types', 'Type of lateral physics direction in ocean', 1, '', '', '', 'Geopotential', 'Geopotential', '', '', 10000, '2017-02-08 10:15:30', 'pamv', NULL, NULL),
(10017, 7, 'cmip6.ocean.lateral_physics.momentum.operator', 'Operator', 'Properties of lateral physics operator for momentum in ocean', 'cmip6.ocean.lateral_physics.momentum.operator.order', 2, 'Order', 'Order of lateral physics momemtum scheme in the ocean', '1.1', 'enum', 'latphys_operator_order_types', 'latphys_operator_order_types', 'Type of lateral physics order in ocean', 1, '', '', '', 'Harmonic', 'Harmonic', '', '', 10000, '2017-02-08 10:15:51', 'pamv', NULL, NULL),
(10018, 7, 'cmip6.ocean.lateral_physics.momentum.operator', 'Operator', 'Properties of lateral physics operator for momentum in ocean', 'cmip6.ocean.lateral_physics.momentum.operator.discretisation', 3, 'Discretisation', 'Discretisation of lateral physics momemtum scheme in the ocean', '1.1', 'enum', 'latphys_operator_discret_types', 'latphys_operator_discret_types', 'Type of lateral physics discretisation in ocean', 1, '', '', '', '', NULL, '', 'nil:unknown', 10000, '2017-02-08 10:16:11', 'pamv', NULL, NULL),
(10019, 7, 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics momemtum scheme in the ocean', 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff.type', 1, 'Type', 'Lateral physics momemtum eddy viscosity coeff type in the ocean', '1.1', 'enum', 'latphys_eddy_visc_coeff_types', 'latphys_eddy_visc_coeff_types', 'Type of lateral physics eddy viscosity coeff in ocean', 1, '', '', '', 'Space varying', 'Space varying', '', '', 10000, '2017-02-08 10:16:42', 'pamv', NULL, NULL),
(10020, 7, 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics momemtum scheme in the ocean', 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff.constant_coefficient', 2, 'Constant Coefficient', 'If constant, value of eddy viscosity coeff in lateral physics momemtum scheme (in m2/s)', '0.1', 'int', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-02-08 10:17:26', 'pamv', NULL, NULL),
(10021, 7, 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics momemtum scheme in the ocean', 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff.variable_coefficient', 3, 'Variable Coefficient', 'If space-varying, describe variations of eddy viscosity coeff in lateral physics momemtum scheme', '0.1', 'str', NULL, NULL, NULL, NULL, '-1.5e11 m4/s at equator reducing with cube of grid spacing, plus hyperbolic vertical profile\r\n', '', '', '', '-1.5e11 m4/s at equator reducing with cube of grid spacing, plus hyperbolic vertical profile\r\n', '', '', 10000, '2017-02-08 10:20:06', 'pamv', NULL, NULL),
(10022, 7, 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics momemtum scheme in the ocean', 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff.coeff_background', 4, 'Coeff Background', 'Background value of eddy viscosity coeff in lateral physics momemtum scheme (in m2/s)', '1.1', 'int', NULL, NULL, NULL, NULL, '20000', '', '', '', '20000', '', '', 10000, '2017-02-08 10:20:49', 'pamv', NULL, NULL),
(10023, 7, 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics momemtum scheme in the ocean', 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff.coeff_backscatter', 5, 'Coeff Backscatter', 'Is there backscatter in eddy viscosity coeff in lateral physics momemtum scheme ?', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'false', '', '', 'false', '', '', 10000, '2017-02-08 10:21:15', 'pamv', NULL, NULL),
(10024, 8, '', '', '', 'cmip6.ocean.lateral_physics.tracers.mesoscale_closure', 1, 'Mesoscale Closure', 'Is there a mesoscale closure in the lateral physics tracers scheme ?', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'true', '', '', 'true', '', '', 10000, '2017-02-08 10:22:17', 'pamv', NULL, NULL),
(10025, 8, '', '', '', 'cmip6.ocean.lateral_physics.tracers.submesoscale_mixing', 2, 'Submesoscale Mixing', 'Is there a submesoscale mixing parameterisation (i.e Fox-Kemper) in the lateral physics tracers scheme ?', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'false', '', '', 'false', '', '', 10000, '2017-02-08 10:22:36', 'pamv', NULL, NULL),
(10026, 8, 'cmip6.ocean.lateral_physics.tracers.operator', 'Operator', 'Properties of lateral physics operator for tracers in ocean', 'cmip6.ocean.lateral_physics.tracers.operator.direction', 1, 'Direction', 'Direction of lateral physics tracers scheme in the ocean', '1.1', 'enum', 'latphys_operator_direc_types', 'latphys_operator_direc_types', 'Type of lateral physics direction in ocean', 1, '', '', '', 'Isoneutral', 'Isoneutral', '', '', 10000, '2017-02-08 10:40:47', 'pamv', NULL, NULL),
(10027, 8, 'cmip6.ocean.lateral_physics.tracers.operator', 'Operator', 'Properties of lateral physics operator for tracers in ocean', 'cmip6.ocean.lateral_physics.tracers.operator.order', 2, 'Order', 'Order of lateral physics tracers scheme in the ocean', '1.1', 'enum', 'latphys_operator_order_types', 'latphys_operator_order_types', 'Type of lateral physics order in ocean', 1, '', '', '', 'Harmonic', 'Harmonic', '', '', 10000, '2017-02-08 10:41:05', 'pamv', NULL, NULL),
(10028, 8, 'cmip6.ocean.lateral_physics.tracers.operator', 'Operator', 'Properties of lateral physics operator for tracers in ocean', 'cmip6.ocean.lateral_physics.tracers.operator.discretisation', 3, 'Discretisation', 'Discretisation of lateral physics tracers scheme in the ocean', '1.1', 'enum', 'latphys_operator_discret_types', 'latphys_operator_discret_types', 'Type of lateral physics discretisation in ocean', 1, '', '', '', '', NULL, '', 'nil:unknown', 10000, '2017-03-05 16:23:12', 'pamv', NULL, NULL),
(10029, 8, 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff.type', 1, 'Type', 'Lateral physics tracers eddy viscosity coeff type in the ocean', '1.1', 'enum', 'latphys_eddy_visc_coeff_types', 'latphys_eddy_visc_coeff_types', 'Type of lateral physics eddy viscosity coeff in ocean', 1, '', '', '', 'Space varying', 'Space varying', '', '', 10000, '2017-02-08 10:29:55', 'pamv', NULL, NULL),
(10030, 8, 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff.constant_coefficient', 2, 'Constant Coefficient', 'If constant, value of eddy viscosity coeff in lateral physics tracers scheme (in m2/s)', '0.1', 'int', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-02-08 10:30:14', 'pamv', NULL, NULL),
(10031, 8, 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff.variable_coefficient', 3, 'Variable Coefficient', 'If space-varying, describe variations of eddy viscosity coeff in lateral physics tracers scheme', '0.1', 'str', NULL, NULL, NULL, NULL, '20000 m2/s; hyperbolic tangent variation with depth associated with a grid size dependence of the magnitude of the coefficient', '', '', '', '20000 m2/s; hyperbolic tangent variation with depth associated with a grid size dependence of the magnitude of the coefficient', '', '', 10000, '2017-02-08 10:31:46', 'pamv', NULL, NULL),
(10032, 8, 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff.coeff_background', 4, 'Coeff Background', 'Background value of eddy viscosity coeff in lateral physics tracers scheme (in m2/s)', '1.1', 'int', NULL, NULL, NULL, NULL, '0', '', '', '', '0', '', '', 10000, '2017-03-05 16:24:30', 'pamv', NULL, NULL),
(10033, 8, 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff.coeff_backscatter', 5, 'Coeff Backscatter', 'Is there backscatter in eddy viscosity coeff in lateral physics tracers scheme ?', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'false', '', '', 'false', '', '', 10000, '2017-02-08 10:32:17', 'pamv', NULL, NULL),
(10034, 8, 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity', 'Eddy Induced Velocity', 'Properties of eddy induced velocity (EIV) in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity.type', 1, 'Type', 'Type of EIV in lateral physics tracers in the ocean', '1.1', 'enum', 'latphys_eiv_types', 'latphys_eiv_types', 'Type of lateral physics eddy induced velocity in ocean', 1, '', '', '', 'HL', 'HL', '', '', 10000, '2017-02-08 10:26:32', 'pamv', NULL, NULL),
(10035, 8, 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity', 'Eddy Induced Velocity', 'Properties of eddy induced velocity (EIV) in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity.constant_val', 2, 'Constant Val', 'If EIV scheme for tracers is constant, specify coefficient value (M2/s)', '0.1', 'int', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-02-08 10:27:06', 'pamv', NULL, NULL),
(10036, 8, 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity', 'Eddy Induced Velocity', 'Properties of eddy induced velocity (EIV) in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity.flux_type', 3, 'Flux Type', 'Type of EIV flux (advective or skew)', '1.1', 'str', NULL, NULL, NULL, NULL, 'Advective', '', '', '', 'Advective', '', '', 10000, '2017-02-08 10:49:53', 'pamv', NULL, NULL),
(10037, 8, 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity', 'Eddy Induced Velocity', 'Properties of eddy induced velocity (EIV) in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity.added_diffusivity', 4, 'Added Diffusivity', 'Type of EIV added diffusivity (constant, flow dependent or none)', '1.1', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-03-05 16:26:26', 'pamv', NULL, NULL),
(10038, 10, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.details', 'Details', 'Properties of vertical physics in ocean', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.details.langmuir_cells_mixing', 1, 'Langmuir Cells Mixing', 'Is there Langmuir cells mixing in upper ocean ?', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'true', '', '', 'true', '', '', 10000, '2017-02-08 14:59:34', 'pamv', NULL, NULL),
(10039, 10, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers', 'Tracers', 'Properties of boundary layer (BL) mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers.type', 1, 'Type', 'Type of boundary layer mixing for tracers in ocean', '1.1', 'enum', 'bndlayer_mixing_types', 'bndlayer_mixing_types', 'Types of boundary layer mixing in ocean', 1, '', '', '', 'Turbulent closure - TKE', 'Turbulent closure - TKE', '', '', 10000, '2017-02-08 15:02:36', 'pamv', NULL, NULL),
(10040, 10, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers', 'Tracers', 'Properties of boundary layer (BL) mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers.closure_order', 2, 'Closure Order', 'If turbulent BL mixing of tracers, specific order of closure (0, 1, 2.5, 3)', '0.1', 'float', NULL, NULL, NULL, NULL, '1.5', '', '', '', '1.5', '', '', 10000, '2017-02-08 15:03:30', 'pamv', NULL, NULL),
(10041, 10, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers', 'Tracers', 'Properties of boundary layer (BL) mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers.constant', 3, 'Constant', 'If constant BL mixing of tracers, specific coefficient (m2/s)', '0.1', 'int', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-02-08 15:03:55', 'pamv', NULL, NULL),
(10042, 10, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers', 'Tracers', 'Properties of boundary layer (BL) mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers.background', 4, 'Background', 'Background BL mixing of tracers coefficient, (schema and value in m2/s - may by none)', '1.1', 'str', NULL, NULL, NULL, NULL, 'constant but reduced in tropics, 1.2e-5 m2/s', '', '', '', 'constant but reduced in tropics, 1.2e-5 m2/s', '', '', 10000, '2017-03-05 16:37:59', 'pamv', NULL, NULL),
(10043, 10, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum', 'Momentum', 'Properties of boundary layer (BL) mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum.type', 1, 'Type', 'Type of boundary layer mixing for momentum in ocean', '1.1', 'enum', 'bndlayer_mixing_types', 'bndlayer_mixing_types', 'Types of boundary layer mixing in ocean', 1, '', '', '', 'Turbulent closure - TKE', 'Turbulent closure - TKE', '', '', 10000, '2017-02-08 15:00:22', 'pamv', NULL, NULL),
(10044, 10, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum', 'Momentum', 'Properties of boundary layer (BL) mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum.closure_order', 2, 'Closure Order', 'If turbulent BL mixing of momentum, specific order of closure (0, 1, 2.5, 3)', '0.1', 'float', NULL, NULL, NULL, NULL, '1.5', '', '', '', '1.5', '', '', 10000, '2017-02-08 15:00:57', 'pamv', NULL, NULL),
(10045, 10, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum', 'Momentum', 'Properties of boundary layer (BL) mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum.constant', 3, 'Constant', 'If constant BL mixing of momentum, specific coefficient (m2/s)', '0.1', 'int', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-02-08 15:01:25', 'pamv', NULL, NULL),
(10046, 10, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum', 'Momentum', 'Properties of boundary layer (BL) mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum.background', 4, 'Background', 'Background BL mixing of momentum coefficient, (schema and value in m2/s - may by none)', '1.1', 'str', NULL, NULL, NULL, NULL, 'constant, 1.2e-5 m2/s', '', '', '', 'constant, 1.2e-5 m2/s', '', '', 10000, '2017-03-05 16:39:34', 'pamv', NULL, NULL),
(10047, 11, 'cmip6.ocean.vertical_physics.interior_mixing.details', 'Details', 'Properties of interior mixing in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.details.convection_type', 1, 'Convection Type', 'Type of vertical convection in ocean', '1.1', 'enum', 'vertphys_convection_types', 'vertphys_convection_types', 'Types of convection scheme in ocean', 1, '', '', '', 'Enhanced vertical diffusion', 'Enhanced vertical diffusion', '', '', 10000, '2017-02-08 15:06:52', 'pamv', NULL, NULL),
(10048, 11, 'cmip6.ocean.vertical_physics.interior_mixing.details', 'Details', 'Properties of interior mixing in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.details.tide_induced_mixing', 2, 'Tide Induced Mixing', 'Describe how tide induced mixing is modelled (barotropic, baroclinic, none)', '1.1', 'str', NULL, NULL, NULL, NULL, 'baroclinic based on climatologies', '', '', '', 'baroclinic based on climatologies', '', '', 10000, '2017-02-08 15:07:55', 'pamv', NULL, NULL),
(10049, 11, 'cmip6.ocean.vertical_physics.interior_mixing.details', 'Details', 'Properties of interior mixing in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.details.double_diffusion', 3, 'Double Diffusion', 'Is there double diffusion', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'true', '', '', 'true', '', '', 10000, '2017-02-08 15:08:20', 'pamv', NULL, NULL),
(10050, 11, 'cmip6.ocean.vertical_physics.interior_mixing.details', 'Details', 'Properties of interior mixing in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.details.shear_mixing', 4, 'Shear Mixing', 'Is there interior shear mixing', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'false', '', '', 'false', '', '', 10000, '2017-03-05 16:31:06', 'pamv', NULL, NULL),
(10051, 11, 'cmip6.ocean.vertical_physics.interior_mixing.tracers', 'Tracers', 'Properties of interior mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.tracers.type', 1, 'Type', 'Type of interior mixing for tracers in ocean', '1.1', 'enum', 'interior_mixing_types', 'interior_mixing_types', 'Types of interior mixing in ocean', 1, '', '', '', 'Turbulent closure / TKE', 'Turbulent closure / TKE', '', '', 10000, '2017-02-08 15:13:24', 'pamv', NULL, NULL),
(10052, 11, 'cmip6.ocean.vertical_physics.interior_mixing.tracers', 'Tracers', 'Properties of interior mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.tracers.constant', 2, 'Constant', 'If constant interior mixing of tracers, specific coefficient (m2/s)', '0.1', 'int', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-02-08 15:14:02', 'pamv', NULL, NULL),
(10053, 11, 'cmip6.ocean.vertical_physics.interior_mixing.tracers', 'Tracers', 'Properties of interior mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.tracers.profile', 3, 'Profile', 'Is the background interior mixing using a vertical profile for tracers (i.e is NOT constant) ?', '1.1', 'str', NULL, NULL, NULL, NULL, 'no profile', '', '', '', 'no profile', '', '', 10000, '2017-02-08 15:14:27', 'pamv', NULL, NULL),
(10054, 11, 'cmip6.ocean.vertical_physics.interior_mixing.tracers', 'Tracers', 'Properties of interior mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.tracers.background', 4, 'Background', 'Background interior mixing of tracers coefficient, (schema and value in m2/s - may by none)', '1.1', 'str', NULL, NULL, NULL, NULL, 'constant but reduced at tropics,1.2e-5 m2/s', '', '', '', 'constant but reduced at tropics,1.2e-5 m2/s', '', '', 10000, '2017-03-05 16:41:19', 'pamv', NULL, NULL),
(10055, 11, 'cmip6.ocean.vertical_physics.interior_mixing.momentum', 'Momentum', 'Properties of interior mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.momentum.type', 1, 'Type', 'Type of interior mixing for momentum in ocean', '1.1', 'enum', 'interior_mixing_types', 'interior_mixing_types', 'Types of interior mixing in ocean', 1, '', '', '', 'Turbulent closure / TKE', 'Turbulent closure / TKE', '', '', 10000, '2017-02-08 15:09:18', 'pamv', NULL, NULL),
(10056, 11, 'cmip6.ocean.vertical_physics.interior_mixing.momentum', 'Momentum', 'Properties of interior mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.momentum.constant', 2, 'Constant', 'If constant interior mixing of momentum, specific coefficient (m2/s)', '0.1', 'int', NULL, NULL, NULL, NULL, '1.5', '', '', '', '1', '', '', 10000, '2017-02-08 15:09:44', 'pamv', NULL, NULL),
(10057, 11, 'cmip6.ocean.vertical_physics.interior_mixing.momentum', 'Momentum', 'Properties of interior mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.momentum.profile', 3, 'Profile', 'Is the background interior mixing using a vertical profile for momentum (i.e is NOT constant) ?', '1.1', 'str', NULL, NULL, NULL, NULL, 'no profile', '', '', '', 'no profile', '', '', 10000, '2017-02-08 15:11:42', 'pamv', NULL, NULL),
(10058, 11, 'cmip6.ocean.vertical_physics.interior_mixing.momentum', 'Momentum', 'Properties of interior mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.momentum.background', 4, 'Background', 'Background interior mixing of momentum coefficient, (schema and value in m2/s - may by none)', '1.1', 'str', NULL, NULL, NULL, NULL, 'constant, 1.2e-5 m2/s', '', '', '', 'constant, 1.2e-5 m2/s', '', '', 10000, '2017-03-05 16:33:15', 'pamv', NULL, NULL),
(10059, 12, 'cmip6.ocean.uplow_boundaries.free_surface', 'Free Surface', 'Properties of free surface in ocean', 'cmip6.ocean.uplow_boundaries.free_surface.scheme', 1, 'Scheme', 'Free surface scheme in ocean', '1.1', 'enum', 'free_surface_types', 'free_surface_types', 'Type of free surface in ocean', 1, '', '', '', 'Non-linear filtered', 'Non-linear filtered', '', '', 10000, '2017-02-09 08:16:02', 'pamv', NULL, NULL),
(10060, 12, 'cmip6.ocean.uplow_boundaries.free_surface', 'Free Surface', 'Properties of free surface in ocean', 'cmip6.ocean.uplow_boundaries.free_surface.embeded_seaice', 2, 'Embeded Seaice', 'Is the sea-ice embeded in the ocean model (instead of levitating) ?', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'false', '', '', 'false', '', '', 10000, '2017-02-09 08:16:18', 'pamv', NULL, NULL),
(10061, 12, 'cmip6.ocean.uplow_boundaries.bottom_boundary_layer', 'Bottom Boundary Layer', 'Properties of bottom boundary layer in ocean', 'cmip6.ocean.uplow_boundaries.bottom_boundary_layer.type_of_bbl', 1, 'Type Of Bbl', 'Type of bottom boundary layer in ocean', '1.1', 'enum', 'bottom_bl_types', 'bottom_bl_types', 'Type of bottom boundary layer in ocean', 1, '', '', '', 'Advective and Diffusive', 'Advective and Diffusive', '', '', 10000, '2017-02-15 16:59:09', 'pamv', NULL, NULL),
(10062, 12, 'cmip6.ocean.uplow_boundaries.bottom_boundary_layer', 'Bottom Boundary Layer', 'Properties of bottom boundary layer in ocean', 'cmip6.ocean.uplow_boundaries.bottom_boundary_layer.lateral_mixing_coef', 2, 'Lateral Mixing Coef', 'If bottom BL is diffusive, specify value of lateral mixing coefficient (in m2/s)', '0.1', 'int', NULL, NULL, NULL, NULL, '1000', '', '', '', '1000', '', '', 10000, '2017-02-09 08:14:56', 'pamv', NULL, NULL),
(10063, 12, 'cmip6.ocean.uplow_boundaries.bottom_boundary_layer', 'Bottom Boundary Layer', 'Properties of bottom boundary layer in ocean', 'cmip6.ocean.uplow_boundaries.bottom_boundary_layer.sill_overflow', 3, 'Sill Overflow', 'Describe any specific treatment of sill overflows', '1.1', 'str', NULL, NULL, NULL, NULL, 'no special treatment', '', '', '', 'no special treatment', '', '', 10000, '2017-02-09 08:15:32', 'pamv', NULL, NULL),
(10064, 13, 'cmip6.ocean.boundary_forcing.boundary_forcing_details', 'Boundary Forcing Details', 'Properties of boundary forcing', 'cmip6.ocean.boundary_forcing.boundary_forcing_details.surface_pressure', 1, 'Surface Pressure', 'Describe how surface pressure is transmitted to ocean (via sea-ice, nothing specific,...)', '1.1', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:unknown', 10000, '2017-03-05 16:49:34', 'pamv', NULL, NULL),
(10065, 13, 'cmip6.ocean.boundary_forcing.boundary_forcing_details', 'Boundary Forcing Details', 'Properties of boundary forcing', 'cmip6.ocean.boundary_forcing.boundary_forcing_details.momentum_flux_correction', 2, 'Momentum Flux Correction', 'Describe any type of ocean surface momentum flux correction and, if applicable, how it is applied and where.', '0.1', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-02-15 10:23:37', 'pamv', NULL, NULL),
(10066, 13, 'cmip6.ocean.boundary_forcing.boundary_forcing_details', 'Boundary Forcing Details', 'Properties of boundary forcing', 'cmip6.ocean.boundary_forcing.boundary_forcing_details.tracers_flux_correction', 3, 'Tracers Flux Correction', 'Describe any type of ocean surface tracers flux correction and, if applicable, how it is applied and where.', '0.1', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-02-15 10:25:40', 'pamv', NULL, NULL),
(10067, 13, 'cmip6.ocean.boundary_forcing.boundary_forcing_details', 'Boundary Forcing Details', 'Properties of boundary forcing', 'cmip6.ocean.boundary_forcing.boundary_forcing_details.wave_effects', 4, 'Wave Effects', 'Describe if/how wave effects are modelled at ocean surface.', '1.1', 'str', NULL, NULL, NULL, NULL, 'Craig-Banner wave breaking parametrisation', '', '', '', 'Craig-Banner wave breaking parametrisation', '', '', 10000, '2017-03-05 16:50:08', 'pamv', NULL, NULL),
(10068, 13, 'cmip6.ocean.boundary_forcing.boundary_forcing_details', 'Boundary Forcing Details', 'Properties of boundary forcing', 'cmip6.ocean.boundary_forcing.boundary_forcing_details.river_runoff_budget', 5, 'River Runoff Budget', 'Describe how river runoff from land surface is routed to ocean and any global adjustment done.', '1.1', 'str', NULL, NULL, NULL, NULL, 'TRIP scheme', '', '', '', 'TRIP scheme', '', '', 10000, '2017-02-15 10:26:49', 'pamv', NULL, NULL),
(10069, 13, 'cmip6.ocean.boundary_forcing.boundary_forcing_details', 'Boundary Forcing Details', 'Properties of boundary forcing', 'cmip6.ocean.boundary_forcing.boundary_forcing_details.geothermal_heating', 6, 'Geothermal Heating', 'Describe if/how geothermal heating is present at ocean bottom.', '1.1', 'str', NULL, NULL, NULL, NULL, 'Climatology (Goutorbe et al., 2011)', '', '', '', 'Climatology (Goutorbe et al., 2011)', '', '', 10000, '2017-02-15 10:27:54', 'pamv', NULL, NULL),
(10070, 14, 'cmip6.ocean.boundary_forcing.momentum.bottom_friction', 'Bottom Friction', 'Properties of momentum bottom friction in ocean', 'cmip6.ocean.boundary_forcing.momentum.bottom_friction.type', 1, 'Type', 'Type of momentum bottom friction in ocean', '1.1', 'enum', 'mom_bottom_friction_types', 'mom_bottom_friction_types', 'Type of momentum bottom friction in ocean', 1, '', '', '', 'Non-linear', 'Non-linear', '', '', 10000, '2017-02-09 08:28:21', 'pamv', NULL, NULL),
(10071, 14, 'cmip6.ocean.boundary_forcing.momentum.lateral_friction', 'Lateral Friction', 'Properties of momentum lateral friction in ocean', 'cmip6.ocean.boundary_forcing.momentum.lateral_friction.type', 1, 'Type', 'Type of momentum lateral friction in ocean', '1.1', 'enum', 'mom_lateral_friction_types', 'mom_lateral_friction_types', 'Type of momentum lateral friction in ocean', 1, '', '', '', 'Free-slip', 'Free-slip', '', '', 10000, '2017-02-09 08:28:42', 'pamv', NULL, NULL),
(10072, 15, 'cmip6.ocean.boundary_forcing.tracers.sunlight_penetration', 'Sunlight Penetration', 'Properties of sunlight penetration scheme in ocean', 'cmip6.ocean.boundary_forcing.tracers.sunlight_penetration.scheme', 1, 'Scheme', 'Type of sunlight penetration scheme in ocean', '1.1', 'enum', 'sunlight_penetration_scheme_types', 'sunlight_penetration_scheme_types', 'Type of sunlight penetration scheme in ocean', 1, '', '', '', '3 extinction depth', '3 extinction depth', '', '', 10000, '2017-02-09 08:33:09', 'pamv', NULL, NULL),
(10073, 15, 'cmip6.ocean.boundary_forcing.tracers.sunlight_penetration', 'Sunlight Penetration', 'Properties of sunlight penetration scheme in ocean', 'cmip6.ocean.boundary_forcing.tracers.sunlight_penetration.ocean_colour', 2, 'Ocean Colour', 'Is the ocean sunlight penetration scheme ocean colour dependent ?', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'false', '', '', 'false', '', '', 10000, '2017-02-09 08:33:31', 'pamv', NULL, NULL),
(10074, 15, 'cmip6.ocean.boundary_forcing.tracers.sunlight_penetration', 'Sunlight Penetration', 'Properties of sunlight penetration scheme in ocean', 'cmip6.ocean.boundary_forcing.tracers.sunlight_penetration.extinction_depth', 3, 'Extinction Depth', 'Describe and list extinctions depths for sunlight penetration scheme (if applicable).', '0.1', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:unknown', 10000, '2017-03-05 16:44:53', 'pamv', NULL, NULL),
(10075, 15, 'cmip6.ocean.boundary_forcing.tracers.fresh_water_forcing', 'Fresh Water Forcing', 'Properties of surface fresh water forcing in ocean', 'cmip6.ocean.boundary_forcing.tracers.fresh_water_forcing.from_atmopshere', 1, 'From Atmopshere', 'Type of surface fresh water forcing from atmos in ocean', '1.1', 'enum', 'surface_fresh_water_forcing_atmos_types', 'surface_fresh_water_forcing_atmos_types', 'Types of surface fresh water forcing from atmosphere in ocean', 1, '', '', '', 'Freshwater flux', 'Freshwater flux', '', '', 10000, '2017-02-09 08:29:39', 'pamv', NULL, NULL),
(10076, 15, 'cmip6.ocean.boundary_forcing.tracers.fresh_water_forcing', 'Fresh Water Forcing', 'Properties of surface fresh water forcing in ocean', 'cmip6.ocean.boundary_forcing.tracers.fresh_water_forcing.from_sea_ice', 2, 'From Sea Ice', 'Type of surface fresh water forcing from sea-ice in ocean', '1.1', 'enum', 'surface_fresh_water_forcing_seaice_types', 'surface_fresh_water_forcing_seaice_types', 'Types of surface fresh water forcing from sea-ice in ocean', 1, '', '', '', '', NULL, '', 'nil:unknown', 10000, '2017-03-05 16:46:17', 'pamv', NULL, NULL),
(10077, 15, 'cmip6.ocean.boundary_forcing.tracers.fresh_water_forcing', 'Fresh Water Forcing', 'Properties of surface fresh water forcing in ocean', 'cmip6.ocean.boundary_forcing.tracers.fresh_water_forcing.forced_mode_restoring', 3, 'Forced Mode Restoring', 'Type of surface salinity restoring in forced mode (OMIP)', '1.1', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:unknown', 10000, '2017-03-05 16:47:07', 'pamv', NULL, NULL),
(10078, 16, 'cmip6.ocean.key_properties.general', 'General', 'General key properties in ocean', 'cmip6.ocean.key_properties.general.model_family', 1, 'Model Family', 'Type of ocean model.', '1.1', 'enum', 'model_family_types', 'model_family_types', 'Types of ocean models', 1, '', '', '', 'OGCM', 'OGCM', '', '', 10000, '2017-02-10 15:06:44', 'pamv', NULL, NULL),
(10079, 16, 'cmip6.ocean.key_properties.general', 'General', 'General key properties in ocean', 'cmip6.ocean.key_properties.general.basic_approximations', 2, 'Basic Approximations', 'Basic approximations made in the ocean.', '1.N', 'enum', 'ocean_basic_approx_types', 'ocean_basic_approx_types', 'Types of basic approximation in ocean', 1, '', '', '', 'Boussinesq,Primitive equations', 'Boussinesq,Primitive equations', '', '', 10000, '2017-02-10 15:12:01', 'pamv', NULL, NULL),
(10080, 16, 'cmip6.ocean.key_properties.general', 'General', 'General key properties in ocean', 'cmip6.ocean.key_properties.general.prognostic_variables', 3, 'Prognostic Variables', 'List of prognostic variables in the ocean component.', '1.N', 'enum', 'prognostic_vars_types', 'prognostic_vars_types', 'List of prognostic variables in ocean', 1, '', '', '', 'Potential temperature,Salinity,U-velocity,V-velocity', 'Potential temperature,Salinity,U-velocity,V-velocity', '', '', 10000, '2017-02-10 15:09:19', 'pamv', NULL, NULL),
(10081, 16, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.eos_type', 1, 'Eos Type', 'Type of EOS for sea water', '1.1', 'enum', 'seawater_eos_types', 'seawater_eos_types', 'Types of seawater Equation of State in ocean', 1, '', '', '', 'Polynomial EOS-80', 'Polynomial EOS-80', '', '', 10000, '2017-02-10 15:25:03', 'pamv', NULL, NULL),
(10082, 16, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.eos_functional_temp', 2, 'Eos Functional Temp', 'Temperature used in EOS for sea water', '1.1', 'enum', 'seawater_eos_func_temp', 'seawater_eos_func_temp', 'Types of temperature used in EOS in ocean', 1, '', '', '', 'Potential temperature', 'Potential temperature', '', '', 10000, '2017-02-10 15:14:06', 'pamv', NULL, NULL),
(10083, 16, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.eos_functional_salt', 3, 'Eos Functional Salt', 'Salinity used in EOS for sea water', '1.1', 'enum', 'seawater_eos_func_salt', 'seawater_eos_func_salt', 'Types of salinity used in EOS in ocean', 1, '', '', '', 'Practical salinity Sp', 'Practical salinity Sp', '', '', 10000, '2017-02-10 15:14:30', 'pamv', NULL, NULL),
(10084, 16, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.eos_functional_depth', 4, 'Eos Functional Depth', 'Depth or pressure used in EOS for sea water ?', '1.1', 'enum', 'seawater_eos_func_depth', 'seawater_eos_func_depth', 'Types of depth used in EOS in ocean', 1, '', '', '', 'Depth (meters)', 'Depth (meters)', '', '', 10000, '2017-02-10 15:14:51', 'pamv', NULL, NULL),
(10085, 16, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.ocean_freezing_point', 5, 'Ocean Freezing Point', 'Equation used to compute the freezing point (in deg C) of seawater, as a function of salinity and pressure', '1.1', 'enum', 'seawater_freezing_point', 'seawater_freezing_point', 'Types of seawater freezing point equation in ocean', 1, '', '', '', 'UNESCO 1983', 'UNESCO 1983', '', '', 10000, '2017-03-06 12:10:47', 'pamv', NULL, NULL),
(10086, 16, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.ocean_specific_heat', 6, 'Ocean Specific Heat', 'Specific heat in ocean (cpocean) in J/(kg K)', '1.1', 'float', NULL, NULL, NULL, NULL, '3991.86795711963', '', '', '', '3991.8679571196', '', '', 10000, '2017-02-10 15:16:11', 'pamv', NULL, NULL),
(10087, 16, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.ocean_reference_density', 7, 'Ocean Reference Density', 'Boussinesq reference density (rhozero) in kg / m3', '1.1', 'float', NULL, NULL, NULL, NULL, '1026.0', '', '', '', '1026', '', '', 10000, '2017-02-10 15:16:37', 'pamv', NULL, NULL),
(10088, 16, 'cmip6.ocean.key_properties.bathymetry', 'Bathymetry', 'Properties of bathymetry in ocean', 'cmip6.ocean.key_properties.bathymetry.reference_dates', 1, 'Reference Dates', 'Reference date of bathymetry', '1.1', 'enum', 'bathymetry_ref_dates', 'bathymetry_ref_dates', 'List of reference dates for bathymetry in ocean', 1, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-05 17:01:15', 'pamv', NULL, NULL),
(10089, 16, 'cmip6.ocean.key_properties.bathymetry', 'Bathymetry', 'Properties of bathymetry in ocean', 'cmip6.ocean.key_properties.bathymetry.type', 2, 'Type', 'Is the bathymetry fixed in time in the ocean ?', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'true', '', '', 'true', '', '', 10000, '2017-02-10 15:30:46', 'pamv', NULL, NULL),
(10090, 16, 'cmip6.ocean.key_properties.bathymetry', 'Bathymetry', 'Properties of bathymetry in ocean', 'cmip6.ocean.key_properties.bathymetry.ocean_smoothing', 3, 'Ocean Smoothing', 'Describe any smoothing or hand editing of bathymetry in ocean', '1.1', 'str', NULL, NULL, NULL, NULL, 'Smoothed coastline at Antarctica to avoid single grid point inlets', '', '', '', 'Smoothed coastline at Antarctica to avoid single grid point inlets', '', '', 10000, '2017-03-05 17:03:37', 'pamv', NULL, NULL),
(10091, 16, 'cmip6.ocean.key_properties.bathymetry', 'Bathymetry', 'Properties of bathymetry in ocean', 'cmip6.ocean.key_properties.bathymetry.source', 4, 'Source', 'Describe source of bathymetry in ocean', '1.1', 'str', NULL, NULL, NULL, NULL, 'ETOPO1, GEBCO, IBSCO', '', '', '', 'ETOPO1, GEBCO, IBSCO', '', '', 10000, '2017-03-05 17:05:17', 'pamv', NULL, NULL),
(10092, 16, 'cmip6.ocean.key_properties.nonoceanic_waters', 'Nonoceanic Waters', 'Non oceanic waters treatement in ocean', 'cmip6.ocean.key_properties.nonoceanic_waters.isolated_seas', 1, 'Isolated Seas', 'Describe if/how isolated seas is performed', '0.1', 'str', NULL, NULL, NULL, NULL, 'Caspian Sea as ocean points', '', '', '', 'Caspian Sea as ocean points', '', '', 10000, '2017-03-05 17:06:26', 'pamv', NULL, NULL),
(10093, 16, 'cmip6.ocean.key_properties.nonoceanic_waters', 'Nonoceanic Waters', 'Non oceanic waters treatement in ocean', 'cmip6.ocean.key_properties.nonoceanic_waters.river_mouth', 2, 'River Mouth', 'Describe if/how river mouth mixing or estuaries specific treatment is performed', '0.1', 'str', NULL, NULL, NULL, NULL, 'none', '', '', '', 'none', '', '', 10000, '2017-02-10 15:39:04', 'pamv', NULL, NULL),
(10094, 16, 'cmip6.ocean.key_properties.resolution', 'Resolution', 'Resolution in the ocean grid', 'cmip6.ocean.key_properties.resolution.name', 1, 'Name', 'This is a string usually used by the modelling group to describe the resolution of this grid, e.g. ORCA025, N512L180, T512L70 etc.', '1.1', 'str', NULL, NULL, NULL, NULL, 'ORCA1', '', '', '', 'ORCA1', '', '', 10000, '2017-02-10 15:26:12', 'pamv', NULL, NULL),
(10095, 16, 'cmip6.ocean.key_properties.resolution', 'Resolution', 'Resolution in the ocean grid', 'cmip6.ocean.key_properties.resolution.canonical_horizontal_resolution', 2, 'Canonical Horizontal Resolution', 'Expression quoted for gross comparisons of resolution, eg. 50km or 0.1 degrees etc.', '0.1', 'str', NULL, NULL, NULL, NULL, '1 degree', '', '', '', '1 degree', '', '', 10000, '2017-02-10 15:27:21', 'pamv', NULL, NULL),
(10096, 16, 'cmip6.ocean.key_properties.resolution', 'Resolution', 'Resolution in the ocean grid', 'cmip6.ocean.key_properties.resolution.number_of_horizontal_gridpoints', 3, 'Number Of Horizontal Gridpoints', 'Total number of horizontal (XY) points (or degrees of freedom) on computational grid.', '0.1', 'int', NULL, NULL, NULL, NULL, '120184', '', '', '', '120184', '', '', 10000, '2017-02-10 15:27:45', 'pamv', NULL, NULL),
(10097, 16, 'cmip6.ocean.key_properties.resolution', 'Resolution', 'Resolution in the ocean grid', 'cmip6.ocean.key_properties.resolution.number_of_vertical_levels', 4, 'Number Of Vertical Levels', 'Number of vertical levels resolved on computational grid.', '0.1', 'int', NULL, NULL, NULL, NULL, '75', '', '', '', '75', '', '', 10000, '2017-02-28 21:57:51', 'admin', NULL, NULL),
(10098, 16, 'cmip6.ocean.key_properties.resolution', 'Resolution', 'Resolution in the ocean grid', 'cmip6.ocean.key_properties.resolution.is_adaptive_grid', 5, 'Is Adaptive Grid', 'Default is False. Set true if grid resolution changes during execution.', '0.1', 'bool', NULL, NULL, NULL, NULL, '', 'false', '', '', 'false', '', '', 10000, '2017-02-10 15:28:27', 'pamv', NULL, NULL),
(10099, 16, 'cmip6.ocean.key_properties.resolution', 'Resolution', 'Resolution in the ocean grid', 'cmip6.ocean.key_properties.resolution.thickness_level_1', 6, 'Thickness Level 1', 'Thickness of first surface ocean level (in meters)', '1.1', 'float', NULL, NULL, NULL, NULL, '1.0', '', '', '', '1', '', '', 10000, '2017-02-10 15:28:42', 'pamv', NULL, NULL),
(10100, 16, 'cmip6.ocean.key_properties.tuning_applied', 'Tuning Applied', 'Tuning methodology for ocean component', 'cmip6.ocean.key_properties.tuning_applied.description', 1, 'Description', 'General overview description of tuning: explain and motivate the main targets and metrics retained. &Document the relative weight given to climate performance metrics versus process oriented metrics, &and on the possible conflicts with parameterization level tuning. In particular describe any struggle &with a parameter value that required pushing it to its limits to solve a particular model deficiency.', '1.1', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-03-05 17:09:28', 'pamv', NULL, NULL),
(10101, 16, 'cmip6.ocean.key_properties.tuning_applied', 'Tuning Applied', 'Tuning methodology for ocean component', 'cmip6.ocean.key_properties.tuning_applied.global_mean_metrics_used', 2, 'Global Mean Metrics Used', 'List set of metrics of the global mean state used in tuning model/component', '0.N', 'str', NULL, NULL, NULL, NULL, '', '', '', '', '', '', 'nil:inapplicable', 10000, '2017-03-05 17:10:40', 'pamv', NULL, NULL),
(10102, 16, 'cmip6.ocean.key_properties.tuning_applied', 'Tuning Applied', 'Tuning methodology for ocean component', 'cmip6.ocean.key_properties.tuning_applied.regional_metrics_used', 3, 'Regional Metrics Used', 'List of regional metrics of mean state (e.g THC, AABW, regional means etc) used in tuning model/component', '0.N', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-03-05 17:12:04', 'pamv', NULL, NULL),
(10103, 16, 'cmip6.ocean.key_properties.tuning_applied', 'Tuning Applied', 'Tuning methodology for ocean component', 'cmip6.ocean.key_properties.tuning_applied.trend_metrics_used', 4, 'Trend Metrics Used', 'List observed trend metrics used in tuning model/component', '0.N', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:inapplicable', 10000, '2017-03-05 17:12:18', 'pamv', NULL, NULL),
(10104, 16, 'cmip6.ocean.key_properties.conservation', 'Conservation', 'Conservation in the ocean component', 'cmip6.ocean.key_properties.conservation.description', 1, 'Description', 'Brief description of conservation methodology', '1.1', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:unknown', 10000, '2017-03-05 17:14:17', 'pamv', NULL, NULL),
(10105, 16, 'cmip6.ocean.key_properties.conservation', 'Conservation', 'Conservation in the ocean component', 'cmip6.ocean.key_properties.conservation.scheme', 2, 'Scheme', 'Properties conserved in the ocean by the numerical schemes', '1.N', 'enum', 'conservation_props_types', 'conservation_props_types', 'List of properties that can be conserved in ocean', 1, '', '', '', 'Salt,Heat', 'Salt,Heat', '', '', 10000, '2017-03-05 17:15:33', 'pamv', NULL, NULL),
(10106, 16, 'cmip6.ocean.key_properties.conservation', 'Conservation', 'Conservation in the ocean component', 'cmip6.ocean.key_properties.conservation.consistency_properties', 3, 'Consistency Properties', 'Any additional consistency properties (energy conversion, pressure gradient discretisation, ...)?', '0.1', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:unknown', 10000, '2017-03-05 17:17:02', 'pamv', NULL, NULL),
(10107, 16, 'cmip6.ocean.key_properties.conservation', 'Conservation', 'Conservation in the ocean component', 'cmip6.ocean.key_properties.conservation.corrected_conserved_prognostic_variables', 4, 'Corrected Conserved Prognostic Variables', 'Set of variables which are conserved by *more* than the numerical scheme alone.', '0.1', 'str', NULL, NULL, NULL, NULL, '', '', '', '', NULL, '', 'nil:unknown', 10000, '2017-03-05 17:17:19', 'pamv', NULL, NULL);
INSERT INTO `mt_property` (`id`, `topicid`, `s_group_id`, `s_group_label`, `s_group_description`, `s_id`, `s_display`, `s_label`, `s_desc`, `s_cardinality`, `s_type`, `s_enum_id`, `s_enum_lbl`, `s_enum_desc`, `s_enum_open`, `tmp_str`, `tmp_bool`, `tmp_enum`, `tmp_enum_open`, `value`, `notes`, `nullreason`, `specifiedby`, `upd_date`, `upd_by`, `esdoc_id`, `esdoc_hash`) VALUES
(10108, 16, 'cmip6.ocean.key_properties.conservation', 'Conservation', 'Conservation in the ocean component', 'cmip6.ocean.key_properties.conservation.was_flux_correction_used', 5, 'Was Flux Correction Used', 'Does conservation involved flux correction ?', '0.1', 'bool', NULL, NULL, NULL, NULL, '', 'false', '', '', 'false', '', '', 10000, '2017-02-10 15:22:41', 'pamv', NULL, NULL),
(10109, 18, 'cmip6.ocean.grid.vertical', 'Vertical', 'Properties of vertical discretisation in ocean', 'cmip6.ocean.grid.vertical.coordinates', 1, 'Coordinates', 'Type of vertical coordinates in ocean', '1.1', 'enum', 'vertical_coordinate_types', 'vertical_coordinate_types', 'Types of vertical coordinates in ocean', 1, '', '', '', 'Z*-coordinate', 'Z*-coordinate', '', '', 10000, '2017-02-09 08:39:20', 'pamv', NULL, NULL),
(10110, 18, 'cmip6.ocean.grid.vertical', 'Vertical', 'Properties of vertical discretisation in ocean', 'cmip6.ocean.grid.vertical.partial_steps', 2, 'Partial Steps', 'Using partial steps with Z or Z* vertical coordinate in ocean ?', '1.1', 'bool', NULL, NULL, NULL, NULL, '', 'true', '', '', 'true', '', '', 10000, '2017-02-09 08:39:41', 'pamv', NULL, NULL),
(10111, 18, 'cmip6.ocean.grid.horizontal', 'Horizontal', 'Type of horizontal discretisation scheme in ocean', 'cmip6.ocean.grid.horizontal.type', 1, 'Type', 'Horizontal grid type', '1.1', 'enum', 'horizontal_grid_types', 'horizontal_grid_types', 'Types of horizonal grid in ocean', 1, '', '', '', 'Two north poles (ORCA-style)', 'Two north poles (ORCA-style)', '', '', 10000, '2017-02-09 08:38:24', 'pamv', NULL, NULL),
(10112, 18, 'cmip6.ocean.grid.horizontal', 'Horizontal', 'Type of horizontal discretisation scheme in ocean', 'cmip6.ocean.grid.horizontal.scheme', 2, 'Scheme', 'Horizontal discretisation scheme in ocean', '1.1', 'enum', 'horizontal_scheme_types', 'horizontal_scheme_types', 'Types of horizonal scheme in ocean', 1, '', '', '', 'Finite difference / Arakawa C-grid', 'Finite difference / Arakawa C-grid', '', '', 10000, '2017-02-09 08:38:55', 'pamv', NULL, NULL),
(10113, 19, 'cmip6.ocean.timestepping_framework.timestepping_attributes', 'Timestepping Attributes', 'Properties of time stepping in ocean', 'cmip6.ocean.timestepping_framework.timestepping_attributes.time_step', 1, 'Time Step', 'Ocean time step in seconds', '1.1', 'int', '', '', '', 0, '900', '', '', '', '900', '', '', 10000, '2017-03-22 11:00:24', 'pamv', NULL, NULL),
(10114, 19, 'cmip6.ocean.timestepping_framework.timestepping_attributes', 'Timestepping Attributes', 'Properties of time stepping in ocean', 'cmip6.ocean.timestepping_framework.timestepping_attributes.diurnal_cycle', 2, 'Diurnal Cycle', 'Diurnal cycle type', '1.1', 'enum', 'diurnal_cycle_types', 'diurnal_cycle_types', 'Types of diurnal cycle resolution in ocean', 1, '', '', '', 'Via coupling', 'Via coupling', '', '', 10000, '2017-03-14 21:28:52', 'clone_10001', NULL, NULL),
(10115, 19, 'cmip6.ocean.timestepping_framework.timestepping_tracers_scheme', 'Timestepping Tracers Scheme', 'Properties of tracers time stepping in ocean', 'cmip6.ocean.timestepping_framework.timestepping_tracers_scheme.tracers', 1, 'Tracers', 'Time stepping tracer scheme', '1.1', 'enum', 'ocean_timestepping_types', 'ocean_timestepping_types', 'Type of timestepping scheme in ocean', 1, '', '', '', 'Leap-frog + Asselin filter', 'Leap-frog + Asselin filter', '', '', 10000, '2017-03-14 21:28:52', 'clone_10002', NULL, NULL),
(10116, 19, 'cmip6.ocean.timestepping_framework.barotropic_solver_scheme', 'Barotropic Solver Scheme', 'Barotropic solver in ocean', 'cmip6.ocean.timestepping_framework.barotropic_solver_scheme.barotropic_solver', 1, 'Barotropic Solver', 'Barotropic solver scheme', '1.1', 'enum', 'ocean_timestepping_types', 'ocean_timestepping_types', 'Type of timestepping scheme in ocean', 1, '', '', '', 'Leap-frog + Asselin filter', 'Leap-frog + Asselin filter', '', '', 10000, '2017-03-14 21:28:52', 'clone_10003', NULL, NULL),
(10117, 19, 'cmip6.ocean.timestepping_framework.barotropic_solver_scheme', 'Barotropic Solver Scheme', 'Barotropic solver in ocean', 'cmip6.ocean.timestepping_framework.barotropic_solver_scheme.type', 2, 'Type', 'Barotropic solver type', '1.1', 'enum', 'barotropic_solver_types', 'barotropic_solver_types', 'Type of barotropic solver in ocean', 1, '', '', '', 'Preconditioned conjugate gradient', 'Preconditioned conjugate gradient', '', '', 10000, '2017-03-14 21:28:52', 'clone_10004', NULL, NULL),
(10118, 19, 'cmip6.ocean.timestepping_framework.barotropic_momentum_scheme', 'Barotropic Momentum Scheme', 'Barotropic momentum solver in ocean', 'cmip6.ocean.timestepping_framework.barotropic_momentum_scheme.barotropic_momentum', 1, 'Barotropic Momentum', 'Barotropic momentum scheme', '1.1', 'enum', 'ocean_timestepping_types', 'ocean_timestepping_types', 'Type of timestepping scheme in ocean', 1, '', '', '', 'Leap-frog + Asselin filter', 'Leap-frog + Asselin filter', '', '', 10000, '2017-03-14 21:28:52', 'clone_10005', NULL, NULL),
(10119, 21, '', '', '', 'cmip6.ocean.advection.momentum.type', 1, 'Type', 'Type of lateral momemtum advection scheme in ocean', '1.1', 'enum', 'adv_mom_scheme_types', 'adv_mom_scheme_types', 'Type of lateral momemtum advection scheme in ocean', 1, '', '', '', 'Vector form', 'Vector form', '', '', 10000, '2017-03-14 21:28:52', 'clone_10006', NULL, NULL),
(10120, 21, '', '', '', 'cmip6.ocean.advection.momentum.scheme_name', 2, 'Scheme Name', 'Name of ocean momemtum advection scheme', '1.1', 'str', '', '', '', 0, 'Energy and ENstrophy conservative scheme (EEN)', '', '', '', 'Energy and ENstrophy conservative scheme (EEN)', '', '', 10000, '2017-03-14 21:28:52', 'clone_10007', NULL, NULL),
(10121, 21, '', '', '', 'cmip6.ocean.advection.momentum.ALE', 3, 'ALE', 'Using ALE for vertical advection ? (if vertical coordinates are sigma)', '0.1', 'bool', '', '', '', 0, '', '', '', '', '', '', 'nil:inapplicable', 10000, '2017-03-14 21:28:52', 'clone_10008', NULL, NULL),
(10122, 22, '', '', '', 'cmip6.ocean.advection.lateral_tracers.type', 1, 'Type', 'Type of lateral tracer advection scheme in ocean', '1.1', 'enum', 'adv_tra_scheme_types', 'adv_tra_scheme_types', 'Type of tracer advection scheme in ocean', 1, '', '', '', 'Total Variance Dissipation (TVD)', 'Total Variance Dissipation (TVD)', '', '', 10000, '2017-03-14 21:28:52', 'clone_10009', NULL, NULL),
(10123, 22, '', '', '', 'cmip6.ocean.advection.lateral_tracers.flux_limiter', 2, 'Flux Limiter', 'Monotonic flux limiter for vertical tracer advection scheme in ocean ?', '1.1', 'bool', '', '', '', 0, '', 'false', '', '', 'false', '', '', 10000, '2017-03-14 21:28:52', 'clone_10010', NULL, NULL),
(10124, 22, '', '', '', 'cmip6.ocean.advection.lateral_tracers.passive_tracers', 3, 'Passive Tracers', 'Passive tracers advected', '0.N', 'enum', 'passive_tracers_list', 'passive_tracers_list', 'Passive tracers in ocean', 1, '', '', '', '', '', '', 'nil:inapplicable', 10000, '2017-03-14 21:28:52', 'clone_10011', NULL, NULL),
(10125, 22, '', '', '', 'cmip6.ocean.advection.lateral_tracers.passive_tracers_advection', 4, 'Passive Tracers Advection', 'Is advection of passive tracers different than active ? if so, describe.', '0.1', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-14 21:28:52', 'clone_10012', NULL, NULL),
(10126, 23, '', '', '', 'cmip6.ocean.advection.vertical_tracers.type', 1, 'Type', 'Type of vertical tracer advection scheme in ocean', '1.1', 'enum', 'adv_tra_scheme_types', 'adv_tra_scheme_types', 'Type of tracer advection scheme in ocean', 1, '', '', '', 'Total Variance Dissipation (TVD)', 'Total Variance Dissipation (TVD)', '', '', 10000, '2017-03-14 21:28:52', 'clone_10013', NULL, NULL),
(10127, 23, '', '', '', 'cmip6.ocean.advection.vertical_tracers.flux_limiter', 2, 'Flux Limiter', 'Monotonic flux limiter for vertical tracer advection scheme in ocean ?', '1.1', 'bool', '', '', '', 0, '', 'false', '', '', 'false', '', '', 10000, '2017-03-14 21:28:52', 'clone_10014', NULL, NULL),
(10128, 24, 'cmip6.ocean.lateral_physics.ocean_transient_eddy_representation', 'Ocean Transient Eddy Representation', 'Type of transient eddy representation in ocean', 'cmip6.ocean.lateral_physics.ocean_transient_eddy_representation.scheme', 1, 'Scheme', 'Type of transient eddy representation in ocean', '1.1', 'enum', 'latphys_transient_eddy_types', 'latphys_transient_eddy_types', 'Type of transient eddy representation in ocean', 1, '', '', '', 'None', 'None', '', '', 10000, '2017-03-14 21:28:52', 'clone_10015', NULL, NULL),
(10129, 25, 'cmip6.ocean.lateral_physics.momentum.operator', 'Operator', 'Properties of lateral physics operator for momentum in ocean', 'cmip6.ocean.lateral_physics.momentum.operator.direction', 1, 'Direction', 'Direction of lateral physics momemtum scheme in the ocean', '1.1', 'enum', 'latphys_operator_direc_types', 'latphys_operator_direc_types', 'Type of lateral physics direction in ocean', 1, '', '', '', 'Geopotential', 'Geopotential', '', '', 10000, '2017-03-14 21:28:52', 'clone_10016', NULL, NULL),
(10130, 25, 'cmip6.ocean.lateral_physics.momentum.operator', 'Operator', 'Properties of lateral physics operator for momentum in ocean', 'cmip6.ocean.lateral_physics.momentum.operator.order', 2, 'Order', 'Order of lateral physics momemtum scheme in the ocean', '1.1', 'enum', 'latphys_operator_order_types', 'latphys_operator_order_types', 'Type of lateral physics order in ocean', 1, '', '', '', 'Bi-harmonic', 'Bi-harmonic', '', '', 10000, '2017-03-22 10:35:52', 'pamv', NULL, NULL),
(10131, 25, 'cmip6.ocean.lateral_physics.momentum.operator', 'Operator', 'Properties of lateral physics operator for momentum in ocean', 'cmip6.ocean.lateral_physics.momentum.operator.discretisation', 3, 'Discretisation', 'Discretisation of lateral physics momemtum scheme in the ocean', '1.1', 'enum', 'latphys_operator_discret_types', 'latphys_operator_discret_types', 'Type of lateral physics discretisation in ocean', 1, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-14 21:28:52', 'clone_10018', NULL, NULL),
(10132, 25, 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics momemtum scheme in the ocean', 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff.type', 1, 'Type', 'Lateral physics momemtum eddy viscosity coeff type in the ocean', '1.1', 'enum', 'latphys_eddy_visc_coeff_types', 'latphys_eddy_visc_coeff_types', 'Type of lateral physics eddy viscosity coeff in ocean', 1, '', '', '', 'Space varying', 'Space varying', '', '', 10000, '2017-03-14 21:28:52', 'clone_10019', NULL, NULL),
(10133, 25, 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics momemtum scheme in the ocean', 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff.constant_coefficient', 2, 'Constant Coefficient', 'If constant, value of eddy viscosity coeff in lateral physics momemtum scheme (in m2/s)', '0.1', 'int', '', '', '', 0, '', '', '', '', '', '', 'nil:inapplicable', 10000, '2017-03-14 21:28:52', 'clone_10020', NULL, NULL),
(10134, 25, 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics momemtum scheme in the ocean', 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff.variable_coefficient', 3, 'Variable Coefficient', 'If space-varying, describe variations of eddy viscosity coeff in lateral physics momemtum scheme', '0.1', 'str', '', '', '', 0, '-1.5e11 m4/s at equator reducing with cube of grid spacing\r\n', '', '', '', '-1.5e11 m4/s at equator reducing with cube of grid spacing\r\n', '', '', 10000, '2017-03-22 10:38:11', 'pamv', NULL, NULL),
(10135, 25, 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics momemtum scheme in the ocean', 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff.coeff_background', 4, 'Coeff Background', 'Background value of eddy viscosity coeff in lateral physics momemtum scheme (in m2/s)', '1.1', 'int', '', '', '', 0, '0', '', '', '', '0', '', '', 10000, '2017-03-22 10:39:06', 'pamv', NULL, NULL),
(10136, 25, 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics momemtum scheme in the ocean', 'cmip6.ocean.lateral_physics.momentum.eddy_viscosity_coeff.coeff_backscatter', 5, 'Coeff Backscatter', 'Is there backscatter in eddy viscosity coeff in lateral physics momemtum scheme ?', '1.1', 'bool', '', '', '', 0, '', 'false', '', '', 'false', '', '', 10000, '2017-03-14 21:28:52', 'clone_10023', NULL, NULL),
(10137, 26, '', '', '', 'cmip6.ocean.lateral_physics.tracers.mesoscale_closure', 1, 'Mesoscale Closure', 'Is there a mesoscale closure in the lateral physics tracers scheme ?', '1.1', 'bool', '', '', '', 0, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-22 10:40:50', 'pamv', NULL, NULL),
(10138, 26, '', '', '', 'cmip6.ocean.lateral_physics.tracers.submesoscale_mixing', 2, 'Submesoscale Mixing', 'Is there a submesoscale mixing parameterisation (i.e Fox-Kemper) in the lateral physics tracers scheme ?', '1.1', 'bool', '', '', '', 0, '', 'false', '', '', 'false', '', '', 10000, '2017-03-14 21:28:52', 'clone_10025', NULL, NULL),
(10139, 26, 'cmip6.ocean.lateral_physics.tracers.operator', 'Operator', 'Properties of lateral physics operator for tracers in ocean', 'cmip6.ocean.lateral_physics.tracers.operator.direction', 1, 'Direction', 'Direction of lateral physics tracers scheme in the ocean', '1.1', 'enum', 'latphys_operator_direc_types', 'latphys_operator_direc_types', 'Type of lateral physics direction in ocean', 1, '', '', '', 'Isoneutral', 'Isoneutral', '', '', 10000, '2017-03-14 21:28:52', 'clone_10026', NULL, NULL),
(10140, 26, 'cmip6.ocean.lateral_physics.tracers.operator', 'Operator', 'Properties of lateral physics operator for tracers in ocean', 'cmip6.ocean.lateral_physics.tracers.operator.order', 2, 'Order', 'Order of lateral physics tracers scheme in the ocean', '1.1', 'enum', 'latphys_operator_order_types', 'latphys_operator_order_types', 'Type of lateral physics order in ocean', 1, '', '', '', 'Harmonic', 'Harmonic', '', '', 10000, '2017-03-14 21:28:52', 'clone_10027', NULL, NULL),
(10141, 26, 'cmip6.ocean.lateral_physics.tracers.operator', 'Operator', 'Properties of lateral physics operator for tracers in ocean', 'cmip6.ocean.lateral_physics.tracers.operator.discretisation', 3, 'Discretisation', 'Discretisation of lateral physics tracers scheme in the ocean', '1.1', 'enum', 'latphys_operator_discret_types', 'latphys_operator_discret_types', 'Type of lateral physics discretisation in ocean', 1, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-14 21:28:52', 'clone_10028', NULL, NULL),
(10142, 26, 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff.type', 1, 'Type', 'Lateral physics tracers eddy viscosity coeff type in the ocean', '1.1', 'enum', 'latphys_eddy_visc_coeff_types', 'latphys_eddy_visc_coeff_types', 'Type of lateral physics eddy viscosity coeff in ocean', 1, '', '', '', 'Space varying', 'Space varying', '', '', 10000, '2017-03-14 21:28:52', 'clone_10029', NULL, NULL),
(10143, 26, 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff.constant_coefficient', 2, 'Constant Coefficient', 'If constant, value of eddy viscosity coeff in lateral physics tracers scheme (in m2/s)', '0.1', 'int', '', '', '', 0, '', '', '', '', '', '', 'nil:inapplicable', 10000, '2017-03-14 21:28:52', 'clone_10030', NULL, NULL),
(10144, 26, 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff.variable_coefficient', 3, 'Variable Coefficient', 'If space-varying, describe variations of eddy viscosity coeff in lateral physics tracers scheme', '0.1', 'str', '', '', '', 0, '150 m2/s at equator reducing linearly with the grid spacing', '', '', '', '150 m2/s at equator reducing linearly with the grid spacing', '', '', 10000, '2017-03-22 10:43:34', 'pamv', NULL, NULL),
(10145, 26, 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff.coeff_background', 4, 'Coeff Background', 'Background value of eddy viscosity coeff in lateral physics tracers scheme (in m2/s)', '1.1', 'int', '', '', '', 0, '0', '', '', '', '0', '', '', 10000, '2017-03-14 21:28:52', 'clone_10032', NULL, NULL),
(10146, 26, 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff', 'Eddy Viscosity Coeff', 'Properties of eddy viscosity coeff in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_viscosity_coeff.coeff_backscatter', 5, 'Coeff Backscatter', 'Is there backscatter in eddy viscosity coeff in lateral physics tracers scheme ?', '1.1', 'bool', '', '', '', 0, '', 'false', '', '', 'false', '', '', 10000, '2017-03-14 21:28:52', 'clone_10033', NULL, NULL),
(10147, 26, 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity', 'Eddy Induced Velocity', 'Properties of eddy induced velocity (EIV) in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity.type', 1, 'Type', 'Type of EIV in lateral physics tracers in the ocean', '1.1', 'enum', 'latphys_eiv_types', 'latphys_eiv_types', 'Type of lateral physics eddy induced velocity in ocean', 1, '', '', '', '', 'HL', '', 'nil:inapplicable', 10000, '2017-03-22 10:45:16', 'pamv', NULL, NULL),
(10148, 26, 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity', 'Eddy Induced Velocity', 'Properties of eddy induced velocity (EIV) in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity.constant_val', 2, 'Constant Val', 'If EIV scheme for tracers is constant, specify coefficient value (M2/s)', '0.1', 'int', '', '', '', 0, '', '', '', '', '', '', 'nil:inapplicable', 10000, '2017-03-14 21:28:52', 'clone_10035', NULL, NULL),
(10149, 26, 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity', 'Eddy Induced Velocity', 'Properties of eddy induced velocity (EIV) in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity.flux_type', 3, 'Flux Type', 'Type of EIV flux (advective or skew)', '1.1', 'str', '', '', '', 0, '', '', '', '', 'Advective', '', 'nil:inapplicable', 10000, '2017-03-22 10:49:40', 'pamv', NULL, NULL),
(10150, 26, 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity', 'Eddy Induced Velocity', 'Properties of eddy induced velocity (EIV) in lateral physics tracers scheme in the ocean', 'cmip6.ocean.lateral_physics.tracers.eddy_induced_velocity.added_diffusivity', 4, 'Added Diffusivity', 'Type of EIV added diffusivity (constant, flow dependent or none)', '1.1', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:inapplicable', 10000, '2017-03-14 21:28:52', 'clone_10037', NULL, NULL),
(10151, 28, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.details', 'Details', 'Properties of vertical physics in ocean', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.details.langmuir_cells_mixing', 1, 'Langmuir Cells Mixing', 'Is there Langmuir cells mixing in upper ocean ?', '1.1', 'bool', '', '', '', 0, '', 'true', '', '', 'true', '', '', 10000, '2017-03-14 21:28:52', 'clone_10038', NULL, NULL),
(10152, 28, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers', 'Tracers', 'Properties of boundary layer (BL) mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers.type', 1, 'Type', 'Type of boundary layer mixing for tracers in ocean', '1.1', 'enum', 'bndlayer_mixing_types', 'bndlayer_mixing_types', 'Types of boundary layer mixing in ocean', 1, '', '', '', 'Turbulent closure - TKE', 'Turbulent closure - TKE', '', '', 10000, '2017-03-14 21:28:52', 'clone_10039', NULL, NULL),
(10153, 28, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers', 'Tracers', 'Properties of boundary layer (BL) mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers.closure_order', 2, 'Closure Order', 'If turbulent BL mixing of tracers, specific order of closure (0, 1, 2.5, 3)', '0.1', 'float', '', '', '', 0, '1.5', '', '', '', '1.5', '', '', 10000, '2017-03-14 21:28:52', 'clone_10040', NULL, NULL),
(10154, 28, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers', 'Tracers', 'Properties of boundary layer (BL) mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers.constant', 3, 'Constant', 'If constant BL mixing of tracers, specific coefficient (m2/s)', '0.1', 'int', '', '', '', 0, '', '', '', '', '', '', 'nil:inapplicable', 10000, '2017-03-14 21:28:52', 'clone_10041', NULL, NULL),
(10155, 28, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers', 'Tracers', 'Properties of boundary layer (BL) mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.tracers.background', 4, 'Background', 'Background BL mixing of tracers coefficient, (schema and value in m2/s - may by none)', '1.1', 'str', '', '', '', 0, 'constant but reduced in tropics, 1.2e-5 m2/s', '', '', '', 'constant but reduced in tropics, 1.2e-5 m2/s', '', '', 10000, '2017-03-14 21:28:52', 'clone_10042', NULL, NULL),
(10156, 28, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum', 'Momentum', 'Properties of boundary layer (BL) mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum.type', 1, 'Type', 'Type of boundary layer mixing for momentum in ocean', '1.1', 'enum', 'bndlayer_mixing_types', 'bndlayer_mixing_types', 'Types of boundary layer mixing in ocean', 1, '', '', '', 'Turbulent closure - TKE', 'Turbulent closure - TKE', '', '', 10000, '2017-03-14 21:28:52', 'clone_10043', NULL, NULL),
(10157, 28, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum', 'Momentum', 'Properties of boundary layer (BL) mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum.closure_order', 2, 'Closure Order', 'If turbulent BL mixing of momentum, specific order of closure (0, 1, 2.5, 3)', '0.1', 'float', '', '', '', 0, '1.5', '', '', '', '1.5', '', '', 10000, '2017-03-14 21:28:52', 'clone_10044', NULL, NULL),
(10158, 28, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum', 'Momentum', 'Properties of boundary layer (BL) mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum.constant', 3, 'Constant', 'If constant BL mixing of momentum, specific coefficient (m2/s)', '0.1', 'int', '', '', '', 0, '', '', '', '', '', '', 'nil:inapplicable', 10000, '2017-03-14 21:28:52', 'clone_10045', NULL, NULL),
(10159, 28, 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum', 'Momentum', 'Properties of boundary layer (BL) mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.boundary_layer_mixing.momentum.background', 4, 'Background', 'Background BL mixing of momentum coefficient, (schema and value in m2/s - may by none)', '1.1', 'str', '', '', '', 0, 'constant, 1.2e-5 m2/s', '', '', '', 'constant, 1.2e-5 m2/s', '', '', 10000, '2017-03-14 21:28:52', 'clone_10046', NULL, NULL),
(10160, 29, 'cmip6.ocean.vertical_physics.interior_mixing.details', 'Details', 'Properties of interior mixing in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.details.convection_type', 1, 'Convection Type', 'Type of vertical convection in ocean', '1.1', 'enum', 'vertphys_convection_types', 'vertphys_convection_types', 'Types of convection scheme in ocean', 1, '', '', '', 'Enhanced vertical diffusion', 'Enhanced vertical diffusion', '', '', 10000, '2017-03-14 21:28:52', 'clone_10047', NULL, NULL),
(10161, 29, 'cmip6.ocean.vertical_physics.interior_mixing.details', 'Details', 'Properties of interior mixing in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.details.tide_induced_mixing', 2, 'Tide Induced Mixing', 'Describe how tide induced mixing is modelled (barotropic, baroclinic, none)', '1.1', 'str', '', '', '', 0, 'baroclinic based on climatologies', '', '', '', 'baroclinic based on climatologies', '', '', 10000, '2017-03-14 21:28:52', 'clone_10048', NULL, NULL),
(10162, 29, 'cmip6.ocean.vertical_physics.interior_mixing.details', 'Details', 'Properties of interior mixing in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.details.double_diffusion', 3, 'Double Diffusion', 'Is there double diffusion', '1.1', 'bool', '', '', '', 0, '', 'true', '', '', 'true', '', '', 10000, '2017-03-14 21:28:52', 'clone_10049', NULL, NULL),
(10163, 29, 'cmip6.ocean.vertical_physics.interior_mixing.details', 'Details', 'Properties of interior mixing in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.details.shear_mixing', 4, 'Shear Mixing', 'Is there interior shear mixing', '1.1', 'bool', '', '', '', 0, '', 'false', '', '', 'false', '', '', 10000, '2017-03-14 21:28:52', 'clone_10050', NULL, NULL),
(10164, 29, 'cmip6.ocean.vertical_physics.interior_mixing.tracers', 'Tracers', 'Properties of interior mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.tracers.type', 1, 'Type', 'Type of interior mixing for tracers in ocean', '1.1', 'enum', 'interior_mixing_types', 'interior_mixing_types', 'Types of interior mixing in ocean', 1, '', '', '', 'Turbulent closure / TKE', 'Turbulent closure / TKE', '', '', 10000, '2017-03-14 21:28:52', 'clone_10051', NULL, NULL),
(10165, 29, 'cmip6.ocean.vertical_physics.interior_mixing.tracers', 'Tracers', 'Properties of interior mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.tracers.constant', 2, 'Constant', 'If constant interior mixing of tracers, specific coefficient (m2/s)', '0.1', 'int', '', '', '', 0, '', '', '', '', '', '', 'nil:inapplicable', 10000, '2017-03-14 21:28:52', 'clone_10052', NULL, NULL),
(10166, 29, 'cmip6.ocean.vertical_physics.interior_mixing.tracers', 'Tracers', 'Properties of interior mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.tracers.profile', 3, 'Profile', 'Is the background interior mixing using a vertical profile for tracers (i.e is NOT constant) ?', '1.1', 'str', '', '', '', 0, 'no profile', '', '', '', 'no profile', '', '', 10000, '2017-03-14 21:28:52', 'clone_10053', NULL, NULL),
(10167, 29, 'cmip6.ocean.vertical_physics.interior_mixing.tracers', 'Tracers', 'Properties of interior mixing on tracers in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.tracers.background', 4, 'Background', 'Background interior mixing of tracers coefficient, (schema and value in m2/s - may by none)', '1.1', 'str', '', '', '', 0, 'constant but reduced at tropics,1.2e-5 m2/s', '', '', '', 'constant but reduced at tropics,1.2e-5 m2/s', '', '', 10000, '2017-03-14 21:28:52', 'clone_10054', NULL, NULL),
(10168, 29, 'cmip6.ocean.vertical_physics.interior_mixing.momentum', 'Momentum', 'Properties of interior mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.momentum.type', 1, 'Type', 'Type of interior mixing for momentum in ocean', '1.1', 'enum', 'interior_mixing_types', 'interior_mixing_types', 'Types of interior mixing in ocean', 1, '', '', '', 'Turbulent closure / TKE', 'Turbulent closure / TKE', '', '', 10000, '2017-03-14 21:28:52', 'clone_10055', NULL, NULL),
(10169, 29, 'cmip6.ocean.vertical_physics.interior_mixing.momentum', 'Momentum', 'Properties of interior mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.momentum.constant', 2, 'Constant', 'If constant interior mixing of momentum, specific coefficient (m2/s)', '0.1', 'int', '', '', '', 0, '1.5', '', '', '', '1', '', '', 10000, '2017-03-14 21:28:52', 'clone_10056', NULL, NULL),
(10170, 29, 'cmip6.ocean.vertical_physics.interior_mixing.momentum', 'Momentum', 'Properties of interior mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.momentum.profile', 3, 'Profile', 'Is the background interior mixing using a vertical profile for momentum (i.e is NOT constant) ?', '1.1', 'str', '', '', '', 0, 'no profile', '', '', '', 'no profile', '', '', 10000, '2017-03-14 21:28:52', 'clone_10057', NULL, NULL),
(10171, 29, 'cmip6.ocean.vertical_physics.interior_mixing.momentum', 'Momentum', 'Properties of interior mixing on momentum in the ocean ', 'cmip6.ocean.vertical_physics.interior_mixing.momentum.background', 4, 'Background', 'Background interior mixing of momentum coefficient, (schema and value in m2/s - may by none)', '1.1', 'str', '', '', '', 0, 'constant, 1.2e-5 m2/s', '', '', '', 'constant, 1.2e-5 m2/s', '', '', 10000, '2017-03-14 21:28:52', 'clone_10058', NULL, NULL),
(10172, 30, 'cmip6.ocean.uplow_boundaries.free_surface', 'Free Surface', 'Properties of free surface in ocean', 'cmip6.ocean.uplow_boundaries.free_surface.scheme', 1, 'Scheme', 'Free surface scheme in ocean', '1.1', 'enum', 'free_surface_types', 'free_surface_types', 'Type of free surface in ocean', 1, '', '', '', 'Non-linear filtered', 'Non-linear filtered', '', '', 10000, '2017-03-14 21:28:52', 'clone_10059', NULL, NULL),
(10173, 30, 'cmip6.ocean.uplow_boundaries.free_surface', 'Free Surface', 'Properties of free surface in ocean', 'cmip6.ocean.uplow_boundaries.free_surface.embeded_seaice', 2, 'Embeded Seaice', 'Is the sea-ice embeded in the ocean model (instead of levitating) ?', '1.1', 'bool', '', '', '', 0, '', 'false', '', '', 'false', '', '', 10000, '2017-03-14 21:28:52', 'clone_10060', NULL, NULL),
(10174, 30, 'cmip6.ocean.uplow_boundaries.bottom_boundary_layer', 'Bottom Boundary Layer', 'Properties of bottom boundary layer in ocean', 'cmip6.ocean.uplow_boundaries.bottom_boundary_layer.type_of_bbl', 1, 'Type Of Bbl', 'Type of bottom boundary layer in ocean', '1.1', 'enum', 'bottom_bl_types', 'bottom_bl_types', 'Type of bottom boundary layer in ocean', 1, '', '', '', 'Advective and Diffusive', 'Advective and Diffusive', '', '', 10000, '2017-03-14 21:28:52', 'clone_10061', NULL, NULL),
(10175, 30, 'cmip6.ocean.uplow_boundaries.bottom_boundary_layer', 'Bottom Boundary Layer', 'Properties of bottom boundary layer in ocean', 'cmip6.ocean.uplow_boundaries.bottom_boundary_layer.lateral_mixing_coef', 2, 'Lateral Mixing Coef', 'If bottom BL is diffusive, specify value of lateral mixing coefficient (in m2/s)', '0.1', 'int', '', '', '', 0, '1000', '', '', '', '1000', '', '', 10000, '2017-03-14 21:28:52', 'clone_10062', NULL, NULL),
(10176, 30, 'cmip6.ocean.uplow_boundaries.bottom_boundary_layer', 'Bottom Boundary Layer', 'Properties of bottom boundary layer in ocean', 'cmip6.ocean.uplow_boundaries.bottom_boundary_layer.sill_overflow', 3, 'Sill Overflow', 'Describe any specific treatment of sill overflows', '1.1', 'str', '', '', '', 0, 'no special treatment', '', '', '', 'no special treatment', '', '', 10000, '2017-03-14 21:28:52', 'clone_10063', NULL, NULL),
(10177, 31, 'cmip6.ocean.boundary_forcing.boundary_forcing_details', 'Boundary Forcing Details', 'Properties of boundary forcing', 'cmip6.ocean.boundary_forcing.boundary_forcing_details.surface_pressure', 1, 'Surface Pressure', 'Describe how surface pressure is transmitted to ocean (via sea-ice, nothing specific,...)', '1.1', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-14 21:28:52', 'clone_10064', NULL, NULL),
(10178, 31, 'cmip6.ocean.boundary_forcing.boundary_forcing_details', 'Boundary Forcing Details', 'Properties of boundary forcing', 'cmip6.ocean.boundary_forcing.boundary_forcing_details.momentum_flux_correction', 2, 'Momentum Flux Correction', 'Describe any type of ocean surface momentum flux correction and, if applicable, how it is applied and where.', '0.1', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:inapplicable', 10000, '2017-03-14 21:28:52', 'clone_10065', NULL, NULL),
(10179, 31, 'cmip6.ocean.boundary_forcing.boundary_forcing_details', 'Boundary Forcing Details', 'Properties of boundary forcing', 'cmip6.ocean.boundary_forcing.boundary_forcing_details.tracers_flux_correction', 3, 'Tracers Flux Correction', 'Describe any type of ocean surface tracers flux correction and, if applicable, how it is applied and where.', '0.1', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:inapplicable', 10000, '2017-03-14 21:28:52', 'clone_10066', NULL, NULL),
(10180, 31, 'cmip6.ocean.boundary_forcing.boundary_forcing_details', 'Boundary Forcing Details', 'Properties of boundary forcing', 'cmip6.ocean.boundary_forcing.boundary_forcing_details.wave_effects', 4, 'Wave Effects', 'Describe if/how wave effects are modelled at ocean surface.', '1.1', 'str', '', '', '', 0, 'Craig-Banner wave breaking parametrisation', '', '', '', 'Craig-Banner wave breaking parametrisation', '', '', 10000, '2017-03-14 21:28:52', 'clone_10067', NULL, NULL),
(10181, 31, 'cmip6.ocean.boundary_forcing.boundary_forcing_details', 'Boundary Forcing Details', 'Properties of boundary forcing', 'cmip6.ocean.boundary_forcing.boundary_forcing_details.river_runoff_budget', 5, 'River Runoff Budget', 'Describe how river runoff from land surface is routed to ocean and any global adjustment done.', '1.1', 'str', '', '', '', 0, 'TRIP scheme', '', '', '', 'TRIP scheme', '', '', 10000, '2017-03-14 21:28:52', 'clone_10068', NULL, NULL),
(10182, 31, 'cmip6.ocean.boundary_forcing.boundary_forcing_details', 'Boundary Forcing Details', 'Properties of boundary forcing', 'cmip6.ocean.boundary_forcing.boundary_forcing_details.geothermal_heating', 6, 'Geothermal Heating', 'Describe if/how geothermal heating is present at ocean bottom.', '1.1', 'str', '', '', '', 0, 'Climatology (Goutorbe et al., 2011)', '', '', '', 'Climatology (Goutorbe et al., 2011)', '', '', 10000, '2017-03-14 21:28:52', 'clone_10069', NULL, NULL),
(10183, 32, 'cmip6.ocean.boundary_forcing.momentum.bottom_friction', 'Bottom Friction', 'Properties of momentum bottom friction in ocean', 'cmip6.ocean.boundary_forcing.momentum.bottom_friction.type', 1, 'Type', 'Type of momentum bottom friction in ocean', '1.1', 'enum', 'mom_bottom_friction_types', 'mom_bottom_friction_types', 'Type of momentum bottom friction in ocean', 1, '', '', '', 'Non-linear', 'Non-linear', '', '', 10000, '2017-03-14 21:28:52', 'clone_10070', NULL, NULL),
(10184, 32, 'cmip6.ocean.boundary_forcing.momentum.lateral_friction', 'Lateral Friction', 'Properties of momentum lateral friction in ocean', 'cmip6.ocean.boundary_forcing.momentum.lateral_friction.type', 1, 'Type', 'Type of momentum lateral friction in ocean', '1.1', 'enum', 'mom_lateral_friction_types', 'mom_lateral_friction_types', 'Type of momentum lateral friction in ocean', 1, '', '', '', 'Free-slip', 'Free-slip', '', '', 10000, '2017-03-14 21:28:52', 'clone_10071', NULL, NULL),
(10185, 33, 'cmip6.ocean.boundary_forcing.tracers.sunlight_penetration', 'Sunlight Penetration', 'Properties of sunlight penetration scheme in ocean', 'cmip6.ocean.boundary_forcing.tracers.sunlight_penetration.scheme', 1, 'Scheme', 'Type of sunlight penetration scheme in ocean', '1.1', 'enum', 'sunlight_penetration_scheme_types', 'sunlight_penetration_scheme_types', 'Type of sunlight penetration scheme in ocean', 1, '', '', '', '3 extinction depth', '3 extinction depth', '', '', 10000, '2017-03-14 21:28:52', 'clone_10072', NULL, NULL),
(10186, 33, 'cmip6.ocean.boundary_forcing.tracers.sunlight_penetration', 'Sunlight Penetration', 'Properties of sunlight penetration scheme in ocean', 'cmip6.ocean.boundary_forcing.tracers.sunlight_penetration.ocean_colour', 2, 'Ocean Colour', 'Is the ocean sunlight penetration scheme ocean colour dependent ?', '1.1', 'bool', '', '', '', 0, '', 'false', '', '', 'false', '', '', 10000, '2017-03-14 21:28:52', 'clone_10073', NULL, NULL),
(10187, 33, 'cmip6.ocean.boundary_forcing.tracers.sunlight_penetration', 'Sunlight Penetration', 'Properties of sunlight penetration scheme in ocean', 'cmip6.ocean.boundary_forcing.tracers.sunlight_penetration.extinction_depth', 3, 'Extinction Depth', 'Describe and list extinctions depths for sunlight penetration scheme (if applicable).', '0.1', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-14 21:28:52', 'clone_10074', NULL, NULL),
(10188, 33, 'cmip6.ocean.boundary_forcing.tracers.fresh_water_forcing', 'Fresh Water Forcing', 'Properties of surface fresh water forcing in ocean', 'cmip6.ocean.boundary_forcing.tracers.fresh_water_forcing.from_atmopshere', 1, 'From Atmopshere', 'Type of surface fresh water forcing from atmos in ocean', '1.1', 'enum', 'surface_fresh_water_forcing_atmos_types', 'surface_fresh_water_forcing_atmos_types', 'Types of surface fresh water forcing from atmosphere in ocean', 1, '', '', '', 'Freshwater flux', 'Freshwater flux', '', '', 10000, '2017-03-14 21:28:52', 'clone_10075', NULL, NULL),
(10189, 33, 'cmip6.ocean.boundary_forcing.tracers.fresh_water_forcing', 'Fresh Water Forcing', 'Properties of surface fresh water forcing in ocean', 'cmip6.ocean.boundary_forcing.tracers.fresh_water_forcing.from_sea_ice', 2, 'From Sea Ice', 'Type of surface fresh water forcing from sea-ice in ocean', '1.1', 'enum', 'surface_fresh_water_forcing_seaice_types', 'surface_fresh_water_forcing_seaice_types', 'Types of surface fresh water forcing from sea-ice in ocean', 1, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-14 21:28:52', 'clone_10076', NULL, NULL),
(10190, 33, 'cmip6.ocean.boundary_forcing.tracers.fresh_water_forcing', 'Fresh Water Forcing', 'Properties of surface fresh water forcing in ocean', 'cmip6.ocean.boundary_forcing.tracers.fresh_water_forcing.forced_mode_restoring', 3, 'Forced Mode Restoring', 'Type of surface salinity restoring in forced mode (OMIP)', '1.1', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-14 21:28:52', 'clone_10077', NULL, NULL),
(10191, 34, 'cmip6.ocean.key_properties.general', 'General', 'General key properties in ocean', 'cmip6.ocean.key_properties.general.model_family', 1, 'Model Family', 'Type of ocean model.', '1.1', 'enum', 'model_family_types', 'model_family_types', 'Types of ocean models', 1, '', '', '', 'OGCM', 'OGCM', '', '', 10000, '2017-03-14 21:28:52', 'clone_10078', NULL, NULL),
(10192, 34, 'cmip6.ocean.key_properties.general', 'General', 'General key properties in ocean', 'cmip6.ocean.key_properties.general.basic_approximations', 2, 'Basic Approximations', 'Basic approximations made in the ocean.', '1.N', 'enum', 'ocean_basic_approx_types', 'ocean_basic_approx_types', 'Types of basic approximation in ocean', 1, '', '', '', 'Boussinesq,Primitive equations', 'Boussinesq,Primitive equations', '', '', 10000, '2017-03-14 21:28:52', 'clone_10079', NULL, NULL),
(10193, 34, 'cmip6.ocean.key_properties.general', 'General', 'General key properties in ocean', 'cmip6.ocean.key_properties.general.prognostic_variables', 3, 'Prognostic Variables', 'List of prognostic variables in the ocean component.', '1.N', 'enum', 'prognostic_vars_types', 'prognostic_vars_types', 'List of prognostic variables in ocean', 1, '', '', '', 'Potential temperature,Salinity,U-velocity,V-velocity', 'Potential temperature,Salinity,U-velocity,V-velocity', '', '', 10000, '2017-03-14 21:28:52', 'clone_10080', NULL, NULL),
(10194, 34, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.eos_type', 1, 'Eos Type', 'Type of EOS for sea water', '1.1', 'enum', 'seawater_eos_types', 'seawater_eos_types', 'Types of seawater Equation of State in ocean', 1, '', '', '', 'Polynomial EOS-80', 'Polynomial EOS-80', '', '', 10000, '2017-03-14 21:28:52', 'clone_10081', NULL, NULL),
(10195, 34, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.eos_functional_temp', 2, 'Eos Functional Temp', 'Temperature used in EOS for sea water', '1.1', 'enum', 'seawater_eos_func_temp', 'seawater_eos_func_temp', 'Types of temperature used in EOS in ocean', 1, '', '', '', 'Potential temperature', 'Potential temperature', '', '', 10000, '2017-03-14 21:28:52', 'clone_10082', NULL, NULL),
(10196, 34, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.eos_functional_salt', 3, 'Eos Functional Salt', 'Salinity used in EOS for sea water', '1.1', 'enum', 'seawater_eos_func_salt', 'seawater_eos_func_salt', 'Types of salinity used in EOS in ocean', 1, '', '', '', 'Practical salinity Sp', 'Practical salinity Sp', '', '', 10000, '2017-03-14 21:28:52', 'clone_10083', NULL, NULL),
(10197, 34, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.eos_functional_depth', 4, 'Eos Functional Depth', 'Depth or pressure used in EOS for sea water ?', '1.1', 'enum', 'seawater_eos_func_depth', 'seawater_eos_func_depth', 'Types of depth used in EOS in ocean', 1, '', '', '', 'Depth (meters)', 'Depth (meters)', '', '', 10000, '2017-03-14 21:28:52', 'clone_10084', NULL, NULL),
(10198, 34, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.ocean_freezing_point', 5, 'Ocean Freezing Point', 'Equation used to compute the freezing point (in deg C) of seawater, as a function of salinity and pressure', '1.1', 'enum', 'seawater_freezing_point', 'seawater_freezing_point', 'Types of seawater freezing point equation in ocean', 1, '', '', '', 'UNESCO 1983', 'UNESCO 1983', '', '', 10000, '2017-03-14 21:28:52', 'clone_10085', NULL, NULL),
(10199, 34, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.ocean_specific_heat', 6, 'Ocean Specific Heat', 'Specific heat in ocean (cpocean) in J/(kg K)', '1.1', 'float', '', '', '', 0, '3991.86795711963', '', '', '', '3991.8679571196', '', '', 10000, '2017-03-14 21:28:52', 'clone_10086', NULL, NULL),
(10200, 34, 'cmip6.ocean.key_properties.seawater_properties', 'Seawater Properties', 'Physical properties of seawater in ocean', 'cmip6.ocean.key_properties.seawater_properties.ocean_reference_density', 7, 'Ocean Reference Density', 'Boussinesq reference density (rhozero) in kg / m3', '1.1', 'float', '', '', '', 0, '1026.0', '', '', '', '1026', '', '', 10000, '2017-03-14 21:28:52', 'clone_10087', NULL, NULL),
(10201, 34, 'cmip6.ocean.key_properties.bathymetry', 'Bathymetry', 'Properties of bathymetry in ocean', 'cmip6.ocean.key_properties.bathymetry.reference_dates', 1, 'Reference Dates', 'Reference date of bathymetry', '1.1', 'enum', 'bathymetry_ref_dates', 'bathymetry_ref_dates', 'List of reference dates for bathymetry in ocean', 1, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-14 21:28:52', 'clone_10088', NULL, NULL),
(10202, 34, 'cmip6.ocean.key_properties.bathymetry', 'Bathymetry', 'Properties of bathymetry in ocean', 'cmip6.ocean.key_properties.bathymetry.type', 2, 'Type', 'Is the bathymetry fixed in time in the ocean ?', '1.1', 'bool', '', '', '', 0, '', 'true', '', '', 'true', '', '', 10000, '2017-03-14 21:28:52', 'clone_10089', NULL, NULL),
(10203, 34, 'cmip6.ocean.key_properties.bathymetry', 'Bathymetry', 'Properties of bathymetry in ocean', 'cmip6.ocean.key_properties.bathymetry.ocean_smoothing', 3, 'Ocean Smoothing', 'Describe any smoothing or hand editing of bathymetry in ocean', '1.1', 'str', '', '', '', 0, 'Smoothed coastline at Antarctica to avoid single grid point inlets', '', '', '', 'Smoothed coastline at Antarctica to avoid single grid point inlets', '', '', 10000, '2017-03-14 21:28:52', 'clone_10090', NULL, NULL),
(10204, 34, 'cmip6.ocean.key_properties.bathymetry', 'Bathymetry', 'Properties of bathymetry in ocean', 'cmip6.ocean.key_properties.bathymetry.source', 4, 'Source', 'Describe source of bathymetry in ocean', '1.1', 'str', '', '', '', 0, 'ETOPO1, GEBCO, IBSCO', '', '', '', 'ETOPO1, GEBCO, IBSCO', '', '', 10000, '2017-03-14 21:28:52', 'clone_10091', NULL, NULL),
(10205, 34, 'cmip6.ocean.key_properties.nonoceanic_waters', 'Nonoceanic Waters', 'Non oceanic waters treatement in ocean', 'cmip6.ocean.key_properties.nonoceanic_waters.isolated_seas', 1, 'Isolated Seas', 'Describe if/how isolated seas is performed', '0.1', 'str', '', '', '', 0, 'Caspian Sea, Aral Sea, Lake Victoria, American Great Lakes included as ocean points', '', '', '', 'Caspian Sea, Aral Sea, Lake Victoria, American Great Lakes included as ocean points', '', '', 10000, '2017-03-22 11:09:22', 'pamv', NULL, NULL),
(10206, 34, 'cmip6.ocean.key_properties.nonoceanic_waters', 'Nonoceanic Waters', 'Non oceanic waters treatement in ocean', 'cmip6.ocean.key_properties.nonoceanic_waters.river_mouth', 2, 'River Mouth', 'Describe if/how river mouth mixing or estuaries specific treatment is performed', '0.1', 'str', '', '', '', 0, 'none', '', '', '', 'none', '', '', 10000, '2017-03-14 21:28:52', 'clone_10093', NULL, NULL),
(10207, 34, 'cmip6.ocean.key_properties.resolution', 'Resolution', 'Resolution in the ocean grid', 'cmip6.ocean.key_properties.resolution.name', 1, 'Name', 'This is a string usually used by the modelling group to describe the resolution of this grid, e.g. ORCA025, N512L180, T512L70 etc.', '1.1', 'str', '', '', '', 0, 'ORCA25', '', '', '', 'ORCA25', '', '', 10000, '2017-03-22 11:10:09', 'pamv', NULL, NULL),
(10208, 34, 'cmip6.ocean.key_properties.resolution', 'Resolution', 'Resolution in the ocean grid', 'cmip6.ocean.key_properties.resolution.canonical_horizontal_resolution', 2, 'Canonical Horizontal Resolution', 'Expression quoted for gross comparisons of resolution, eg. 50km or 0.1 degrees etc.', '0.1', 'str', '', '', '', 0, '0.25 degree', '', '', '', '0.25 degree', '', '', 10000, '2017-03-22 11:10:25', 'pamv', NULL, NULL),
(10209, 34, 'cmip6.ocean.key_properties.resolution', 'Resolution', 'Resolution in the ocean grid', 'cmip6.ocean.key_properties.resolution.number_of_horizontal_gridpoints', 3, 'Number Of Horizontal Gridpoints', 'Total number of horizontal (XY) points (or degrees of freedom) on computational grid.', '0.1', 'int', '', '', '', 0, '1468800', '', '', '', '1468800', '', '', 10000, '2017-03-22 11:11:02', 'pamv', NULL, NULL),
(10210, 34, 'cmip6.ocean.key_properties.resolution', 'Resolution', 'Resolution in the ocean grid', 'cmip6.ocean.key_properties.resolution.number_of_vertical_levels', 4, 'Number Of Vertical Levels', 'Number of vertical levels resolved on computational grid.', '0.1', 'int', '', '', '', 0, '75', '', '', '', '75', '', '', 10000, '2017-03-14 21:28:52', 'clone_10097', NULL, NULL),
(10211, 34, 'cmip6.ocean.key_properties.resolution', 'Resolution', 'Resolution in the ocean grid', 'cmip6.ocean.key_properties.resolution.is_adaptive_grid', 5, 'Is Adaptive Grid', 'Default is False. Set true if grid resolution changes during execution.', '0.1', 'bool', '', '', '', 0, '', 'false', '', '', 'false', '', '', 10000, '2017-03-14 21:28:52', 'clone_10098', NULL, NULL),
(10212, 34, 'cmip6.ocean.key_properties.resolution', 'Resolution', 'Resolution in the ocean grid', 'cmip6.ocean.key_properties.resolution.thickness_level_1', 6, 'Thickness Level 1', 'Thickness of first surface ocean level (in meters)', '1.1', 'float', '', '', '', 0, '1.0', '', '', '', '1', '', '', 10000, '2017-03-14 21:28:52', 'clone_10099', NULL, NULL),
(10213, 34, 'cmip6.ocean.key_properties.tuning_applied', 'Tuning Applied', 'Tuning methodology for ocean component', 'cmip6.ocean.key_properties.tuning_applied.description', 1, 'Description', 'General overview description of tuning: explain and motivate the main targets and metrics retained. &Document the relative weight given to climate performance metrics versus process oriented metrics, &and on the possible conflicts with parameterization level tuning. In particular describe any struggle &with a parameter value that required pushing it to its limits to solve a particular model deficiency.', '1.1', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-22 11:11:47', 'pamv', NULL, NULL),
(10214, 34, 'cmip6.ocean.key_properties.tuning_applied', 'Tuning Applied', 'Tuning methodology for ocean component', 'cmip6.ocean.key_properties.tuning_applied.global_mean_metrics_used', 2, 'Global Mean Metrics Used', 'List set of metrics of the global mean state used in tuning model/component', '0.N', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-22 11:12:27', 'pamv', NULL, NULL),
(10215, 34, 'cmip6.ocean.key_properties.tuning_applied', 'Tuning Applied', 'Tuning methodology for ocean component', 'cmip6.ocean.key_properties.tuning_applied.regional_metrics_used', 3, 'Regional Metrics Used', 'List of regional metrics of mean state (e.g THC, AABW, regional means etc) used in tuning model/component', '0.N', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-22 11:12:50', 'pamv', NULL, NULL);
INSERT INTO `mt_property` (`id`, `topicid`, `s_group_id`, `s_group_label`, `s_group_description`, `s_id`, `s_display`, `s_label`, `s_desc`, `s_cardinality`, `s_type`, `s_enum_id`, `s_enum_lbl`, `s_enum_desc`, `s_enum_open`, `tmp_str`, `tmp_bool`, `tmp_enum`, `tmp_enum_open`, `value`, `notes`, `nullreason`, `specifiedby`, `upd_date`, `upd_by`, `esdoc_id`, `esdoc_hash`) VALUES
(10216, 34, 'cmip6.ocean.key_properties.tuning_applied', 'Tuning Applied', 'Tuning methodology for ocean component', 'cmip6.ocean.key_properties.tuning_applied.trend_metrics_used', 4, 'Trend Metrics Used', 'List observed trend metrics used in tuning model/component', '0.N', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-22 11:13:07', 'pamv', NULL, NULL),
(10217, 34, 'cmip6.ocean.key_properties.conservation', 'Conservation', 'Conservation in the ocean component', 'cmip6.ocean.key_properties.conservation.description', 1, 'Description', 'Brief description of conservation methodology', '1.1', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-14 21:28:52', 'clone_10104', NULL, NULL),
(10218, 34, 'cmip6.ocean.key_properties.conservation', 'Conservation', 'Conservation in the ocean component', 'cmip6.ocean.key_properties.conservation.scheme', 2, 'Scheme', 'Properties conserved in the ocean by the numerical schemes', '1.N', 'enum', 'conservation_props_types', 'conservation_props_types', 'List of properties that can be conserved in ocean', 1, '', '', '', 'Salt,Heat', 'Salt,Heat', '', '', 10000, '2017-03-14 21:28:52', 'clone_10105', NULL, NULL),
(10219, 34, 'cmip6.ocean.key_properties.conservation', 'Conservation', 'Conservation in the ocean component', 'cmip6.ocean.key_properties.conservation.consistency_properties', 3, 'Consistency Properties', 'Any additional consistency properties (energy conversion, pressure gradient discretisation, ...)?', '0.1', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-14 21:28:52', 'clone_10106', NULL, NULL),
(10220, 34, 'cmip6.ocean.key_properties.conservation', 'Conservation', 'Conservation in the ocean component', 'cmip6.ocean.key_properties.conservation.corrected_conserved_prognostic_variables', 4, 'Corrected Conserved Prognostic Variables', 'Set of variables which are conserved by *more* than the numerical scheme alone.', '0.1', 'str', '', '', '', 0, '', '', '', '', '', '', 'nil:unknown', 10000, '2017-03-14 21:28:52', 'clone_10107', NULL, NULL),
(10221, 34, 'cmip6.ocean.key_properties.conservation', 'Conservation', 'Conservation in the ocean component', 'cmip6.ocean.key_properties.conservation.was_flux_correction_used', 5, 'Was Flux Correction Used', 'Does conservation involved flux correction ?', '0.1', 'bool', '', '', '', 0, '', 'false', '', '', 'false', '', '', 10000, '2017-03-14 21:28:52', 'clone_10108', NULL, NULL),
(10222, 36, 'cmip6.ocean.grid.vertical', 'Vertical', 'Properties of vertical discretisation in ocean', 'cmip6.ocean.grid.vertical.coordinates', 1, 'Coordinates', 'Type of vertical coordinates in ocean', '1.1', 'enum', 'vertical_coordinate_types', 'vertical_coordinate_types', 'Types of vertical coordinates in ocean', 1, '', '', '', 'Z*-coordinate', 'Z*-coordinate', '', '', 10000, '2017-03-14 21:28:52', 'clone_10109', NULL, NULL),
(10223, 36, 'cmip6.ocean.grid.vertical', 'Vertical', 'Properties of vertical discretisation in ocean', 'cmip6.ocean.grid.vertical.partial_steps', 2, 'Partial Steps', 'Using partial steps with Z or Z* vertical coordinate in ocean ?', '1.1', 'bool', '', '', '', 0, '', 'true', '', '', 'true', '', '', 10000, '2017-03-14 21:28:52', 'clone_10110', NULL, NULL),
(10224, 36, 'cmip6.ocean.grid.horizontal', 'Horizontal', 'Type of horizontal discretisation scheme in ocean', 'cmip6.ocean.grid.horizontal.type', 1, 'Type', 'Horizontal grid type', '1.1', 'enum', 'horizontal_grid_types', 'horizontal_grid_types', 'Types of horizonal grid in ocean', 1, '', '', '', 'Two north poles (ORCA-style)', 'Two north poles (ORCA-style)', '', '', 10000, '2017-03-14 21:28:52', 'clone_10111', NULL, NULL),
(10225, 36, 'cmip6.ocean.grid.horizontal', 'Horizontal', 'Type of horizontal discretisation scheme in ocean', 'cmip6.ocean.grid.horizontal.scheme', 2, 'Scheme', 'Horizontal discretisation scheme in ocean', '1.1', 'enum', 'horizontal_scheme_types', 'horizontal_scheme_types', 'Types of horizonal scheme in ocean', 1, '', '', '', 'Finite difference / Arakawa C-grid', 'Finite difference / Arakawa C-grid', '', '', 10000, '2017-03-14 21:28:52', 'clone_10112', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `mt_topic`
--

CREATE TABLE IF NOT EXISTS `mt_topic` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for process',
  `o_id` int(11) NOT NULL COMMENT 'id of object this topic concerns (e.g GRID, DOMAIN, PROCESS)',
  `o_type` enum('COUPLEDMODEL','DOMAIN','PROCESS','GRID','KEY') NOT NULL DEFAULT 'PROCESS' COMMENT 'type of referencing object',
  `topic_type` varchar(20) NOT NULL COMMENT 'type code for this topic - from codelist',
  `s_id` varchar(100) NOT NULL COMMENT 'specialisation id for this topic',
  `s_label` varchar(200) NOT NULL COMMENT 'specialisation label for this topic',
  `s_desc` varchar(400) NOT NULL COMMENT 'specialisation description for this topic',
  `description` text COMMENT 'description of how the model deals with this process',
  `implementation` text,
  `keywords` varchar(200) DEFAULT NULL COMMENT 'keywords describing process',
  `specifiedby` int(11) DEFAULT NULL COMMENT 'person responsible for specification',
  `upd_by` char(20) NOT NULL COMMENT 'update by',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of update',
  `ref_type` char(5) NOT NULL DEFAULT 'TOPIC' COMMENT 'type code used to link to references',
  `esdoc_id` text COMMENT 'id from esdoc specialisation',
  `esdoc_hash` text COMMENT 'used to check if record needs to be updated with new esdoc specialisation',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `mt_topic`
--

INSERT INTO `mt_topic` (`id`, `o_id`, `o_type`, `topic_type`, `s_id`, `s_label`, `s_desc`, `description`, `implementation`, `keywords`, `specifiedby`, `upd_by`, `upd_date`, `ref_type`, `esdoc_id`, `esdoc_hash`) VALUES
(1, 10002, 'DOMAIN', 'PROCESS', 'cmip6.ocean.timestepping_framework', 'Timestepping Framework', 'Ocean Timestepping Framework', 'The integration timestep is 15 minutes. \r\nTimestepping of tracers is achieved by use of a leap-frog scheme and Asselin filter.\r\nThe barotropic solver scheme is a preconditioned conjugate gradient type, using a leapfrog and Asselin filter scheme.\r\nThe barotropic momentum solver also uses a leapfrog / Asselin filter scheme.', '', '', 10000, 'pamv', '2017-02-10 15:47:47', 'TOPIC', NULL, NULL),
(2, 10002, 'DOMAIN', 'PROCESS', 'cmip6.ocean.advection', 'Advection', 'Ocean advection', 'Advection of momentum uses a vector-invariant (rotational and irrotational) formulation. The irrotational component follows Hollingsworth et al. (1983) to avoid vertical numerical instabilities. The vorticity term is calculated using an energy and enstrophy conserving scheme. Advection of tracers uses  Total Variance Dissipation (TVD) scheme.', '', '', 10000, 'pamv', '2017-03-05 15:08:10', 'TOPIC', NULL, NULL),
(3, 2, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.advection.momentum', 'Momentum', 'Properties of lateral momemtum advection scheme in ocean', 'The momentum advection term is a vector-invariant formulation in which the horizontal advection is split into rotational and irrotational parts. The vorticity term (including the coriolis term) is calculated using the energy and enstrophy conserving scheme of Arakawa and Lamb (1981). The irrotational part is formulated according to Hollingsworth et al. (1983) in order to avoid vertical numerical instabilities.', '', '', 10000, 'pamv', '2017-03-05 15:09:05', 'TOPIC', NULL, NULL),
(4, 2, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.advection.lateral_tracers', 'Lateral Tracers', 'Properties of lateral tracer advection scheme in ocean', 'The advection of tracers is done using a Total Variance Dissipation (TVD) scheme (Zalesak, 1979).\r\n', '', '', 10000, 'pamv', '2017-02-08 09:05:15', 'TOPIC', NULL, NULL),
(5, 2, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.advection.vertical_tracers', 'Vertical Tracers', 'Properties of vertical tracer advection scheme in ocean', 'The advection of tracers is done using a Total Variance Dissipation (TVD) scheme (Zalesak, 1979).\r\n', '', '', 10000, 'pamv', '2017-02-08 09:06:36', 'TOPIC', NULL, NULL),
(6, 10002, 'DOMAIN', 'PROCESS', 'cmip6.ocean.lateral_physics', 'Lateral Physics', 'Ocean lateral physics', 'Lateral diffusion of momentum uses a bilaplacian operator and is on geopotential surfaces. Lateral diffusion of tracers uses a laplacian operator and is along isoneutral surfaces. Both terms use a grid scale dependent mixing coefficient. Adiabatic mixing by transient eddies is parameterized in the ORCA1 configuration.', '', '', 10000, 'pamv', '2017-03-05 15:10:00', 'TOPIC', NULL, NULL),
(7, 6, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.lateral_physics.momentum', 'Momentum', 'Properties of lateral physics for momentum in ocean', 'The horizontal viscosity is bilaplacian (bi-harmonic, along-geopotential?) with a value of 1.5 × 1011 m4/s at the equator, reducing polewards with the cube of the grid spacing in order to avoid numerical diffusion instabilities (REF; Roberts and Marshall, 1998?).\r\n', '', '', 10000, 'pamv', '2017-02-08 10:03:04', 'TOPIC', NULL, NULL),
(8, 6, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.lateral_physics.tracers', 'Tracers', 'Properties of lateral physics for tracers in ocean', 'Lateral tracer mixing is along isoneutral surfaces with a coefficient of 150m2/s at the equator, reducing linearly with the grid spacing. \r\nThe Gent and McWilliams (1990) parameterisation of adiabatic eddy mixing is not used at ORCA025, but at ORCA1 is used with ORCA1 GM details.', '', '', 10000, 'pamv', '2017-02-08 10:04:25', 'TOPIC', NULL, NULL),
(9, 10002, 'DOMAIN', 'PROCESS', 'cmip6.ocean.vertical_physics', 'Vertical Physics', 'Ocean Vertical Physics', 'The vertical physics are parameterized using a ‘one-equation’ (‘TKE’) scheme. Further parameterized processes include Langmuir turbulence, double-diffusive mixing, tidally-driven mixing and near-inertial wave breaking. Unresolved mixing is represented as background values of eddy diffusivity and viscosity.', '', '', 10000, 'pamv', '2017-03-05 15:11:13', 'TOPIC', NULL, NULL),
(10, 9, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.vertical_physics.boundary_layer_mixing', 'Boundary Layer Mixing', 'Properties of boundary layer mixing in the ocean (aka mixed layer)', 'The vertical mixing of tracers and momentum is parameterised using a modified version of the Gaspar et al. (1990) Turbulent Kinetic Energy (TKE) scheme (Madec et al., 1998).\r\nUnresolved mixing due to internal wave breaking is represented by a background vertical eddy diffusivity of 1.2 × 10−5 m2/s, which decreases linearly from ±15° latitude to a value of 1.2 × 10−6 m2/s at ±5° latitude (Gregg et al., 2003) and a globally constant background viscosity of 1.2 × 10−4 m2/s. \r\nThere is enhanced mixing at the surface depending on the wind stress to represent mixing due to wave breaking (Craig and Banner, 1994) and an ad hoc representation of mixing due to near-inertial wave breaking (Madec, 2008 section 10.1; Rodgers et al., 2014). The e-decay length scale of the latter parameterization increases sinusoidally from 0.5 m at the equator to 10 m and 30 m at ~13° N and ~40° S respectively (Storkey et al., in preparation).\r\nThe Axell (2002) parameterization of Langmuir turbulence is used.', '', '', 10000, 'pamv', '2017-02-08 14:37:20', 'TOPIC', NULL, NULL),
(11, 9, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.vertical_physics.interior_mixing', 'Interior Mixing', 'Properties of interior vertical mixing in the ocean', 'The vertical mixing of tracers and momentum is parameterised using a modified version of the Gaspar et al. (1990) Turbulent Kinetic Energy (TKE) scheme (Madec et al., 1998). Unresolved mixing due to internal wave breaking is represented by a background vertical eddy diffusivity of 1.2 × 10−5 m2/s, which decreases linearly from ±15° latitude to a value of 1.2 × 10−6 m2/s at ±5° latitude (Gregg et al., 2003) and a globally constant background viscosity of 1.2 × 10−4 m2/s.  The tidal mixing parameterisation of Simmons et al. (2004) is used with a special formulation for the Indonesian Throughflow (Koch-Larrouy et al., 2008).  The Merryfield et al. (1999) parameterisation of double diffusive mixing is used. Convective mixing is achieved via an enhanced vertical eddy diffusivity coefficient of 10 m2/s where the density profile is statically unstable.', '', '', 10000, 'pamv', '2017-03-05 15:13:07', 'TOPIC', NULL, NULL),
(12, 10002, 'DOMAIN', 'PROCESS', 'cmip6.ocean.uplow_boundaries', 'Uplow Boundaries', 'Ocean upper / lower boundaries', 'The model uses a non-linear free surface in which the cell thicknesses throughout the water column are allowed to vary with time (the z∗ coordinate of Adcroft and Campin, 2004). This permits an exact representation of the surface freshwater flux. \r\nThe equation for the surface pressure gradient is solved using a filtered solution in which the fast gravity waves are damped by an additional force in the equation (Roullet and Madec, 2000).\r\nAn advective and diffusive bottom boundary layer scheme is used (Beckmann and Doscher, 1997), with a lateral mixing coefficient of 1000 m2/s.\r\nSea ice levitating?', '', '', 10000, 'pamv', '2017-02-09 08:18:28', 'TOPIC', NULL, NULL),
(13, 10002, 'DOMAIN', 'PROCESS', 'cmip6.ocean.boundary_forcing', 'Boundary Forcing', 'Ocean boundary forcing', 'Meltwater fluxes from icebergs and ice shelves are specifically parameterized. Penetration of the shortwave heat flux into the ocean is parameterized using a 3-band ‘RGB’ scheme. Dense overflows are parameterized using an advective and diffusive bottom boundary layer scheme. A quadratic bottom friction is used with regional coefficient enhancements.', '', '', 10000, 'pamv', '2017-03-05 15:10:46', 'TOPIC', NULL, NULL),
(14, 13, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.boundary_forcing.momentum', 'Momentum', 'Key properties of momentum boundary forcing in the ocean', 'Bottom friction is quadratic with an increased coefficient in the Indonesian Throughflow, Denmark Strait and Bab al Mandab regions. ', '', '', 10000, 'pamv', '2017-03-05 15:14:03', 'TOPIC', NULL, NULL),
(15, 13, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.boundary_forcing.tracers', 'Tracers', 'Key properties of tracer boundary forcing in the ocean', 'Freshwater runoff from land is input in the surface layer of the ocean with the assumption that the runoff is fresh and at the same temperature as the local sea surface temperature. An enhanced vertical mixing of 2 × 10−3 m2/s is added over the top 10 m of the water column at runoff points to mix the runoff vertically and avoid instabilities associated with very shallow fresh layers at the surface. \r\nFreshwater input from frozen land masses (Greenland and Antarctica) is modelled using a lagrangian iceberg scheme and a parameterization of ice shelf basal melting. The lagrangian iceberg model is that of Bigg et al. (1997) and Martin and Adcroft (2010) as implemented in NEMO by Marsh et al. (2015). Icebergs are represented by lagrangian particles, each particle representing a collection of icebergs within a given size range. The momentum balance for icebergs comprises the Coriolis force, air and water form drags, the horizontal pressure gradient force, a wave radiation force and interaction with sea ice The mass balance for an individual iceberg is governed by basal melting, buoyant convection at the sidewalls, and wave erosion. A weaknesses of the present model configuration is that the icebergs only exchange momentum, heat and freshwater with the surface layer of the ocean (of 1m thickness) whereas in reality many icebergs have draughts of hundreds of metres. Also there is no momentum exchange with sea ice. As icebergs melt the latent heat of melting is extracted from the ocean, but the heat content of the meltwater input to the ocean is neglected.\r\nIce shelf basal meltwater is input through depth at the edge of the ice shelves using the parameterization described by Mathiot et al. (2017). The 3-band ‘RGB’ scheme of Lengaigne et al. (2007) is used to model shortwave flux penetration into the ocean, assuming a constant chlorophyll concentration of 0.05 g.Chl/L. An advective and diffusive bottom boundary layer scheme is used to represent dense overflows (Beckmann and Doscher, 1997).', '', '', 10000, 'pamv', '2017-03-05 15:18:03', 'TOPIC', NULL, NULL),
(16, 10002, 'DOMAIN', 'KEY', 'cmip6.ocean.key_properties', 'Key Properties', 'Ocean key properties', 'Includes information on the model family, prognostic variables, seawater properties, bathymetry, ocean smoothing, resolution, global and regional metrics and conservation.', '', '', 74, 'pamv', '2017-02-16 09:40:24', 'TOPIC', NULL, NULL),
(17, 10002, 'DOMAIN', 'GRID', 'cmip6.ocean.grid', 'Grid', 'Ocean grid', 'The horizontal grid is an extended version of the ORCA025 tripolar Arakawa C-grid (Barnier et al., 2006). This has nominal 1/4° resolution (1442 x 1207 grid points) at global scale decreasing poleward (an isotropic Mercator grid in the southern hemisphere, matched to a quasi-isotropic bipolar grid in the northern hemisphere with poles at 107°W and 73°E). The reference ORCA025 grid has been extended southwards from 77°S to 85°S using the procedure of Mathiot et al. (submitted 2017) to permit the modelling of the circulation under ice shelves in Antarctica. The effective resolution is approximately 27.75 km at the equator but increases with latitude (for example, to 13.8 km at 60°S or 60°N). ', '', '', 10000, 'pamv', '2017-02-09 08:42:08', 'TOPIC', NULL, NULL),
(18, 17, 'GRID', 'SUBPROCESS', 'cmip6.ocean.grid.discretisation', 'Discretisation', 'Type of discretisation scheme in ocean', NULL, NULL, NULL, NULL, 'realm_importer', '2017-02-02 15:57:02', 'TOPIC', NULL, NULL),
(19, 10003, 'DOMAIN', 'PROCESS', 'cmip6.ocean.timestepping_framework', 'Timestepping Framework', 'Ocean Timestepping Framework', 'The integration timestep is 15 minutes. \r\nTimestepping of tracers is achieved by use of a leap-frog scheme and Asselin filter.\r\nThe barotropic solver scheme is a preconditioned conjugate gradient type, using a leapfrog and Asselin filter scheme.\r\nThe barotropic momentum solver also uses a leapfrog / Asselin filter scheme.', '', '', 10000, 'clone_1', '2017-03-14 21:28:51', 'TOPIC', NULL, NULL),
(20, 10003, 'DOMAIN', 'PROCESS', 'cmip6.ocean.advection', 'Advection', 'Ocean advection', 'Advection of momentum uses a vector-invariant (rotational and irrotational) formulation. The irrotational component follows Hollingsworth et al. (1983) to avoid vertical numerical instabilities. The vorticity term is calculated using an energy and enstrophy conserving scheme. Advection of tracers uses  Total Variance Dissipation (TVD) scheme.', '', '', 10000, 'clone_2', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(21, 20, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.advection.momentum', 'Momentum', 'Properties of lateral momemtum advection scheme in ocean', 'The momentum advection term is a vector-invariant formulation in which the horizontal advection is split into rotational and irrotational parts. The vorticity term (including the coriolis term) is calculated using the energy and enstrophy conserving scheme of Arakawa and Lamb (1981). The irrotational part is formulated according to Hollingsworth et al. (1983) in order to avoid vertical numerical instabilities.', '', '', 10000, 'clone_3', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(22, 20, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.advection.lateral_tracers', 'Lateral Tracers', 'Properties of lateral tracer advection scheme in ocean', 'The advection of tracers is done using a Total Variance Dissipation (TVD) scheme (Zalesak, 1979).\r\n', '', '', 10000, 'clone_4', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(23, 20, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.advection.vertical_tracers', 'Vertical Tracers', 'Properties of vertical tracer advection scheme in ocean', 'The advection of tracers is done using a Total Variance Dissipation (TVD) scheme (Zalesak, 1979).\r\n', '', '', 10000, 'clone_5', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(24, 10003, 'DOMAIN', 'PROCESS', 'cmip6.ocean.lateral_physics', 'Lateral Physics', 'Ocean lateral physics', 'Lateral diffusion of momentum uses a bilaplacian operator and is on geopotential surfaces. Lateral diffusion of tracers uses a laplacian operator and is along isoneutral surfaces. Both terms use a grid scale dependent mixing coefficient. Adiabatic mixing by transient eddies is parameterized in the ORCA1 configuration.', '', '', 10000, 'clone_6', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(25, 24, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.lateral_physics.momentum', 'Momentum', 'Properties of lateral physics for momentum in ocean', 'The horizontal viscosity is bilaplacian (bi-harmonic, along-geopotential?) with a value of 1.5 × 1011 m4/s at the equator, reducing polewards with the cube of the grid spacing in order to avoid numerical diffusion instabilities (REF; Roberts and Marshall, 1998?).\r\n', '', '', 10000, 'clone_7', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(26, 24, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.lateral_physics.tracers', 'Tracers', 'Properties of lateral physics for tracers in ocean', 'Lateral tracer mixing is along isoneutral surfaces with a coefficient of 150m2/s at the equator, reducing linearly with the grid spacing. \r\nThe Gent and McWilliams (1990) parameterisation of adiabatic eddy mixing is not used at ORCA025, but at ORCA1 is used with ORCA1 GM details.', '', '', 10000, 'clone_8', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(27, 10003, 'DOMAIN', 'PROCESS', 'cmip6.ocean.vertical_physics', 'Vertical Physics', 'Ocean Vertical Physics', 'The vertical physics are parameterized using a ‘one-equation’ (‘TKE’) scheme. Further parameterized processes include Langmuir turbulence, double-diffusive mixing, tidally-driven mixing and near-inertial wave breaking. Unresolved mixing is represented as background values of eddy diffusivity and viscosity.', '', '', 10000, 'clone_9', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(28, 27, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.vertical_physics.boundary_layer_mixing', 'Boundary Layer Mixing', 'Properties of boundary layer mixing in the ocean (aka mixed layer)', 'The vertical mixing of tracers and momentum is parameterised using a modified version of the Gaspar et al. (1990) Turbulent Kinetic Energy (TKE) scheme (Madec et al., 1998).\r\nUnresolved mixing due to internal wave breaking is represented by a background vertical eddy diffusivity of 1.2 × 10−5 m2/s, which decreases linearly from ±15° latitude to a value of 1.2 × 10−6 m2/s at ±5° latitude (Gregg et al., 2003) and a globally constant background viscosity of 1.2 × 10−4 m2/s. \r\nThere is enhanced mixing at the surface depending on the wind stress to represent mixing due to wave breaking (Craig and Banner, 1994) and an ad hoc representation of mixing due to near-inertial wave breaking (Madec, 2008 section 10.1; Rodgers et al., 2014). The e-decay length scale of the latter parameterization increases sinusoidally from 0.5 m at the equator to 10 m and 30 m at ~13° N and ~40° S respectively (Storkey et al., in preparation).\r\nThe Axell (2002) parameterization of Langmuir turbulence is used.', '', '', 10000, 'clone_10', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(29, 27, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.vertical_physics.interior_mixing', 'Interior Mixing', 'Properties of interior vertical mixing in the ocean', 'The vertical mixing of tracers and momentum is parameterised using a modified version of the Gaspar et al. (1990) Turbulent Kinetic Energy (TKE) scheme (Madec et al., 1998). Unresolved mixing due to internal wave breaking is represented by a background vertical eddy diffusivity of 1.2 × 10−5 m2/s, which decreases linearly from ±15° latitude to a value of 1.2 × 10−6 m2/s at ±5° latitude (Gregg et al., 2003) and a globally constant background viscosity of 1.2 × 10−4 m2/s.  The tidal mixing parameterisation of Simmons et al. (2004) is used with a special formulation for the Indonesian Throughflow (Koch-Larrouy et al., 2008).  The Merryfield et al. (1999) parameterisation of double diffusive mixing is used. Convective mixing is achieved via an enhanced vertical eddy diffusivity coefficient of 10 m2/s where the density profile is statically unstable.', '', '', 10000, 'clone_11', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(30, 10003, 'DOMAIN', 'PROCESS', 'cmip6.ocean.uplow_boundaries', 'Uplow Boundaries', 'Ocean upper / lower boundaries', 'The model uses a non-linear free surface in which the cell thicknesses throughout the water column are allowed to vary with time (the z∗ coordinate of Adcroft and Campin, 2004). This permits an exact representation of the surface freshwater flux. \r\nThe equation for the surface pressure gradient is solved using a filtered solution in which the fast gravity waves are damped by an additional force in the equation (Roullet and Madec, 2000).\r\nAn advective and diffusive bottom boundary layer scheme is used (Beckmann and Doscher, 1997), with a lateral mixing coefficient of 1000 m2/s.\r\nSea ice levitating?', '', '', 10000, 'clone_12', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(31, 10003, 'DOMAIN', 'PROCESS', 'cmip6.ocean.boundary_forcing', 'Boundary Forcing', 'Ocean boundary forcing', 'Meltwater fluxes from icebergs and ice shelves are specifically parameterized. Penetration of the shortwave heat flux into the ocean is parameterized using a 3-band ‘RGB’ scheme. Dense overflows are parameterized using an advective and diffusive bottom boundary layer scheme. A quadratic bottom friction is used with regional coefficient enhancements.', '', '', 10000, 'clone_13', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(32, 31, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.boundary_forcing.momentum', 'Momentum', 'Key properties of momentum boundary forcing in the ocean', 'Bottom friction is quadratic with an increased coefficient in the Indonesian Throughflow, Denmark Strait and Bab al Mandab regions. ', '', '', 10000, 'clone_14', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(33, 31, 'PROCESS', 'SUBPROCESS', 'cmip6.ocean.boundary_forcing.tracers', 'Tracers', 'Key properties of tracer boundary forcing in the ocean', 'Freshwater runoff from land is input in the surface layer of the ocean with the assumption that the runoff is fresh and at the same temperature as the local sea surface temperature. An enhanced vertical mixing of 2 × 10−3 m2/s is added over the top 10 m of the water column at runoff points to mix the runoff vertically and avoid instabilities associated with very shallow fresh layers at the surface. \r\nFreshwater input from frozen land masses (Greenland and Antarctica) is modelled using a lagrangian iceberg scheme and a parameterization of ice shelf basal melting. The lagrangian iceberg model is that of Bigg et al. (1997) and Martin and Adcroft (2010) as implemented in NEMO by Marsh et al. (2015). Icebergs are represented by lagrangian particles, each particle representing a collection of icebergs within a given size range. The momentum balance for icebergs comprises the Coriolis force, air and water form drags, the horizontal pressure gradient force, a wave radiation force and interaction with sea ice The mass balance for an individual iceberg is governed by basal melting, buoyant convection at the sidewalls, and wave erosion. A weaknesses of the present model configuration is that the icebergs only exchange momentum, heat and freshwater with the surface layer of the ocean (of 1m thickness) whereas in reality many icebergs have draughts of hundreds of metres. Also there is no momentum exchange with sea ice. As icebergs melt the latent heat of melting is extracted from the ocean, but the heat content of the meltwater input to the ocean is neglected.\r\nIce shelf basal meltwater is input through depth at the edge of the ice shelves using the parameterization described by Mathiot et al. (2017). The 3-band ‘RGB’ scheme of Lengaigne et al. (2007) is used to model shortwave flux penetration into the ocean, assuming a constant chlorophyll concentration of 0.05 g.Chl/L. An advective and diffusive bottom boundary layer scheme is used to represent dense overflows (Beckmann and Doscher, 1997).', '', '', 10000, 'clone_15', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(34, 10003, 'DOMAIN', 'KEY', 'cmip6.ocean.key_properties', 'Key Properties', 'Ocean key properties', 'Includes information on the model family, prognostic variables, seawater properties, bathymetry, ocean smoothing, resolution, global and regional metrics and conservation.', '', '', 74, 'clone_16', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(35, 10003, 'DOMAIN', 'GRID', 'cmip6.ocean.grid', 'Grid', 'Ocean grid', 'The horizontal grid is an extended version of the ORCA025 tripolar Arakawa C-grid (Barnier et al., 2006). This has nominal 1/4° resolution (1442 x 1207 grid points) at global scale decreasing poleward (an isotropic Mercator grid in the southern hemisphere, matched to a quasi-isotropic bipolar grid in the northern hemisphere with poles at 107°W and 73°E). The reference ORCA025 grid has been extended southwards from 77°S to 85°S using the procedure of Mathiot et al. (submitted 2017) to permit the modelling of the circulation under ice shelves in Antarctica. The effective resolution is approximately 27.75 km at the equator but increases with latitude (for example, to 13.8 km at 60°S or 60°N). ', '', '', 10000, 'clone_17', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL),
(36, 35, 'GRID', 'SUBPROCESS', 'cmip6.ocean.grid.discretisation', 'Discretisation', 'Type of discretisation scheme in ocean', '', '', '', 0, 'clone_18', '2017-03-14 21:28:52', 'TOPIC', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `pt_ancillary`
--

CREATE TABLE IF NOT EXISTS `pt_ancillary` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'table primary index',
  `projectid` int(11) NOT NULL,
  `sname` varchar(20) NOT NULL COMMENT 'code used to reference use of ancillary as forcing',
  `category` varchar(30) DEFAULT NULL COMMENT 'ancillary category (code)',
  `group` varchar(30) DEFAULT NULL COMMENT 'group within category (code)',
  `info` text COMMENT 'description of anciallary content',
  `integration_type` varchar(40) DEFAULT NULL COMMENT 'how is it used (e.g. scenario, idealised)',
  `integration` varchar(500) DEFAULT NULL COMMENT 'integration description',
  `source` varchar(200) NOT NULL COMMENT 'source for data',
  `referenceid` int(11) NOT NULL COMMENT 'source citation',
  `weblink` varchar(200) NOT NULL COMMENT 'url for source data',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date/time for last update',
  `upd_by` varchar(20) NOT NULL COMMENT 'user responsible for last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `pt_errata`
--

CREATE TABLE IF NOT EXISTS `pt_errata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `programmeid` int(11) DEFAULT NULL COMMENT 'id for programme associated with this errata issue',
  `experimentid` varchar(500) DEFAULT NULL COMMENT 'comma separated list of experiment (short) namesconcerned with errata issue',
  `modelid` varchar(500) DEFAULT NULL COMMENT 'comma seperated list of model (short) namesconcerned with errata issue',
  `simulationid` varchar(500) DEFAULT NULL COMMENT 'comma seperated list of simulation realisation codes (e.g. r1i1p1f1) concerned with errata issue',
  `variable` varchar(500) DEFAULT NULL COMMENT 'comma separated list of variable name/table pairs associated with errata issue',
  `title` varchar(200) NOT NULL COMMENT 'title for errata issue',
  `info` text NOT NULL COMMENT 'description of errata issue',
  `json_spec` text COMMENT 'json specification of datasets affected in terms of DRS facets',
  `record_type` varchar(40) NOT NULL COMMENT 'type of errata record type (e.g. ''info'') - from codelist',
  `severity` enum('low','medium','high','critical') NOT NULL COMMENT 'severity code for errata issue',
  `landing_page` varchar(200) DEFAULT NULL COMMENT 'publicly accessible URL for further information on the issue',
  `date_created` date DEFAULT NULL COMMENT 'date errata issue created',
  `date_closed` date DEFAULT NULL COMMENT 'date errata issue closed',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `upd_by` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='table to record eratta information related to an experiment';

-- --------------------------------------------------------

--
-- Table structure for table `pt_errata_data`
--

CREATE TABLE IF NOT EXISTS `pt_errata_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key for table',
  `errataid` int(11) NOT NULL COMMENT 'id for errata issue this data item is associated with',
  `drs` varchar(300) DEFAULT NULL COMMENT 'drs representation of data item',
  `upd_by` varchar(20) NOT NULL COMMENT 'user responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Data items associated with errata issue';

-- --------------------------------------------------------

--
-- Table structure for table `pt_experiment`
--

CREATE TABLE IF NOT EXISTS `pt_experiment` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'unique id',
  `projectid` int(11) NOT NULL,
  `sname` varchar(40) NOT NULL COMMENT 'project specific experiment code (e.g rcp45)',
  `subname` varchar(20) DEFAULT NULL COMMENT 'subname (e.g s1960 to indicate startdate at 1960)',
  `name` varchar(200) NOT NULL COMMENT 'full name - from description of code',
  `info` text COMMENT 'text description',
  `weblink` varchar(150) DEFAULT NULL COMMENT 'link to further information on experiment (e.g internal wiki page)',
  `areatype` char(20) NOT NULL DEFAULT 'global' COMMENT 'global or regional (coded)',
  `areacode` varchar(20) DEFAULT NULL COMMENT 'code to link to project specific domains contained in pt_domain',
  `ensemblesize` int(6) NOT NULL DEFAULT '1' COMMENT 'total no. of elements in ensemble',
  `ensembletype` varchar(20) NOT NULL COMMENT 'coded rip value indicating how ensemble is constructed (e.g. r*i*p - indicates the initialisation and initialisation method can change - rip means none)',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` varchar(20) NOT NULL COMMENT 'person/process responsible for last update',
  `o_type` enum('EXPERIMENT') NOT NULL DEFAULT 'EXPERIMENT' COMMENT 'object type (always EXPERIMENT)',
  `esdoc_id` text COMMENT 'id from esdoc specialisation',
  `esdoc_hash` text COMMENT 'hash from esdoc specialisation',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='experiment information';

--
-- Dumping data for table `pt_experiment`
--

INSERT INTO `pt_experiment` (`id`, `projectid`, `sname`, `subname`, `name`, `info`, `weblink`, `areatype`, `areacode`, `ensemblesize`, `ensembletype`, `upd_date`, `upd_by`, `o_type`, `esdoc_id`, `esdoc_hash`) VALUES
(10110, 10012, 'ssp245', '', 'SSP2-4.5', 'SSP-based RCP scenario with medium radiative forcing by the end of the century. Following approximately RCP4.5 global forcing pathway with SSP2 socioeconomic conditions. Radiative forcing reaches a level of 4.5 W/m2 in 2100. Concentration-driven. \r\nThe scenario represents the medium part of the range of plausible future pathways. ', 'http://view.es-doc.org/?renderMethod=id&project=CMIP6-DRAFT&id=c588ab1f-19aa-4671-97b6-38621954e9d1&version=1&client=esdoc-search', 'global', NULL, 1, 'n/a', '2017-03-15 14:52:43', 'admin', 'EXPERIMENT', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `pt_forcing`
--

CREATE TABLE IF NOT EXISTS `pt_forcing` (
  `id` int(11) NOT NULL COMMENT 'primary key for this table',
  `simulationid` int(11) NOT NULL COMMENT 'simulation to which forcing applies',
  `ancillaryid` int(11) NOT NULL COMMENT 'id for project ancillary',
  `integration` varchar(1000) DEFAULT NULL COMMENT 'integration details for simulation',
  `modification` varchar(1000) DEFAULT NULL COMMENT 'details on any modifications made to the standard dataset',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` varchar(20) NOT NULL COMMENT 'user responsible for last update'
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `pt_links`
--

CREATE TABLE IF NOT EXISTS `pt_links` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for link',
  `o_type` varchar(20) NOT NULL COMMENT 'object type that link refers to',
  `o_id` int(11) NOT NULL COMMENT 'id of relevant object type',
  `name` varchar(60) NOT NULL COMMENT 'name for link',
  `weblink` varchar(200) NOT NULL COMMENT 'url to resource',
  `tooltip` varchar(512) DEFAULT NULL COMMENT 'text for popup description of the link',
  `category` varchar(40) DEFAULT NULL COMMENT 'grouping keyword - may be object type and/or object specific',
  `rank` tinyint(4) NOT NULL COMMENT 'order to display within category',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` char(20) CHARACTER SET latin1 COLLATE latin1_general_ci NOT NULL COMMENT 'person/process responsible for last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='links information';

--
-- Dumping data for table `pt_links`
--

INSERT INTO `pt_links` (`id`, `o_type`, `o_id`, `name`, `weblink`, `tooltip`, `category`, `rank`, `upd_date`, `upd_by`) VALUES
(10001, '', 10001, 'WCRP CMIP Phase 6', 'http://www.wcrp-climate.org/wgcm-cmip/wgcm-cmip6', NULL, 'project', 1, '2016-03-01 11:00:02', 'pamv'),
(10003, 'PROJECT', 10003, 'Scenario MIP home', 'http://cmip.ucar.edu/scenario-mip', NULL, 'project', 1, '2016-03-01 15:16:49', 'pamv'),
(10004, 'PROJECT', 10006, 'WCRP-DAMIP', 'http://www.wcrp-climate.org/modelling-wgcm-mip-catalogue/modelling-wgcm-mips/475-modelling-wgcm-damip', NULL, 'project', 1, '2016-03-02 09:26:39', 'pamv'),
(10005, 'PROJECT', 10009, 'WCRP-RFMIP', 'http://www.wcrp-climate.org/modelling-wgcm-mip-catalogue/modelling-wgcm-mips/418-wgcm-rfmip', NULL, 'project', 1, '2016-03-02 09:26:24', 'pamv'),
(10006, 'PROJECT', 10003, 'WCRP-ScenarioMIP', 'http://www.wcrp-climate.org/modelling-wgcm-mip-catalogue/modelling-wgcm-mips/319-modelling-wgcm-scenario-mip', NULL, 'project', 1, '2016-03-02 09:25:49', 'pamv'),
(10007, 'PROJECT', 10010, 'WCRP-LUMIP', 'http://www.wcrp-climate.org/modelling-wgcm-mip-catalogue/modelling-wgcm-mips/318-modelling-wgcm-catalogue-lumip', NULL, 'general', 1, '2016-03-02 09:52:01', 'pamv'),
(10008, 'PROJECT', 10011, 'WCRP-GeoMIP', 'http://www.wcrp-climate.org/modelling-wgcm-mip-catalogue/modelling-wgcm-mips/231-modelling-wgcm-geomip', NULL, 'project', 1, '2016-03-02 11:10:54', 'pamv');

-- --------------------------------------------------------

--
-- Table structure for table `pt_modelrun`
--

CREATE TABLE IF NOT EXISTS `pt_modelrun` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for model run',
  `suiteid` varchar(40) CHARACTER SET utf8 NOT NULL COMMENT '	ROSE suite name or UMUI run name',
  `revision` varchar(20) CHARACTER SET utf8 NOT NULL COMMENT 'revision for branch',
  `runname` varchar(60) CHARACTER SET utf8 NOT NULL COMMENT 'branch name',
  `simulationid` int(11) NOT NULL COMMENT 'simulation that owns this run',
  `realisation` varchar(20) CHARACTER SET utf8 DEFAULT NULL COMMENT 'rip for this run - by default takes value of simulation, but can indicate the ensemble element within a simulation.  Can include ranges.',
  `realisation_info` varchar(300) CHARACTER SET utf8 DEFAULT NULL COMMENT 'short text to identify variant',
  `start_date` datetime NOT NULL COMMENT 'start date/time for complete run',
  `end_date` datetime NOT NULL COMMENT 'end date/time for complete run',
  `sim_start_date` datetime NOT NULL COMMENT 'start date/time for part of run that contributes to simulation',
  `sim_end_date` datetime NOT NULL COMMENT 'end date/time for part of run that contributes to simulation',
  `atmos_mean` datetime DEFAULT NULL COMMENT 'date origin for non-ocean meaning',
  `ocean_mean` datetime DEFAULT NULL COMMENT 'date origin for ocean meaning',
  `weblink` varchar(150) CHARACTER SET utf8 DEFAULT NULL COMMENT 'url link to more information',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` char(20) CHARACTER SET utf8 NOT NULL COMMENT 'person/process responsible for last update',
  `o_type` enum('RUN') CHARACTER SET utf8 NOT NULL DEFAULT 'RUN' COMMENT 'object type label',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci COMMENT='details on a specific model run';

--
-- Dumping data for table `pt_modelrun`
--

INSERT INTO `pt_modelrun` (`id`, `suiteid`, `revision`, `runname`, `simulationid`, `realisation`, `realisation_info`, `start_date`, `end_date`, `sim_start_date`, `sim_end_date`, `atmos_mean`, `ocean_mean`, `weblink`, `upd_date`, `upd_by`, `o_type`) VALUES
(10001, 'u-aj040', '1234', 'u-aj040', 10000, 'r1i1p1f1', NULL, '1978-12-01 00:00:00', '1980-05-07 00:00:00', '1979-01-01 00:00:00', '1980-06-01 00:00:00', '1859-12-01 00:00:00', '1859-12-01 00:00:00', NULL, '2017-05-03 09:25:33', 'admin', 'RUN');

-- --------------------------------------------------------

--
-- Table structure for table `pt_programme`
--

CREATE TABLE IF NOT EXISTS `pt_programme` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for project record',
  `sname` varchar(20) NOT NULL COMMENT 'shortname or code for project (e.g cmip5)',
  `name` varchar(100) NOT NULL COMMENT 'full name for project',
  `info` text COMMENT 'short text description for project',
  `weblink` varchar(150) DEFAULT NULL COMMENT 'url to project website',
  `upd_by` char(20) NOT NULL COMMENT 'person/process responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `visible` char(2) NOT NULL DEFAULT 'TT',
  `o_type` varchar(30) NOT NULL DEFAULT 'PROGRAMME' COMMENT 'used by utility tables',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='projects information (e.g. CIM activity)';

--
-- Dumping data for table `pt_programme`
--

INSERT INTO `pt_programme` (`id`, `sname`, `name`, `info`, `weblink`, `upd_by`, `upd_date`, `visible`, `o_type`) VALUES
(10000, 'CMIP6-TEST', 'test CMIP6 programme', 'Test area - not to be used for CMIP6 simulations x', '', 'markelk', '2016-08-02 09:31:01', 'TT', 'PROGRAMME'),
(10001, 'CMIP6', 'Coupled Model Intercomparison Project 6', 'The Coupled Model Intercomparison Project (CMIP) is one of the foundational elements of climate science. It consists of three major elements: (1) a handful of common experiments, the DECK (Diagnostic, Evaluation and Characterization of Klima experiments) and the CMIP Historical Simulation (1850–near-present) that maintain continuity and help document basic characteristics of models across different phases of CMIP; (2) common standards, coordination, infrastructure and documentation that will facilitate the distribution of model outputs and the characterization of the model ensemble; and (3) an ensemble of CMIP-Endorsed Model Intercomparison Projects (MIPs) that will be specific to a particular phase of CMIP and that will build on the DECK and the CMIP Historical Simulation to address a large range of specific questions and fill the scientific gaps of the previous CMIP phases. The scientific backdrop for CMIP6 is the World Climate Research Programme (WCRP) grand challenges: 1. Clouds, Circulation and Climate Sensitivity; 2. Changes in Cryosphere; 3. Climate Extremes; 4. Regional Sea-level Rise; 5. Water Availability; 6. Decadal Predictability (pending); 7. Biogeochemical Forcings and Feedbacks (pending). Furthermore CMIP6 will address three broad questions: (i) how does the Earth system respond to forcing? (ii) what are the origins and consequences of systematic model biases? and (iii) how can we assess future climate changes given climate variability, predictability and uncertainties in scenarios? \r\n', 'http://www.wcrp-climate.org/wgcm-cmip/wgcm-cmip6', 'marke', '2016-03-19 15:44:28', 'TT', 'PROGRAMME');

-- --------------------------------------------------------

--
-- Table structure for table `pt_project`
--

CREATE TABLE IF NOT EXISTS `pt_project` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for project record',
  `programmeid` int(11) NOT NULL COMMENT 'parent programme id',
  `sname` char(20) NOT NULL COMMENT 'shortname or code for project (e.g cmip5)',
  `name` varchar(100) NOT NULL COMMENT 'full name for project',
  `info` text COMMENT 'short text description for project',
  `weblink` varchar(150) DEFAULT NULL COMMENT 'url to project website',
  `dataowner` int(11) NOT NULL COMMENT 'institute owning the data produced by this project',
  `datalicense` text COMMENT 'text for data licence to be used in data files',
  `datause` text COMMENT 'description of data use restrictions',
  `configdefault` varchar(10) DEFAULT NULL COMMENT 'default CDDS configuration version to be used for all simulations',
  `upd_by` char(20) NOT NULL COMMENT 'person/process responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `o_type` char(10) NOT NULL DEFAULT 'PROJECT' COMMENT 'fixed object type to use in master-detail relationship',
  `visible` char(2) NOT NULL DEFAULT 'TT',
  `esdoc_id` text COMMENT 'id from esdoc specialisation',
  `esdoc_hash` text COMMENT 'hash from esdoc specialisation',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='projects information (e.g. CIM activity)';

--
-- Dumping data for table `pt_project`
--

INSERT INTO `pt_project` (`id`, `programmeid`, `sname`, `name`, `info`, `weblink`, `dataowner`, `datalicense`, `datause`, `configdefault`, `upd_by`, `upd_date`, `o_type`, `visible`, `esdoc_id`, `esdoc_hash`) VALUES
(10001, 10001, 'DECK', 'Diagnostic, Evaluation and Characteristics of Klima experiments', 'Primary Goals: To maintain continuity and help document basic characteristics of models across different phases of CMIP.\r\nAim/Objectives: In principle each new model configuration in CMIP6 should perform a set of DECK experiments. ', '', 1, '2', '1', NULL, 'pamv', '2016-03-02 08:38:30', 'PROJECT', 'TT', NULL, NULL),
(10002, 10001, 'historical', 'CMIP6 Historical Simulation', 'Primary Goals: To maintain continuity and help document basic characteristics of models across different phases of CMIP.\r\nAim/Objectives: In principle each new model configuration in CMIP6 should perform a set of historical experiments to reproduce observed climate and climate change starting in 1850 and extending to the near present (end of 2014 for CMIP6).  The CMIP historical experiment branches from the piControl and is forced, based on observations, by evolving, externally-imposed forcings such as solar variability, volcanic aerosols, and changes in atmospheric composition (GHGs and aerosols) caused by human activities. It provides rich opportunities to assess model ability to simulate climate, including variability and century time-scale trends and it has also proven essential in reducing uncertainty in radiative forcing associated with short lived species such as the atmospheric aerosol. When supplemented with additional experiments, the Historical Simulation can be used in detection and attribution studies to help interpret the extent to which observed climate change can be explained by different causes.', '', 1, '2', '1', NULL, 'pamv', '2016-03-02 08:38:49', 'PROJECT', 'TT', NULL, NULL),
(10003, 10001, 'ScenarioMIP', 'Scenario Model Intercomparison Project', 'Primary Goals: (a) Facilitating integrated research on the impact of plausible future scenarios over physical and human systems, and on mitigation and adaptation options; (b) addressing targeted studies on the effects of particular forcings in collaboration with other MIPs; (c) help quantifying projection uncertainties based on multi-model ensembles and emergent constraints.\r\nAim/Objectives: The objectives of ScenarioMIP are to (1) define and recommend an experimental design for future scenarios to be run by climate models as part of CMIP6; (2) coordinate the provision of IAM scenario information to climate modeling groups and (3) coordinate the production of climate model simulations and facilitate provision of output.', 'http://cmip.ucar.edu/scenario-mip', 1, '2', '1', '1.0', 'pamv', '2017-06-08 16:03:21', 'PROJECT', 'TT', NULL, NULL),
(10004, 10001, 'C4MIP', 'Coupled Climate Carbon Cycle Model Intercomparison Project', 'Primary Goals: Understanding and quantifying future century-scale changes in the global carbon cycle and its feedbacks on the climate system, making the link between CO2 emissions and climate change.\r\nAim/Objectives: The primary aim of C4MIP is to understand and quantify future (century-scale) changes in the global carbon cycle and its feedbacks on the climate system, making the link between CO2 emissions and climate change. This objective is obtained through idealized, historical  and future scenario experiments.\r\nC4MIP addresses the WCRP’s grand challenges related to biospheric forcings and feedbacks, and water availability and is the only MIP that addresses the coupled climate carbon cycle interactions in ESMs focusing both on land and ocean carbon components.\r\nCMIP5 results from 1% per year increasing CO2 simulations showed there were large differences especially in the response of the land carbon cycle components to atmospheric CO2 forcing. C4MIP is the only MIP that addresses the [CO2 emissions > CO2 concentration > climate response] causal chain, allowing to quantify carbon emissions to meet climate targets and the transient climate response to cumulative emissions (TCRE) metric. A large fraction of the uncertainty in TCRE comes from the carbon cycle.', 'http://c4mip.lsce.ipsl.fr/', 1, '2', '1', NULL, 'pamv', '2016-03-02 08:14:52', 'PROJECT', 'TT', NULL, NULL),
(10005, 10001, 'CFMIP', 'Cloud Feedback Model Intercomparison Project', 'Primary Goals: Improved assessments of cloud feedbacks via (a) improved understanding of cloud- climate feedback mechanisms and (b) better evaluation of clouds and cloud feedbacks in climate models. Also improved understanding of circulation, regional-scale precipitation and non-linear changes.\r\nAim/Objectives: (1) to inform improved assessments of climate change cloud feedbacks by: (a) improving our understanding of cloud-climate feedback mechanisms and (b) improving evaluation of clouds and cloud feedbacks in climate models; and (2) to use the CFMIP experimental hierarchy and process diagnostics to better understand other aspects of the climate response, such as changes in circulation, regional-scale precipitation and non-linear change.', 'http://cfmip.metoffice.com', 1, '2', '1', NULL, 'pamv', '2016-03-02 08:19:37', 'PROJECT', 'TT', NULL, NULL),
(10006, 10001, 'DAMIP', 'Detection and Attribution Model Intercomparison Project', 'Primary Goals: (1) estimating the contribution of external forcings to observed global and regional climate changes; and (2) observationally constraining future climate change projections by scaling future GHG and other anthropogenic responses using regression coefficients derived for the historical period.\r\nAim/Objectives: Detection and attribution studies (D&A) investigate whether climate has changed significantly and if so what has caused such changes. Generally, D&A studies are based on historical climate change experiments of AOGCMs forced by anthropogenic and natural external forcing agents (ALL), and experiments using individual forcings or subsets of forcings. Combinations of ALL runs and separated forcing experiments from AOGCMs participating in CMIP6 are essential for model evaluation, better understanding of historical climate changes, and observational constraints on future climate change projections. The extension of experiments from 2005 to near-present is key to understanding the reasons for the recent hiatus of climate warming, and for more closely constraining uncertainties in future climate projections. ', '', 1, '2', '1', NULL, 'pamv', '2016-03-02 08:57:17', 'PROJECT', 'TT', NULL, NULL),
(10007, 10001, 'DCPP', 'Decadal Climate Prediction Project', 'Primary Goals: Predicting and understanding forced climate change and internal variability up to 10 years into the future through a coordinated set of hindcast experiments, targeted experiments to understand the physical processes, and the ongoing production of skilful decadal predictions.\r\nAim/Objectives: The term “decadal prediction” encompasses predictions on annual, multi-annual to decadal timescales. The possibility of making skillful forecasts on these timescales and the ability to do so is investigated by means predictability studies and retrospective predictions (or hindcasts) made using the current generation climate models as well as statistical approaches. Skillful decadal prediction of relevant climate parameters is a key deliverable of the WCRP\'s Grand Challenge of providing  regional climate information. The DCPP envisions three components: (1) hindcasts, (2) forecasts and (3) predictability, mechanisms and case studies.', 'http://www.wcrp-climate.org/dcp-overview', 1, '2', '1', NULL, 'pamv', '2016-03-02 08:54:56', 'PROJECT', 'TT', NULL, NULL),
(10008, 10001, 'HighResMIP', 'High Resolution Model Intercomparison Project', 'Primary Goals: Assessing the robustness of improvements in the representation of important climate processes with ‘weather-resolving’ global model resolutions ( 25 km or finer), within a simplified framework using the physical climate system only with constrained aerosol forcing.\r\nAim/Objectives: The objectives of HighResMIP are (1) to investigate the robustness across a multi-model ensemble of changes to the representation of climate processes as model horizontal resolution is increased and (2) to find out if there is any convergence with resolution across models.', 'https://dev.knmi.nl/projects/highresmip/wiki', 1, '2', '1', NULL, 'pamv', '2016-03-07 12:27:56', 'PROJECT', 'TT', NULL, NULL),
(10009, 10001, 'RFMIP', 'Radiative Forcing Model Intercomparison Project', 'Primary Goals: (a) Characterizing the global and regional effective radiative forcing for each model for historical and 4xCO2 simulations; (b) assessing the absolute accuracy of clear-sky radiative transfer parameterizations; (c) identifying the robust impacts of aerosol radiative forcing during the historical period.\r\nAim/Objectives: The aim of RFMIP is to evaluate RF within climate models in order to understand the range of surface temperature change and errors in models.\r\n', '', 1, '2', '1', NULL, 'pamv', '2016-03-02 09:22:03', 'PROJECT', 'TT', NULL, NULL),
(10010, 10001, 'LUMIP', 'Land-Use Model Intercomparison Project', 'Primary Goals: Quantifying the effects of land use on climate and biogeochemical cycling (past-future), and assessing the potential for alternative land management strategies to mitigate climate change.\r\nAim/Objectives: Human land-use activities have resulted in large changes to the biogeochemical and biophysical properties of the Earth surface, with resulting implications for climate. In the future, land-use activities are likely to expand and/or intensify further to meet growing demands for food, fiber, and energy. CMIP5 achieved a qualitative scientific advance in studying the effects of land-use on climate, for the first time explicitly accounting for the effects of global gridded land-use changes (past-future) in coupled carbon-climate model projections. Enabling this advance, the first consistent gridded land-use dataset (past-future) was developed, linking historical land-use data, to future projections from Integrated Assessment Models, in a standard format required by climate models. Results indicate that the effects of land-use on climate, while uncertain, are sufficiently large and complex to warrant an expanded activity focused on land-use for CMIP6.', 'https://cmip.ucar.edu/lumip', 1, '2', '1', NULL, 'pamv', '2016-03-02 09:51:18', 'PROJECT', 'TT', NULL, NULL),
(10011, 10001, 'GeoMIP', ' Geoengineering Model Intercomparison Project', 'Primary Goals: Assessing the climate system response (including on extreme events) to proposed radiation modification geoengineering schemes by evaluating their efficacies, benefits, and side effects.\r\nAim/Objectives: The Geoengineering Model Intercomparison Project (GeoMIP) was designed to determine robust climate system model responses to solar geoengineering. GeoMIP currently consists of four standardized simulations involving reduction of insolation or increased amounts of stratospheric sulfate aerosols. Three more experiments involving marine cloud brightening are planned. This project has improved confidence in the expected climate effects of geoengineering in several key areas, such as the effects of geoengineering on spatial patterns of temperature and the spatial distribution of precipitation, especially extreme precipitation events. However, GeoMIP has also highlighted several important research gaps, such as the effects on terrestrial net primary productivity and the importance of the CO2 physiological effect in determining the hydrologic cycle response to geoengineering. Future efforts will endeavor to address these gaps, as well as encourage cooperation with the chemistry modeling communities, the impact assessment communities, and other groups interested in model output.', 'http://climate.envsci.rutgers.edu/GeoMIP/index.html', 1, '2', '1', NULL, 'pamv', '2016-03-02 11:10:20', 'PROJECT', 'TT', NULL, NULL),
(10012, 10000, 'ScenarioMIP', 'Scenario Model Intercomparison Project', 'Primary Goals: (a) Facilitating integrated research on the impact of plausible future scenarios over physical and human systems, and on mitigation and adaptation options; (b) addressing targeted studies on the effects of particular forcings in collaboration with other MIPs; (c) help quantifying projection uncertainties based on multi-model ensembles and emergent constraints.\r\nAim/Objectives: The objectives of ScenarioMIP are to (1) define and recommend an experimental design for future scenarios to be run by climate models as part of CMIP6; (2) coordinate the provision of IAM scenario information to climate modeling groups and (3) coordinate the production of climate model simulations and facilitate provision of output.', 'http://cmip.ucar.edu/scenario-mip', 1, '2', '1', NULL, 'marke', '2016-03-23 12:00:07', 'PROJECT', 'TT', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `pt_region`
--

CREATE TABLE IF NOT EXISTS `pt_region` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'domain id',
  `projectid` int(11) NOT NULL COMMENT 'project id',
  `sname` varchar(20) NOT NULL COMMENT 'domain code - project specific (e.g. AFR-44i)',
  `name` varchar(100) NOT NULL COMMENT 'full name - defaults to code description',
  `info` text COMMENT 'description of domain',
  `resolution` float(7,2) DEFAULT NULL COMMENT 'resolution in degrees (e.g. 0.44)',
  `np_lon` float(7,2) DEFAULT NULL COMMENT 'if rotated pole - longitude of north pole otherwise NULL',
  `np_lat` float(7,2) DEFAULT NULL COMMENT 'if rotated pole - latitude of north pole otherwise NULL',
  `n_lon` int(10) DEFAULT NULL COMMENT 'no. of grid cells in longitude',
  `n_lat` int(10) DEFAULT NULL COMMENT 'no. of grid cells in latitude',
  `west` float(7,2) DEFAULT NULL COMMENT 'centre of most westerly cell - in rotated or geographic coordinates',
  `east` float(7,2) DEFAULT NULL COMMENT 'centre of most easterly cell - in rotated or geographic coordinates',
  `south` float(7,2) DEFAULT NULL COMMENT 'centre of most southerly cell - in rotated or geographic coordinates',
  `north` float(7,2) DEFAULT NULL COMMENT 'centre of most northerly cell - in rotated or geographic coordinates',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` varchar(20) NOT NULL COMMENT 'person/process responsible for last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='defines regional domains for a project';

-- --------------------------------------------------------

--
-- Table structure for table `pt_reqt_attribute`
--

CREATE TABLE IF NOT EXISTS `pt_reqt_attribute` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for requirement attribute',
  `requirementid` int(11) NOT NULL COMMENT 'id for requirement attribute is related to ',
  `meta_type` varchar(40) NOT NULL COMMENT 'code for attribute type (CIM:metadata_type)',
  `meta_value` varchar(100) NOT NULL COMMENT 'value for attribute type (CIM:metadata_value)',
  `upd_by` varchar(20) NOT NULL COMMENT 'user for record update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of record update',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `pt_reqt_attribute`
--

INSERT INTO `pt_reqt_attribute` (`id`, `requirementid`, `meta_type`, `meta_value`, `upd_by`, `upd_date`) VALUES
(10000, 10000, 'start_date', '1860-01-01', 'marke', '2017-02-09 17:53:31'),
(10001, 10000, 'end_date', '2010-12-30', 'marke', '2017-02-09 17:53:31');

-- --------------------------------------------------------

--
-- Table structure for table `pt_requirement`
--

CREATE TABLE IF NOT EXISTS `pt_requirement` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'requirement id',
  `parent_id` int(11) NOT NULL COMMENT 'id to parent experiment or requirement',
  `parent_type` enum('EXPERIMENT','REQUIREMENT') NOT NULL DEFAULT 'EXPERIMENT' COMMENT 'parent type for requirement - either experiment or another requirement',
  `s_name` varchar(150) NOT NULL COMMENT 'requirement name (CIM:canonical_name)',
  `s_label` varchar(200) DEFAULT NULL COMMENT 'label for requirement (CIM:label)',
  `s_info` varchar(1000) DEFAULT NULL COMMENT 'description of requirement (CIM:description)',
  `s_required` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'if set - then conformance information must be provided (CIM:is_conformance_required)',
  `s_reqt_type` varchar(40) NOT NULL COMMENT 'code value for requirement type (CIM:type)',
  `s_keywords` varchar(200) DEFAULT NULL COMMENT 'keywords related to requirement (CIM:keywords)',
  `s_scope` varchar(500) DEFAULT NULL COMMENT 'requirement scope (CIM:scope)',
  `s_ordinal` int(3) DEFAULT NULL COMMENT 'requirement order (CIM:delivery_order)',
  `conform_status` varchar(20) DEFAULT NULL COMMENT 'coded conformance status (full, partial, none)',
  `conform_method` varchar(100) DEFAULT NULL COMMENT 'coded conformance method',
  `conform_info` varchar(1000) DEFAULT NULL COMMENT 'conformance description',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` char(20) NOT NULL COMMENT 'person responsible for last update',
  `esdoc_id` text COMMENT 'id from esdoc specialisation',
  `esdoc_hash` text COMMENT 'hash from esdoc specialisation',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='describes project requirements';

--
-- Dumping data for table `pt_requirement`
--

INSERT INTO `pt_requirement` (`id`, `parent_id`, `parent_type`, `s_name`, `s_label`, `s_info`, `s_required`, `s_reqt_type`, `s_keywords`, `s_scope`, `s_ordinal`, `conform_status`, `conform_method`, `conform_info`, `upd_date`, `upd_by`, `esdoc_id`, `esdoc_hash`) VALUES
(10000, 10110, 'EXPERIMENT', 'test.requirement.1', 'simulation period', 'The simulation period shall be 150 years starting in 1860', 1, 'spatiotemporal', '', 'DECK, SCENARIO', 1, 'conformed', 'model_configuration', '', '2017-02-09 17:56:16', 'admin', NULL, NULL),
(10001, 10110, 'EXPERIMENT', 'test.requirement.2', 'CO2 forcing', 'Use SSP2.6 well-mixed CO2 forcing data', 0, 'forcing', '', '', 2, 'not conformed', 'forcing_data', 'We screwed up at 2080', '2017-02-22 13:04:31', 'admin', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `pt_simulation`
--

CREATE TABLE IF NOT EXISTS `pt_simulation` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'simulation id',
  `modelid` int(11) NOT NULL COMMENT 'model id',
  `experimentid` int(11) NOT NULL COMMENT 'experiment id',
  `projectid` int(11) NOT NULL COMMENT 'project id',
  `sname` char(40) CHARACTER SET utf8 NOT NULL COMMENT 'simulation shortname',
  `name` varchar(200) CHARACTER SET utf8 NOT NULL COMMENT 'simulation descriptive name',
  `info` text CHARACTER SET utf8 COMMENT 'additional information about simulation (used as comment in header)',
  `weblink` varchar(150) CHARACTER SET utf8 DEFAULT NULL COMMENT 'url link to additional information',
  `model_config` varchar(100) CHARACTER SET utf8 NOT NULL COMMENT 'coded model configuratio for this simulation as defined for the CMIP source_type attribute',
  `timestep` int(6) DEFAULT NULL COMMENT 'model timestep in seconds (if not as defined for model)',
  `calendar` varchar(40) CHARACTER SET utf8 NOT NULL COMMENT 'type of calendar used for this simulation',
  `start_date` datetime DEFAULT NULL COMMENT 'start date/time for complete simulation',
  `end_date` datetime DEFAULT NULL COMMENT 'end date/time for complete simulation',
  `suiteid` varchar(40) CHARACTER SET utf8 DEFAULT NULL COMMENT 'ROSE suite id to be used to gather metadata',
  `contactid` int(11) DEFAULT NULL COMMENT 'person coordinating the simulation',
  `configversion` varchar(10) CHARACTER SET utf8 DEFAULT NULL COMMENT 'CDDS configuration version used for this simulation (should default to value in pt_project)',
  `modelversion` varchar(40) CHARACTER SET utf8 DEFAULT NULL COMMENT 'version code for model (e.g. 6.6.4)',
  `realisation` varchar(20) CHARACTER SET utf8 NOT NULL COMMENT 'realisation code (e.g. r1i1p1) - can also indicate ranges of values for ensembles',
  `realisation_info` varchar(300) CHARACTER SET utf8 DEFAULT NULL COMMENT 'short text to identify variant',
  `forcing_species` varchar(300) CHARACTER SET utf8 DEFAULT NULL COMMENT 'list of forcing codes applicable to this simulation',
  `pnt_project` int(11) DEFAULT NULL COMMENT 'project for parent simulation',
  `pnt_model` int(11) DEFAULT NULL COMMENT 'parent model id',
  `pnt_experiment` int(11) DEFAULT NULL COMMENT 'parent experiment name (e.g. picontrol)',
  `pnt_realisation` varchar(20) CHARACTER SET utf8 DEFAULT NULL COMMENT 'parent simulation',
  `pnt_basedate_parent` date DEFAULT NULL COMMENT 'base date for parent simulation',
  `pnt_branch_parent` date DEFAULT NULL COMMENT 'branch date in parent simulation',
  `pnt_basedate_child` date DEFAULT NULL COMMENT 'base date for child (this) simulation',
  `pnt_branch_child` date DEFAULT NULL COMMENT 'branch date in child (this) simulation',
  `pnt_type` varchar(200) CHARACTER SET utf8 NOT NULL COMMENT 'parent type code (e.g. parallel, cotinuation)',
  `pnt_notes` varchar(500) CHARACTER SET utf8 DEFAULT NULL COMMENT 'parent notes',
  `bnd_project` varchar(40) CHARACTER SET utf8 DEFAULT NULL COMMENT 'project for boundary simulation - text because it might be an external project',
  `bnd_model` varchar(60) CHARACTER SET utf8 DEFAULT NULL COMMENT 'e.g. MOHC-HadGEM2-ES - text because it might be an external model',
  `bnd_experiment` varchar(60) CHARACTER SET utf8 DEFAULT NULL COMMENT 'boundary experiment (e.g. rcp45)',
  `bnd_realisation` varchar(20) CHARACTER SET utf8 DEFAULT NULL COMMENT 'boundary simulation realisation',
  `bnd_notes` varchar(500) CHARACTER SET utf8 DEFAULT NULL COMMENT 'notes about boundary simulation',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` char(20) CHARACTER SET utf8 NOT NULL COMMENT 'person/process responsible for last update',
  `log` text CHARACTER SET utf8 COMMENT 'text describing activity on the simulation',
  `o_type` enum('SIMULATION') CHARACTER SET utf8 NOT NULL DEFAULT 'SIMULATION' COMMENT 'object type code',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci COMMENT='describes project simulation';

--
-- Dumping data for table `pt_simulation`
--

INSERT INTO `pt_simulation` (`id`, `modelid`, `experimentid`, `projectid`, `sname`, `name`, `info`, `weblink`, `model_config`, `timestep`, `calendar`, `start_date`, `end_date`, `suiteid`, `contactid`, `configversion`, `modelversion`, `realisation`, `realisation_info`, `forcing_species`, `pnt_project`, `pnt_model`, `pnt_experiment`, `pnt_realisation`, `pnt_basedate_parent`, `pnt_branch_parent`, `pnt_basedate_child`, `pnt_branch_child`, `pnt_type`, `pnt_notes`, `bnd_project`, `bnd_model`, `bnd_experiment`, `bnd_realisation`, `bnd_notes`, `upd_date`, `upd_by`, `log`, `o_type`) VALUES
(10000, 10001, 10110, 10012, 'HadGEM3-GC31-LL_ssp245_r1i1p1f1', 'primary rcp45 run', '', '', '', 20, '360_day', '1980-01-01 00:00:00', '2000-01-01 00:00:00', 'u_ab634', 1, '1.0', '3.1', 'r1i1p1f1', NULL, NULL, 10001, 10001, 0, '', '1860-01-01', '1900-01-01', '1860-01-01', '1860-01-01', 'n/a', '', '', '', '', '', '', '2018-12-13 09:44:20', 'admin', '', 'SIMULATION');

-- --------------------------------------------------------

--
-- Table structure for table `rt_file_manifest`
--

CREATE TABLE IF NOT EXISTS `rt_file_manifest` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `filename` varchar(255) NOT NULL COMMENT 'file name',
  `variable` varchar(30) NOT NULL COMMENT 'variable short name (e.g. tas)',
  `start_date` datetime DEFAULT NULL COMMENT 'data start date/time as extracted from filename',
  `end_date` datetime DEFAULT NULL COMMENT 'data end date/time as extracted from filename',
  `version` varchar(30) DEFAULT NULL COMMENT 'version code for file',
  `current_state` varchar(20) DEFAULT NULL COMMENT 'Currebt state in MASS archive (e.g. embargoed, available, withdrawn)',
  `create_date` datetime NOT NULL COMMENT 'date/time file created',
  `transfer_date` datetime NOT NULL COMMENT 'date/time file transferred to MASS',
  `available_date` datetime DEFAULT NULL COMMENT 'date made available for publishing',
  `checksum` varchar(255) DEFAULT NULL COMMENT 'checksum value',
  `programmeid` int(11) DEFAULT NULL COMMENT 'id for associated programme',
  `projectid` int(11) DEFAULT NULL COMMENT 'id for crem project record',
  `experimentid` int(11) DEFAULT NULL COMMENT 'id for associated experiment',
  `requestid` int(11) DEFAULT NULL COMMENT 'id for crem request record',
  `upd_by` varchar(20) NOT NULL COMMENT 'last update by',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `rt_filter`
--

CREATE TABLE IF NOT EXISTS `rt_filter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `variable` varchar(20) NOT NULL COMMENT 'variable short name',
  `miptable` varchar(20) NOT NULL COMMENT 'mip table name',
  `model` varchar(30) NOT NULL COMMENT 'model name (short)',
  `stream` varchar(20) NOT NULL COMMENT 'data stream name',
  `filters` varchar(300) NOT NULL COMMENT 'stash constraint in specific format',
  `projects` varchar(200) NOT NULL COMMENT 'comma separated list of projects that this filter is relevant to',
  `experiments` varchar(200) NOT NULL COMMENT 'experiment constraint if only used for specific experiments (comma separate list)',
  `comment` varchar(200) DEFAULT NULL COMMENT 'notes',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `rt_history`
--

CREATE TABLE IF NOT EXISTS `rt_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for history record',
  `requestid` int(11) NOT NULL COMMENT 'id for related request',
  `process_type` char(40) NOT NULL COMMENT 'type of process (system code)',
  `host` char(20) DEFAULT NULL COMMENT 'host running process',
  `user` char(20) DEFAULT NULL COMMENT 'user owning process',
  `uid` char(10) DEFAULT NULL COMMENT 'user id',
  `pid` char(10) DEFAULT NULL COMMENT 'process id',
  `status_value` varchar(100) NOT NULL COMMENT 'current status (system code - process specific)',
  `notes` text COMMENT 'notes relating to status change',
  `process_status` varchar(500) DEFAULT NULL COMMENT 'updates to process progress',
  `upd_by` varchar(20) NOT NULL COMMENT 'person/process responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'date of last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='maintains history of status changes for request';

--
-- Dumping data for table `rt_history`
--

INSERT INTO `rt_history` (`id`, `requestid`, `process_type`, `host`, `user`, `uid`, `pid`, `status_value`, `notes`, `process_status`, `upd_by`, `upd_date`) VALUES
(111, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '24126', 'IP', '', 'extract processing started', 'marke', '2016-11-03 15:52:49'),
(112, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '28739', 'IP', '', 'extract processing started', 'marke', '2016-11-03 16:01:47'),
(113, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '30244', 'IP', '', 'extract processing started', 'marke', '2016-11-03 16:04:46'),
(114, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '15115', 'IP', ' | Stream Start:  apa  ---------------- start: 1978-09-01 00:00:00  end: 2035-08-01 00:00:00  ', 'starting task: ', 'marke', '2016-11-03 16:39:34'),
(115, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '15115', 'SP', 'user request', 'extract processing suspended', 'marke', '2016-11-03 16:41:48'),
(116, 10000, 'extract', 'eld278', 'hadel', '4119', '29353', 'CF', 'ERROR failed to create data directory\n            root: /data/local10/ar5\n            map: programme|project|model|experiment|realisation\n            name: /data/local10/ar5/CMIP6-TEST/ScenarioMIP/HadGEM3-GC31-LL/ssp245/r1i1p1f1\n            status: failed\n            error: Problem creating subdirectory /data/local10 in directory path /data/local10/ar5/CMIP6-TEST/ScenarioMIP/HadGEM3-GC31-LL/ssp245/r1i1p1f1 [Permission denied - [hadel:users]]\n        ', 'extract processing failed', 'marke', '2017-03-16 10:38:25'),
(117, 10000, 'extract', 'eld278', 'hadel', '4119', '13286', 'CF', 'ERROR failed to create data directory\n            root: /data/local10/ar5\n            map: programme|project|model|experiment|realisation\n            name: /data/local10/ar5/CMIP6-TEST/ScenarioMIP/HadGEM3-GC31-LL/ssp245/r1i1p1f1\n            status: failed\n            error: Problem creating subdirectory /data/local10 in directory path /data/local10/ar5/CMIP6-TEST/ScenarioMIP/HadGEM3-GC31-LL/ssp245/r1i1p1f1 [Permission denied - [hadel:users]]\n        ', 'extract processing failed', 'marke', '2017-03-23 15:32:04'),
(118, 10000, 'extract', 'eld278', 'hadel', '4119', '25601', 'CF', 'ERROR failed to create data directory\n            root: /data/local10/ar5\n            map: programme|project|model|experiment|realisation\n            name: /data/local10/ar5/CMIP6-TEST/ScenarioMIP/HadGEM3-GC31-LL/ssp245/r1i1p1f1\n            status: failed\n            error: Problem creating subdirectory /data/local10 in directory path /data/local10/ar5/CMIP6-TEST/ScenarioMIP/HadGEM3-GC31-LL/ssp245/r1i1p1f1 [Permission denied - [hadel:users]]\n        ', 'extract processing failed', 'marke', '2017-03-28 13:43:46'),
(119, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '21011', 'IP', '', 'extract processing started', 'marke', '2017-03-28 14:37:42'),
(120, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '2690', 'IP', '', 'extract processing started', 'marke', '2017-03-29 15:12:43'),
(121, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '2690', 'CF', 'variables file [/home/h06/hadel/MO_DEV/CMIP6/variables/CMIP6-TEST/ScenarioMIP/ssp245/HadGEM3-GC31-LL.json] not found or not readable [error: file missing]', 'failed', 'marke', '2017-03-29 15:12:48'),
(122, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '22000', 'IP', '', 'extract processing started', 'marke', '2017-03-29 15:58:54'),
(123, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '22000', 'CF', 'variables file [/home/h06/hadel/MO_DEV/CMIP6/variables/CMIP6-TEST/ScenarioMIP/CMIP6-TEST_ScenarioMIP_ssp245_HadGEM3-GC31-LL.json] not found or not readable [error: file missing]', 'failed', 'marke', '2017-03-29 15:58:59'),
(124, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '25021', 'IP', '', 'extract processing started', 'marke', '2017-03-29 16:05:03'),
(125, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '25021', 'CF', 'variables file [/home/h06/hadel/MO_DEV/CMIP6/variables/CMIP6-TEST/ScenarioMIP/CMIP6-TEST_ScenarioMIP_ssp245_HadGEM3-GC31-LL.json] not found or not readable [error: file missing]', 'failed', 'marke', '2017-03-29 16:05:08'),
(130, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '32397', 'IP', '', 'extract processing started', 'marke', '2017-03-30 11:29:46'),
(131, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '873', 'IP', '', 'extract processing started', 'marke', '2017-03-30 11:31:20'),
(132, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '1339', 'IP', '', 'extract processing started', 'marke', '2017-03-30 11:32:56'),
(133, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '5369', 'IP', '', 'extract processing started', 'marke', '2017-03-30 11:41:55'),
(134, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '8020', 'IP', '', 'extract processing started', 'marke', '2017-03-30 11:47:22'),
(135, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '11848', 'IP', '', 'extract processing started', 'marke', '2017-03-30 11:56:24'),
(136, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '13549', 'IP', '', 'extract processing started', 'marke', '2017-03-30 12:01:01'),
(137, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '16566', 'IP', '', 'extract processing started', 'marke', '2017-03-30 12:07:30'),
(138, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '19934', 'IP', '', 'extract processing started', 'marke', '2017-03-30 12:15:36'),
(139, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '31206', 'IP', '', 'extract processing started', 'marke', '2017-03-30 12:42:06'),
(140, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '8753', 'IP', '', 'extract processing started', 'marke', '2017-03-30 15:37:52'),
(141, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '12538', 'IP', '', 'extract processing started', 'marke', '2017-03-30 15:46:32'),
(142, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '25109', 'IP', '', 'extract processing started', 'marke', '2017-03-30 16:16:07'),
(143, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '21376', 'IP', '', 'extract processing started', 'marke', '2017-03-31 08:42:07'),
(144, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '28650', 'IP', '', 'extract processing started', 'marke', '2017-03-31 08:58:40'),
(145, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '3264', 'IP', '', 'extract processing started', 'marke', '2017-03-31 09:15:17'),
(146, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '7059', 'IP', '', 'extract processing started', 'marke', '2017-03-31 09:24:38'),
(147, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '9752', 'IP', '', 'extract processing started', 'marke', '2017-03-31 09:29:49'),
(148, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'IP', ' | Stream Start:  apa  ---------------- start: 2006-01-01 00:00:00  end: 2006-12-02 00:00:00  ', 'starting task: ', 'marke', '2017-03-31 09:33:09'),
(149, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-03-31 09:36:25'),
(150, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:28'),
(151, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:30'),
(152, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:30'),
(153, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(154, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(155, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(156, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(157, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(158, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(159, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(160, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(161, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(162, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(163, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(164, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(165, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(166, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(167, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(168, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(169, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(170, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(171, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(172, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(173, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(174, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(175, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(176, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:31'),
(177, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(178, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(179, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(180, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(181, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(182, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(183, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(184, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(185, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(186, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(187, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(188, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(189, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(190, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(191, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '11111', 'SP', 'user request', 'suspended', 'marke', '2017-03-31 09:36:32'),
(192, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '13729', 'IP', ' | Stream Start:  apa  ---------------- start: 2006-01-01 00:00:00  end: 2006-12-02 00:00:00  ', 'starting task: ', 'marke', '2017-03-31 09:37:45'),
(193, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '13729', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-03-31 09:37:56'),
(194, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '30345', 'IP', ' | Stream Start:  apa  ---------------- start: 2006-01-01 00:00:00  end: 2006-12-02 00:00:00  ', 'starting task: ', 'marke', '2017-03-31 10:19:22'),
(195, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '6604', 'IP', ' | Stream Start:  apa  ---------------- start: 2006-01-01 00:00:00  end: 2006-12-02 00:00:00  ', 'starting task: ', 'marke', '2017-03-31 10:36:23'),
(196, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '6604', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-03-31 10:36:33'),
(197, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '8101', 'IP', ' | Stream Start:  apa  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-03-31 10:39:55'),
(198, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '8101', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-03-31 10:40:06'),
(199, 10000, 'extract', 'eld254', 'hadmm', '4252', '9359', 'SP', 'user request', 'suspended', 'marke', '2017-04-06 08:48:51'),
(200, 10000, 'extract', 'eld254', 'hadmm', '4252', '9359', 'SP', 'user request', 'suspended', 'marke', '2017-04-06 08:48:53'),
(201, 10000, 'extract', 'eld254', 'hadmm', '4252', '9359', 'SP', 'user request', 'suspended', 'marke', '2017-04-06 08:48:57'),
(202, 10000, 'extract', 'eld254', 'hadmm', '4252', '9389', 'CF', 'ERROR failed to create data directory\n            root: /data/local10/ar5\n            map: programme|project|model|experiment|realisation\n            name: /data/local10/ar5/CMIP6-TEST/ScenarioMIP/HadGEM3-GC31-LL/ssp245/r1i1p1f1\n            status: failed\n            error: Problem creating subdirectory /data/local10 in directory path /data/local10/ar5/CMIP6-TEST/ScenarioMIP/HadGEM3-GC31-LL/ssp245/r1i1p1f1 [Permission denied - [hadmm:users]]\n        ', 'failed', 'marke', '2017-04-06 08:49:55'),
(203, 10000, 'extract', 'eld254', 'hadmm', '4252', '9508', 'CF', 'ERROR failed to create data directory\n            root: /data/local10/ar5\n            map: programme|project|model|experiment|realisation\n            name: /data/local10/ar5/CMIP6-TEST/ScenarioMIP/HadGEM3-GC31-LL/ssp245/r1i1p1f1\n            status: failed\n            error: Problem creating subdirectory /data/local10 in directory path /data/local10/ar5/CMIP6-TEST/ScenarioMIP/HadGEM3-GC31-LL/ssp245/r1i1p1f1 [Permission denied - [hadmm:users]]\n        ', 'failed', 'marke', '2017-04-06 08:50:57'),
(204, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '17150', 'IP', ' | Stream Start:  apa  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 10:09:25'),
(205, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '17150', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-04-06 10:09:37'),
(206, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '22550', 'IP', ' | Stream Start:  apa  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 10:21:59'),
(207, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '24415', 'IP', ' | Stream Start:  apa  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 10:26:43'),
(208, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '28297', 'IP', ' | Stream Start:  apa  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 10:35:04'),
(209, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '28297', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-04-06 10:37:24'),
(210, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '28297', 'IP', ' | Stream Start:  apa  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 10:39:00'),
(211, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '783', 'IP', ' | Stream Start:  apa  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 10:46:01'),
(212, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '1893', 'IP', ' | Stream Start:  apa  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 10:47:31'),
(213, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '1893', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-04-06 10:47:42'),
(214, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '22382', 'IP', ' | Stream Start:  apa  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 12:51:37'),
(215, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '24547', 'IP', ' | Stream Start:  apa  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream apa completed  ---------------- \n\n | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction FAILED - task rejected', '', 'marke', '2017-04-06 12:55:47'),
(216, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '24547', 'CF', 'MOOSE request failed: rejected [err: task rejected]', 'failed', 'marke', '2017-04-06 13:03:44'),
(217, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31227', 'IP', ' | Stream Start:  apm  ---------------- start: 1980-03-01 00:00:00  end: 1981-01-03 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 13:09:29'),
(218, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31227', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-04-06 13:09:40'),
(219, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31848', 'IP', ' | Stream Start:  apm  ---------------- start: 1980-03-01 00:00:00  end: 1981-01-03 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 13:10:33'),
(220, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31848', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-04-06 13:10:47'),
(221, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31848', 'IP', ' | Stream Start:  apm  ---------------- start: 1980-03-01 00:00:00  end: 1981-01-03 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 13:11:26'),
(222, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31848', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-04-06 13:11:37'),
(223, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31848', 'IP', ' | Stream Start:  apm  ---------------- start: 1980-03-01 00:00:00  end: 1981-01-03 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 13:16:56'),
(224, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31848', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-04-06 13:17:21'),
(225, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31848', 'IP', ' | Stream Start:  apm  ---------------- start: 1980-03-01 00:00:00  end: 1981-01-03 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 13:18:09'),
(226, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31848', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-04-06 13:23:13'),
(227, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31848', 'IP', ' | Stream Start:  apm  ---------------- start: 1980-03-01 00:00:00  end: 1981-01-03 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 13:26:16'),
(228, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31848', 'CF', 'could not establish number of MASS requests required [error: max number of blocks exceeded ]', 'failed', 'marke', '2017-04-06 13:27:08'),
(229, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31848', 'IP', '', 'extract processing started', 'marke', '2017-04-06 13:28:36'),
(230, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '31848', 'IP', '', 'extract processing started', 'marke', '2017-04-06 13:32:24'),
(231, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '10768', 'IP', '', 'extract processing started', 'marke', '2017-04-06 13:35:07'),
(232, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '12983', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 13:39:23'),
(233, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '13924', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 13:41:36'),
(234, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '5189', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-06 15:51:14'),
(235, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '13318', 'IP', ' | Stream Start:  apa  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream apa completed  ---------------- \n\n | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction FAILED - task rejected', '', 'marke', '2017-04-07 09:50:54'),
(236, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '13318', 'CF', 'MOOSE request failed: rejected [err: task rejected]', 'failed', 'marke', '2017-04-07 09:51:50'),
(237, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '17226', 'IP', ' | Stream Start:  apa  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream apa completed  ---------------- \n\n | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction FAILED - task rejected', '', 'marke', '2017-04-11 14:47:05'),
(238, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '17226', 'CF', 'MOOSE request failed: rejected [err: task rejected]', 'failed', 'marke', '2017-04-11 14:47:28'),
(239, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '19519', 'IP', '', 'extract processing started', 'marke', '2017-04-11 14:50:37'),
(240, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '21231', 'IP', ' | Stream Start:  ap8  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap8 completed  ---------------- \n\n | Stream Start:  ap6  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap6 completed  ---------------- \n\n', 'ending task: extract stream ap6', 'marke', '2017-04-11 14:55:17'),
(241, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '21231', 'CS', 'VALIDATION for stream ap8:\nfiles count: mismatch on number of files (expected: 36 ; actual: 37 )\nVALIDATION for stream ap6:\nfiles count: mismatch on number of files (expected: 36 ; actual: 37 )\n', 'complete / success', 'marke', '2017-04-11 15:04:03'),
(242, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '19886', 'IP', ' | Stream Start:  ap8  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-19 10:33:27'),
(243, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '19886', 'SP', 'user request', 'suspended', 'marke', '2017-04-19 10:35:31'),
(244, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '25256', 'IP', ' | Stream Start:  ap8  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap8 completed  ---------------- \n\n | Stream Start:  ap6  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap6 completed  ---------------- \n\n', 'ending task: extract stream ap6', 'marke', '2017-04-19 15:14:34'),
(245, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '25256', 'CS', 'VALIDATION for stream ap8:\nfiles count: mismatch on number of files (expected: 36 ; actual: 37 )\nVALIDATION for stream ap6:\nfiles count: correct number of files ( 36 )\n', 'complete / success', 'marke', '2017-04-19 15:17:32'),
(246, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '11017', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction FAILED - task rejected', '', 'marke', '2017-04-19 15:44:55'),
(247, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '11017', 'CF', 'MOOSE request failed: rejected [err: task rejected]', 'failed', 'marke', '2017-04-19 15:45:05'),
(248, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '31682', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-20 09:32:47'),
(249, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '3082', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-20 09:38:24'),
(250, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '6565', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-20 09:44:09'),
(251, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '10042', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-20 09:50:09'),
(252, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '10573', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction FAILED - task rejected', '', 'marke', '2017-04-20 09:51:22'),
(253, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '10573', 'CF', 'MOOSE request failed: rejected [err: task rejected]', 'failed', 'marke', '2017-04-20 09:51:31'),
(254, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '12739', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-20 09:54:31'),
(255, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '12739', 'SP', 'user request', 'suspended', 'marke', '2017-04-20 10:03:51'),
(256, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '12739', 'SP', 'user request', 'suspended', 'marke', '2017-04-20 10:03:56'),
(257, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '7686', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-20 12:26:41'),
(258, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '7686', 'CS', 'VALIDATION for stream inm:\nfiles count: mismatch on number of files (expected: 1 ; actual: 0 )\n', 'complete / success', 'marke', '2017-04-20 12:26:49'),
(259, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '18944', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-20 12:44:33'),
(260, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '18944', 'CS', 'VALIDATION for stream inm:\nfiles count: mismatch on number of files (expected: 1 ; actual: 0 )\n', 'complete / success', 'marke', '2017-04-20 12:44:41'),
(261, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '27472', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-20 12:58:36'),
(262, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '27472', 'CS', 'VALIDATION for stream inm:\nfiles count: mismatch on number of files (expected: 36 ; actual: 24 )\n', 'complete / success', 'marke', '2017-04-20 12:59:29'),
(263, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '9049', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-20 15:10:27'),
(264, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '9049', 'CS', 'VALIDATION for stream inm:\nfiles count: mismatch on number of files (expected: 36 ; actual: 24 )\n', 'complete / success', 'marke', '2017-04-20 15:11:19'),
(265, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '9637', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-20 15:11:58'),
(266, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '9637', 'CS', 'VALIDATION for stream inm:\nfiles count: mismatch on number of files (expected: 1 ; actual: 0 )\n', 'complete / success', 'marke', '2017-04-20 15:12:54'),
(267, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '10542', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-25 14:35:19'),
(268, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '13095', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-25 14:39:45'),
(269, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '15170', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-25 14:42:59'),
(270, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '19621', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-25 14:50:09'),
(271, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '21301', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-25 14:52:40'),
(272, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '26177', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-25 15:01:46'),
(273, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '28287', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-25 15:04:16'),
(274, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '838', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-25 15:12:23'),
(275, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '2939', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-25 15:16:30'),
(276, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '4693', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-25 15:18:35'),
(277, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '28513', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-26 07:21:55'),
(278, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '28513', 'CS', 'VALIDATION for stream inm:\nfiles count: mismatch on number of files (expected: 36 ; actual: 24 )\n', 'complete / success', 'marke', '2017-04-26 07:22:48'),
(279, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '26451', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-26 08:11:56'),
(280, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '26451', 'CS', 'VALIDATION for stream inm:\nstream type is netcdf - no validation performed\n', 'complete / success', 'marke', '2017-04-26 08:12:46'),
(281, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '12081', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-26 08:40:14'),
(282, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '12081', 'SP', 'user request', 'suspended', 'marke', '2017-04-26 08:43:49'),
(283, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '20252', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00  ', 'starting task: ', 'marke', '2017-04-26 08:53:32'),
(284, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '20252', 'SP', 'user request', 'suspended', 'marke', '2017-04-26 09:02:25'),
(285, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '26396', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | Stream onm failed ---------------- \n\n', 'ending task: extract stream onm', 'marke', '2017-04-26 09:03:19'),
(286, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '26396', 'CF', 'VALIDATION for stream onm:\nextract failed: no validation performed\n', 'failed', 'marke', '2017-04-26 09:05:32'),
(287, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '27252', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 33% complete: block 1: extraction success -  | task 66% complete: block 2: extraction success -  | task 100% complete: block 3: extraction success -  | Stream onm completed  ---------------- \n\n', 'ending task: extract stream onm', 'marke', '2017-04-26 10:53:28'),
(288, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '27252', 'CS', 'VALIDATION for stream onm:\nstream type is netcdf - no validation performed\n', 'complete / success', 'marke', '2017-04-26 10:55:03'),
(289, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '14075', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 33% complete: block 1: extraction success -  | task 66% complete: block 2: extraction success -  | task 100% complete: block 3: extraction success - some file(s) already existed | Stream onm completed  ---------------- \n\n', 'ending task: extract stream onm', 'marke', '2017-04-26 14:09:02'),
(290, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '14075', 'CS', 'VALIDATION for stream onm:\nstream type is netcdf - no validation performed\n', 'complete / success', 'marke', '2017-04-26 14:10:37'),
(291, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '3176', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 33% complete: block 1: extraction FAILED - requested variable not found [tauuo and maybe others]', '', 'marke', '2017-04-26 14:43:15'),
(292, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '3176', 'CF', 'MOOSE request failed: rejected [err: requested variable not found [tauuo and maybe others]]', 'failed', 'marke', '2017-04-26 14:43:41'),
(293, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '8631', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 33% complete: block 1: extraction FAILED - requested variable not found [tauuo and maybe others] | task 66% complete: block 2: extraction FAILED - requested variable not found [agessc and maybe others] | task 100% complete: block 3: extraction success - some file(s) already existed | Stream onm failed ---------------- \n\n', 'ending task: extract stream onm', 'marke', '2017-04-26 14:52:13'),
(294, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '8631', 'CQ', 'VALIDATION for stream onm:\nextract failed: no validation performed\n', 'complete / quality issues', 'marke', '2017-04-26 14:53:34'),
(295, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '15274', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction FAILED - task rejected', '', 'marke', '2017-04-26 15:49:18'),
(296, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '15274', 'CF', 'MOOSE request failed: rejected [err: task rejected]', 'failed', 'marke', '2017-04-26 15:49:32'),
(297, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '16742', 'IP', ' | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction FAILED - task rejected', '', 'marke', '2017-04-26 15:52:15'),
(298, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '16742', 'CF', 'MOOSE request failed: rejected [err: task rejected]', 'failed', 'marke', '2017-04-26 15:52:26'),
(299, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '17816', 'IP', ' | Stream Start:  ap8  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap8 completed  ---------------- \n\n | Stream Start:  ap6  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap6 completed  ---------------- \n\n', 'ending task: extract stream ap6', 'marke', '2017-04-26 15:54:08'),
(300, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '17816', 'CS', 'VALIDATION for stream ap8:\nfiles count: mismatch on number of files (expected: 36 ; actual: 37 )\nVALIDATION for stream ap6:\nfiles count: correct number of files ( 36 )\n', 'complete / success', 'marke', '2017-04-26 15:57:24'),
(301, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '21126', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction FAILED - task rejected', '', 'marke', '2017-04-26 16:00:17'),
(302, 10000, 'extract', 'exxar5h1', 'hadmm', '4252', '21126', 'CF', 'MOOSE request failed: rejected [err: task rejected]', 'failed', 'marke', '2017-04-26 16:00:28'),
(303, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '10345', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-27 08:57:45'),
(304, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '10345', 'CS', 'VALIDATION for stream inm:\nstream type is netcdf - no validation performed\n', 'complete / success', 'marke', '2017-04-27 08:58:16'),
(305, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '17121', 'IP', '', 'extract processing started', 'marke', '2017-04-27 09:08:22'),
(306, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '19638', 'IP', '', 'extract processing started', 'marke', '2017-04-27 09:12:16'),
(307, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '20572', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-27 09:14:28'),
(308, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '20572', 'CS', 'VALIDATION for stream inm:\nstream type is netcdf - no validation performed\n', 'complete / success', 'marke', '2017-04-27 09:14:37'),
(309, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '22801', 'IP', '', 'extract processing started', 'marke', '2017-04-27 09:17:57'),
(310, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '25797', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-27 09:22:29'),
(311, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '25797', 'CS', 'VALIDATION for stream inm:\nstream type is netcdf - no validation performed\n', 'complete / success', 'marke', '2017-04-27 09:22:38'),
(312, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '29789', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-27 09:29:25'),
(313, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '29789', 'CS', 'VALIDATION for stream inm:\nstream type is netcdf - no validation performed\n', 'complete / success', 'marke', '2017-04-27 09:29:35'),
(314, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '19292', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-27 15:30:32'),
(315, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '19292', 'CS', 'VALIDATION for stream inm:\nstream type is netcdf - no validation performed\n', 'complete / success', 'marke', '2017-04-27 15:30:42'),
(316, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '24055', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-04-27 15:37:55'),
(317, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '24055', 'CS', 'VALIDATION for stream inm:\nstream type is netcdf - no validation performed\n', 'complete / success', 'marke', '2017-04-27 15:38:04'),
(318, 10000, 'extract', 'eld278', 'hadel', '4119', '15829', 'CF', 'ERROR failed to create data directory\n            root: /data/local10/ar5\n            map: programme|project|model|experiment|realisation\n            name: /data/local10/ar5/CMIP6-TEST/ScenarioMIP/HadGEM3-GC31-LL/ssp245/r1i1p1f1\n            status: failed\n            error: Problem creating subdirectory /data/local10 in directory path /data/local10/ar5/CMIP6-TEST/ScenarioMIP/HadGEM3-GC31-LL/ssp245/r1i1p1f1 [Permission denied - [hadel:users]]\n        ', 'failed', 'marke', '2017-05-02 15:45:55'),
(319, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '7484', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-05-02 15:54:27'),
(320, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '7484', 'CS', 'VALIDATION for stream inm:\nstream type is netcdf - no validation performed\n', 'complete / success', 'marke', '2017-05-02 15:54:37'),
(321, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '16150', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-05-02 16:08:46'),
(322, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '16150', 'CS', 'VALIDATION for stream inm:\nstream type is netcdf - no validation performed\n', 'complete / success', 'marke', '2017-05-02 16:08:56'),
(323, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '19262', 'IP', ' | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n', 'ending task: extract stream inm', 'marke', '2017-05-02 16:13:36'),
(324, 10000, 'extract', 'exxar5h2', 'hadel', '4119', '19262', 'CS', 'VALIDATION for stream inm:\nstream type is netcdf - no validation performed\n', 'complete / success', 'marke', '2017-05-02 16:13:46'),
(325, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '31912', 'IP', ' | Stream Start:  ap6  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap6 completed  ---------------- \n\n | Stream Start:  inm  ---------------- start: 1979-01-01 00:00:00  end: 1980-06-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream inm completed  ---------------- \n\n | Stream Start:  onm  ---------------- start: 1979-01-01 00:00:00  end: 1980-06-01 00:00:00   | task 33% complete: block 1: extraction FAILED - requested variable not found [tauuo and maybe others] | task 66% complete: block 2: extraction FAILED - requested variable not found [agessc and maybe others] | task 100% complete: block 3: extraction FAILED - requested variable not found [tauvo and maybe others] | Stream onm failed ---------------- \n\n | Stream Start:  ap8  ---------------- start: 1979-01-01 00:00:00  end: 1980-06-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap8 completed  ---------------- \n\n', 'ending task: extract stream ap8', 'marke', '2017-05-03 09:42:44'),
(326, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '31912', 'CQ', 'VALIDATION for stream ap6:\nfiles count: correct number of files ( 36 )\nVALIDATION for stream inm:\nstream type is netcdf - no validation performed\nVALIDATION for stream onm:\nextract failed: no validation performed\nVALIDATION for stream ap8:\nfiles count: mismatch on number of files (expected: 51 ; actual: 37 )\n', 'complete / quality issues', 'marke', '2017-05-03 09:48:22'),
(327, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '25550', 'IP', ' | Stream Start:  ap6  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap6 completed  ---------------- \n\n | Stream Start:  ap8  ---------------- start: 1979-01-01 00:00:00  end: 1980-06-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap8 completed  ---------------- \n\n', 'ending task: extract stream ap8', 'marke', '2017-05-03 13:06:53'),
(328, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '25550', 'CS', 'VALIDATION for stream ap6:\nfiles count: correct number of files ( 36 )\nVALIDATION for stream ap8:\nfiles count: mismatch on number of files (expected: 51 ; actual: 37 )\n', 'complete / success', 'marke', '2017-05-03 13:07:23'),
(329, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '32130', 'IP', ' | Stream Start:  ap6  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap6 completed  ---------------- \n\n | Stream Start:  ap8  ---------------- start: 1979-01-01 00:00:00  end: 1980-06-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap8 completed  ---------------- \n\n', 'ending task: extract stream ap8', 'marke', '2017-05-03 13:20:26'),
(330, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '32130', 'CS', 'VALIDATION for stream ap6:\nfiles count: correct number of files ( 36 )\nVALIDATION for stream ap8:\nfiles count: mismatch on number of files (expected: 51 ; actual: 52 )\n', 'complete / success', 'marke', '2017-05-03 13:25:49'),
(331, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '20119', 'IP', ' | Stream Start:  ap6  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap6 completed  ---------------- \n\n | Stream Start:  ap8  ---------------- start: 1979-01-01 00:00:00  end: 1980-06-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap8 completed  ---------------- \n\n', 'ending task: extract stream ap8', 'marke', '2017-05-03 14:04:31'),
(332, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '20119', 'CS', 'VALIDATION for stream ap6:\nfiles count: correct number of files ( 36 )\nVALIDATION for stream ap8:\nfiles count: mismatch on number of files (expected: 51 ; actual: 52 )\n', 'complete / success', 'marke', '2017-05-03 14:08:48'),
(333, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '30905', 'IP', ' | Stream Start:  ap6  ---------------- start: 1979-01-01 00:00:00  end: 1980-01-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap6 completed  ---------------- \n\n | Stream Start:  ap8  ---------------- start: 1980-01-01 00:00:00  end: 1980-06-01 00:00:00   | task 100% complete: block 1: extraction success -  | Stream ap8 completed  ---------------- \n\n', 'ending task: extract stream ap8', 'marke', '2017-05-03 14:28:35'),
(334, 10000, 'extract', 'exxar5h1', 'hadel', '4119', '30905', 'CS', 'VALIDATION for stream ap6:\nfiles count: correct number of files ( 36 )\nVALIDATION for stream ap8:\nfiles count: mismatch on number of files (expected: 15 ; actual: 16 )\n', 'complete / success', 'marke', '2017-05-03 14:30:45');

-- --------------------------------------------------------

--
-- Table structure for table `rt_process`
--

CREATE TABLE IF NOT EXISTS `rt_process` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'process id',
  `requestid` int(11) NOT NULL COMMENT 'request id',
  `process_type` varchar(40) NOT NULL COMMENT 'type of process (system code)',
  `host` varchar(20) NOT NULL COMMENT 'host running process',
  `user` varchar(20) NOT NULL COMMENT 'user owning process',
  `uid` varchar(10) NOT NULL COMMENT 'user id',
  `pid` varchar(10) NOT NULL COMMENT 'process id',
  `upd_by` varchar(20) NOT NULL COMMENT 'person/process responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='describes process';

-- --------------------------------------------------------

--
-- Table structure for table `rt_request`
--

CREATE TABLE IF NOT EXISTS `rt_request` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for request record',
  `projectid` int(11) NOT NULL COMMENT 'id for project this request belongs too',
  `experimentid` int(11) NOT NULL COMMENT 'id for experiment this request belongs too',
  `simulationid` int(11) NOT NULL COMMENT 'id of simulation',
  `name` varchar(60) NOT NULL COMMENT 'name for request - typically set to model_experiment_variant',
  `info` varchar(500) DEFAULT NULL COMMENT 'free text description for request',
  `package` varchar(60) NOT NULL COMMENT 'request name extender to indicate which subset of variables are being produced',
  `request_date` date NOT NULL COMMENT 'date request submitted',
  `input_format` varchar(40) DEFAULT NULL COMMENT 'data type for input (system code)',
  `output_format` varchar(40) DEFAULT NULL COMMENT 'data type for output (system code)',
  `delivery_method` varchar(40) DEFAULT NULL COMMENT 'delivery method (system code)',
  `source_loc` int(11) NOT NULL COMMENT 'id (rt_location) for location of input data',
  `process_loc` int(11) NOT NULL COMMENT 'id (rt_location) for output data',
  `owner_institute` int(11) NOT NULL DEFAULT '1' COMMENT 'institute owning the simulation/data ',
  `upd_by` varchar(20) NOT NULL COMMENT 'user/process responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `o_type` enum('REQUEST') NOT NULL DEFAULT 'REQUEST' COMMENT 'object type',
  `active` tinyint(1) NOT NULL DEFAULT '1' COMMENT 'if 1 the request is active - otherwise not shown in cremadmin',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='manages requests for data dissemination';

--
-- Dumping data for table `rt_request`
--

INSERT INTO `rt_request` (`id`, `projectid`, `experimentid`, `simulationid`, `name`, `info`, `package`, `request_date`, `input_format`, `output_format`, `delivery_method`, `source_loc`, `process_loc`, `owner_institute`, `upd_by`, `upd_date`, `o_type`, `active`) VALUES
(10000, 10012, 10110, 10000, 'HadGEM3-GC31-LL_ssp245_r1i1p1f1', 'request for test 0.2', 'all_vars', '2017-03-16', '', 'nc4', 'MASS', 2, 21, 1, 'admin', '2018-05-23 15:37:27', 'REQUEST', 1);

-- --------------------------------------------------------

--
-- Table structure for table `rt_requestdata`
--

CREATE TABLE IF NOT EXISTS `rt_requestdata` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for requested data record',
  `requestid` int(11) NOT NULL COMMENT 'id for request',
  `simulationid` int(11) NOT NULL COMMENT 'simulation id',
  `runid` int(11) NOT NULL COMMENT 'id for model run that data belongs too',
  `stream` varchar(20) NOT NULL COMMENT 'code for datastream (system codes)',
  `streamtype` varchar(10) NOT NULL COMMENT 'code for data stream type (e.g pp, mocdf, etc.)',
  `streaminit` int(6) NOT NULL DEFAULT '0' COMMENT 'data stream file reinitialisation period in hours',
  `start_date` datetime DEFAULT NULL COMMENT 'start date for data required for output products',
  `end_date` datetime DEFAULT NULL COMMENT 'end_date for data required for output products',
  `extract_order` int(3) DEFAULT NULL COMMENT 'order specified for data extraction if user wishes to specify priority',
  `skip` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'ignore on next extraction if set',
  `upd_by` varchar(20) NOT NULL COMMENT 'person/process responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='input data items associated with a request';

--
-- Dumping data for table `rt_requestdata`
--

INSERT INTO `rt_requestdata` (`id`, `requestid`, `simulationid`, `runid`, `stream`, `streamtype`, `streaminit`, `start_date`, `end_date`, `extract_order`, `skip`, `upd_by`, `upd_date`) VALUES
(10322, 10000, 10000, 10001, 'ap8', 'pp', 0, '1980-01-01 00:00:00', '1980-06-01 00:00:00', 4, 0, 'admin', '2017-05-03 14:27:46'),
(10002, 10000, 10000, 10001, 'onm', 'nc', 0, NULL, NULL, 3, 1, 'admin', '2017-05-03 12:34:31'),
(10323, 10000, 10000, 10001, 'ap6', 'pp', 0, NULL, '1980-01-01 00:00:00', 1, 0, 'admin', '2017-05-03 14:03:34'),
(10324, 10000, 10000, 10001, 'inm', 'nc', 0, NULL, NULL, 2, 1, 'admin', '2017-05-03 14:07:12');

-- --------------------------------------------------------

--
-- Table structure for table `rt_status`
--

CREATE TABLE IF NOT EXISTS `rt_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for status record',
  `requestid` int(11) NOT NULL COMMENT 'id for request that these status records relate to',
  `process_type` varchar(40) NOT NULL COMMENT 'process type (system code)',
  `status_value` varchar(40) DEFAULT NULL COMMENT 'status value (e.g. not started) - system codes',
  `status_info` varchar(500) NOT NULL COMMENT 'user comment on status change',
  `upd_by` varchar(20) NOT NULL COMMENT 'person/process responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='describes status of request';

--
-- Dumping data for table `rt_status`
--

INSERT INTO `rt_status` (`id`, `requestid`, `process_type`, `status_value`, `status_info`, `upd_by`, `upd_date`) VALUES
(10317, 10000, 'extract', 'CS', 'cdds_extract.py', 'marke', '2017-05-03 14:30:45');

-- --------------------------------------------------------

--
-- Table structure for table `ut_comments`
--

CREATE TABLE IF NOT EXISTS `ut_comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for comment',
  `o_id` int(11) NOT NULL COMMENT 'id for object in object table',
  `o_type` enum('TICKET','COUPLEDMODEL','SIMULATION','REQUEST') CHARACTER SET utf8 NOT NULL COMMENT 'object type label',
  `subject` varchar(100) CHARACTER SET utf8 NOT NULL COMMENT 'subject',
  `info` text CHARACTER SET utf8 NOT NULL COMMENT 'comment text (can be html)',
  `author` int(11) NOT NULL COMMENT 'id for person making comment',
  `upd_by` char(20) CHARACTER SET utf8 NOT NULL COMMENT 'person/process responsible fro last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci COMMENT='manages content of comments';

--
-- Dumping data for table `ut_comments`
--

INSERT INTO `ut_comments` (`id`, `o_id`, `o_type`, `subject`, `info`, `author`, `upd_by`, `upd_date`) VALUES
(9, 6, 'TICKET', 'Just a note', 'to say we don\'t give a damn', 63, 'admin', '2017-01-04 13:13:06'),
(10, 10000, 'REQUEST', 'a test comment', 'What am I talking baout', 63, 'admin', '2017-02-21 17:05:56');

-- --------------------------------------------------------

--
-- Table structure for table `ut_commontxt`
--

CREATE TABLE IF NOT EXISTS `ut_commontxt` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `category` enum('data_access','data_license') NOT NULL COMMENT 'content category',
  `label` varchar(20) NOT NULL COMMENT 'label used in user interface',
  `description` varchar(100) NOT NULL COMMENT 'short description of content',
  `content` text NOT NULL COMMENT 'text content',
  `upd_by` varchar(20) NOT NULL COMMENT 'user responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `ut_commontxt`
--

INSERT INTO `ut_commontxt` (`id`, `category`, `label`, `description`, `content`, `upd_by`, `upd_date`) VALUES
(1, 'data_access', 'Met Office - CMIP6', 'Standard Met Office data access agreement text.', 'placeholder text', 'marke', '2016-02-10 12:17:26'),
(2, 'data_license', 'Met Office - CMIP6', 'Standard Met Office data license agreement text.', 'Placeholder text', 'marke', '2016-02-10 12:17:26');

-- --------------------------------------------------------

--
-- Table structure for table `ut_contactrole`
--

CREATE TABLE IF NOT EXISTS `ut_contactrole` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'primary key',
  `o_id` int(11) NOT NULL COMMENT 'id of object for this contact',
  `o_type` varchar(30) NOT NULL COMMENT 'object type for this contact',
  `personid` int(11) DEFAULT NULL COMMENT 'id of person record (must be provided if instituteid is null)',
  `instituteid` int(11) DEFAULT NULL COMMENT 'id of institute record (must be provided if personid is null)',
  `role` varchar(30) NOT NULL COMMENT 'role for this contact in the context of the referenced object',
  `display` varchar(500) NOT NULL COMMENT 'text display field with role + summary contact details',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` varchar(20) NOT NULL COMMENT 'person responsible for last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Stores role of contact';

--
-- Dumping data for table `ut_contactrole`
--

INSERT INTO `ut_contactrole` (`id`, `o_id`, `o_type`, `personid`, `instituteid`, `role`, `display`, `upd_date`, `upd_by`) VALUES
(10001, 10002, 'MODEL', 10001, NULL, 'point of contact', '1', '2017-03-22 11:56:01', 'pamv'),
(10002, 10001, 'MODEL', 10002, NULL, 'point of contact', '1', '2017-03-22 12:11:56', 'pamv'),
(10003, 10000, 'PROGRAMME', 1, 1, 'principal investigator', '2', '2017-05-23 13:56:28', 'admin'),
(10004, 10000, 'PROGRAMME', 45, 1, 'author', '3', '2017-05-23 13:56:28', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `ut_institute`
--

CREATE TABLE IF NOT EXISTS `ut_institute` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'institute id',
  `sname` char(20) NOT NULL COMMENT 'institute acronym',
  `name` varchar(100) NOT NULL COMMENT 'full name',
  `address` varchar(200) DEFAULT NULL,
  `city` varchar(60) DEFAULT NULL,
  `adminarea` varchar(60) DEFAULT NULL COMMENT 'e.g. county, state, etc.',
  `postcode` char(12) DEFAULT NULL,
  `country` varchar(60) NOT NULL,
  `weblink` varchar(150) DEFAULT NULL COMMENT 'URL to institute homepage',
  `cim_id` varchar(150) DEFAULT NULL COMMENT 'cim document identifier for institute',
  `upd_by` char(20) NOT NULL COMMENT 'person responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='manages information on an organisation';

--
-- Dumping data for table `ut_institute`
--

INSERT INTO `ut_institute` (`id`, `sname`, `name`, `address`, `city`, `adminarea`, `postcode`, `country`, `weblink`, `cim_id`, `upd_by`, `upd_date`) VALUES
(1, 'MOHC', 'Met Office Hadley Centre', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'http://www.metoffice.gov.uk', '12345678', 'admin', '2017-01-04 16:12:57'),
(2, 'BADC', 'British Atmospheric Data Centre', 'Space Science and Technology Dept., R25 - Room 2.122, STFC Rutherford Appleton Laboratory', 'Chilton, Nr Didcot', 'Oxfordshire', 'OX11 0QX', 'UK', 'http://www.badc.rl.ac.uk', NULL, 'marke', '2015-06-23 13:04:54'),
(4, 'WDCC', 'World Data Center for Climate', 'Max-Planck-Institute for Meteorology/M&D\r\nBundesstrasse 53', 'Hamburg', '', 'D-20146', 'Germany', 'http://www.mad.zmaw.de/wdc-for-climate/', NULL, 'marke', '2009-03-09 11:38:00'),
(5, 'DLR', 'Deutsches Zentrum für Luft- und Raumfahrt', '', 'Oberpfaffenhofen', '82234 Wessling', '', 'Germany', 'http://www.dlr.de', NULL, 'pamv', '2016-03-01 14:06:05'),
(6, 'NCAR', 'National Center for Atmsopheric Research', 'P.O. Box 3000 Boulder', 'Boulder', 'CO 80307', '', 'USA', 'https://ncar.ucar.edu/', NULL, 'pamv', '2016-03-01 15:10:00'),
(7, 'LSCE', 'Laboratoire de Sciences du Climat et de l\'Environnement', 'Bât. 12, avenue de la Terrasse', 'F-91198 GIF-SUR-YVETTE CEDEX', '', '', 'France', 'http://www.lsce.ipsl.fr', NULL, 'pamv', '2016-03-02 08:06:06'),
(8, 'CCCma', 'Canadian Centre for Climate Modelling and Analysis', '', '', '', '', 'Canada', 'http://www.uvic.ca/ccma/', NULL, 'pamv', '2016-03-23 14:54:18'),
(9, 'KNMI', 'Royal Netherlands Meteorological Institute', 'PO Box 201', '', '', 'NL-3730 AE D', 'Netherlands', 'http://knmi.nl/home', NULL, 'pamv', '2016-03-02 09:05:40'),
(10, 'CIRES', 'Cooperative Institute for Research In Environmental Sciences', 'University of Colorado Boulder, 216 UCB', ' Boulder', '', 'CO 80309-021', 'USA', '', NULL, 'pamv', '2016-03-02 09:16:19'),
(11, 'UMD', 'University of Maryland', '', '', '', '', '', '', NULL, 'pamv', '2016-03-02 09:44:48'),
(12, 'PNNL', 'Pacific Northwest National Laboratory', '', '', '', '', '', 'http://www.pnnl.gov/', NULL, 'pamv', '2016-03-02 11:04:29'),
(10000, 'UoR', 'University of Reading', 'Department of Meteorology Earley Gate PO Box 243', 'Reading', 'Berks', 'RG6 6BB', 'UK', '', NULL, 'pamv', '2017-03-22 12:04:24');

-- --------------------------------------------------------

--
-- Table structure for table `ut_locations`
--

CREATE TABLE IF NOT EXISTS `ut_locations` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for disk location',
  `name` varchar(40) CHARACTER SET utf8 NOT NULL COMMENT 'name ',
  `location` varchar(300) CHARACTER SET utf8 NOT NULL COMMENT 'location pathname',
  `loctype` varchar(20) CHARACTER SET utf8 NOT NULL COMMENT 'local for location connected to DDS computer server, network for location accessible via network',
  `source` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'true if this can be used as extraction source',
  `process` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'true if this can be used as processing area',
  `processhost` varchar(40) CHARACTER SET utf8 DEFAULT NULL COMMENT 'preferred host for software processes - only needed for ''local'' locations',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `upd_by` varchar(20) CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci COMMENT='Contains a list of short names for network locations used in';

--
-- Dumping data for table `ut_locations`
--

INSERT INTO `ut_locations` (`id`, `name`, `location`, `loctype`, `source`, `process`, `processhost`, `upd_date`, `upd_by`) VALUES
(2, 'MASS-R', 'moose:/crum/', 'network', 1, 0, '', '2012-01-23 15:39:49', 'marke'),
(15, 'Stager_cmip5', '10.169.200.100:/badcstager/badc1/staging_area/mohc1/cmip5', 'network', 0, 0, '', '2012-01-23 15:39:49', 'paulw'),
(5, 'AR5_SERVER_0', '/data/local/ar5', 'local', 0, 1, '617', '2012-01-25 10:24:37', 'paulw'),
(6, 'AR5_SERVER_2', '/data/local2/ar5', 'local', 0, 1, '617', '2012-01-25 10:22:36', 'paulw'),
(16, 'AR5_SERVER_1', '/data/local1/ar5', 'local', 0, 1, '617', '2012-01-25 10:24:37', 'paulw'),
(17, 'AR5_SERVER_3', '/data/local3/ar5', 'local', 0, 1, '617', '2012-01-25 10:24:37', 'paulw'),
(18, 'AR5_SERVER_4', '/data/local4/ar5', 'local', 0, 1, '617', '2012-01-25 10:24:37', 'paulw'),
(21, 'AR5_SERVER_10', '/data/local10/ar5', 'local', 0, 1, '616', '2012-01-25 10:22:08', 'paulw'),
(22, 'AR5_SERVER_11', '/data/local11/ar5', 'local', 0, 1, '616', '2012-01-25 10:22:08', 'paulw'),
(23, 'AR5_SERVER_12', '/data/local12/ar5', 'local', 0, 1, '616', '2012-01-25 10:22:08', 'paulw');

-- --------------------------------------------------------

--
-- Table structure for table `ut_person`
--

CREATE TABLE IF NOT EXISTS `ut_person` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for person',
  `title` char(10) DEFAULT NULL COMMENT 'personal title (e.g. Dr, Prof)',
  `firstname` varchar(30) DEFAULT NULL,
  `familyname` varchar(40) NOT NULL,
  `institute` int(11) NOT NULL COMMENT 'id of institute that this person is associated with',
  `position` varchar(80) DEFAULT NULL COMMENT 'job title/position',
  `phone` varchar(20) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `city` varchar(60) DEFAULT NULL,
  `adminarea` varchar(60) DEFAULT NULL COMMENT 'e.g. county, state, etc.',
  `postcode` char(10) DEFAULT NULL,
  `country` varchar(60) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `weblink` varchar(150) DEFAULT NULL COMMENT 'personal web link',
  `permanent_id` varchar(150) DEFAULT NULL COMMENT 'external identifier for person (e.g. ORCID)',
  `cim_id` varchar(150) DEFAULT NULL COMMENT 'cim document identifier for person',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` char(20) NOT NULL COMMENT 'person responsible for last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='manages information on an individual';

--
-- Dumping data for table `ut_person`
--

INSERT INTO `ut_person` (`id`, `title`, `firstname`, `familyname`, `institute`, `position`, `phone`, `address`, `city`, `adminarea`, `postcode`, `country`, `email`, `weblink`, `permanent_id`, `cim_id`, `upd_date`, `upd_by`) VALUES
(1, 'Dr', 'Mark', 'Elkington', 1, 'Climate Data Analyst', '01392 884835', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'mark.elkington@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, '987654321', '2017-01-05 12:01:05', 'marke'),
(5, 'Mr', 'John', 'King', 1, 'IT Support', '01392 884479', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'john.king@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(7, 'Dr', 'Tim', 'Johns', 1, 'Manager Global Coupled Modelling', '01392 886901', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'tim.johns@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(8, 'Mr', 'Ag', 'Stephens (STFC)', 2, 'Met. Office Liaison', '07704 869343', 'Space Science and Technology Dept., R25 - Room 2.122, STFC Rutherford Appleton Laboratory', 'Chilton, Nr Didcot', 'Oxfordshire', 'OX11 0QX', 'UK', 'ag.stephens@stfc.ac.uk', 'http://www.badc.rl.ac.uk', NULL, NULL, '2015-06-23 14:57:08', 'philb'),
(9, 'Dr', 'Kevin', 'Marsh', 2, '', '+44 (0) 1235 446521', 'Space Science and Technology Dept., R25 - Room 2.122, STFC Rutherford Appleton Laboratory', 'Chilton, Nr Didcot', 'Oxfordshire', 'OX11 0QX', 'UK', 'kevin.marsh@stfc.ac.uk', 'http://www.badc.rl.ac.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(10, 'Dr', 'Jamie', 'Kettleborough', 1, 'Data Applications Manager', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX3', 'UK', 'jamie.kettleborough@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(11, 'Dr', 'Ben', 'Booth', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', '', 'UK', 'ben.booth@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(13, 'Ms', 'Silke', 'Schubert', 4, 'ENSEMBLES Project', '+49 (40) 41173 125', 'Max-Planck-Institute for Meteorology/M&D\r\nBundesstrasse 53', 'Hamburg', '', 'D-20146', 'Germany', 'silke.schubert@zmaw.de', 'http://http://www.mad.zmaw.de/wdc-for-climate/', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(14, 'Dr', 'Phil', 'Bentley', 1, '', '01392 884105', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'philip.bentley@metoffice.gov.uk ', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(17, 'Dr', 'Chris', 'Jones', 1, 'Manager, Terrestrial Carbon Cycle ', '01392 884514 ', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'chris.d.jones@metoffice.gov.uk', 'http://http://www.metoffice.gov.uk/research/our-scientists/climate-chemistry-ecosystems/chris-jones', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(18, 'Dr', 'Mike ', 'Sanderson', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'michael.sanderson@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(19, 'Dr', 'Jonny', 'Williams', 1, 'Climate Model Development and Evaluation Scientist ', '01392 884814', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'jonny.williams@metoffice.gov.uk ', 'http://http://www-hc/~hadjw/home.html ', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(22, 'Dr', 'Bill', 'Collins', 1, 'Manager Atmospheric Composition and Climate', '01392 884634', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'bill.collins@metoffice.gov.uk', 'http://http://www-hc/~hadwc/home.html', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(23, 'Dr', 'Gareth', 'Jones', 1, 'Climate change detection', '01392 884835', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'gareth.s.jones@metoffice.gov.uk', 'http://http://www-hc/~hadgk/home.html', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(24, 'Dr', 'Nikos', 'Christidis', 1, 'Climate Research Scientist', '01392 884067 ', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'nikos.christidis@metoffice.gov.uk', 'http://http://www-hc/~hadnc/home.html', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(25, 'Dr', 'Mark', 'Webb', 1, '', '01392 884515 ', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', ' mark.webb@metoffice.gov.uk', 'http://http://www-hc/~hadmw/home.html', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(26, 'Dr', 'Keith', 'Williams', 1, '', '01392 885681 ', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'keith.williams@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(27, 'Dr', 'Nicolas', 'Bellouin', 1, 'Climate Research Scientist ', '01392 884684', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'nicolas.bellouin@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(28, 'Dr', 'Marie', 'Doutriaux-Boucher  ', 1, 'Senior HadGEM2 Climate Feedback Scientist', '01392 886041', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'marie.doutriaux-boucher@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(29, 'Dr', 'Fiona', 'O\'Connor', 1, 'Atmospheric Chemistry Modeller ', '01392 884296', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', ' fiona.oconnor@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(30, 'Dr', 'Jeff', 'Ridley', 1, 'Climate Research Scientist ', '01392 886472', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'jeff.ridley@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(32, 'Dr', 'Ian', 'Totterdell', 1, 'Ocean Scientist (Ocean Carbon Cycle) ', '01392 884264', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'ian.totterdell@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(33, 'Dr', 'Alison', 'McLaren', 1, 'Sea Ice Scientist ', '01392 884242', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'alison.mclaren@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(34, 'Dr', 'Helene', 'Hewitt', 1, 'Manager, Ocean and Sea Ice Modelling', '01392 884956', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'helene.hewitt@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(35, 'Dr', 'Jonathan', 'Gregory', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', '', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(36, 'Dr', 'Spencer', 'Liddicoat', 1, 'Scientist, Terrestrial Carbon Cycle Group', '01392 884884', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'spencer.liddicoat@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(37, 'Dr', 'Yoko', 'Tsushima', 1, 'Climate Scientist', '01392 885258', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'yoko.tsushima@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(38, 'Dr', 'Alejandro', 'Bodas-Salcedo', 1, '', '01392 886113', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'alejandro.bodas@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(39, 'Dr', 'Holger', 'Pohlmann', 1, 'Climate Scientist', '01392 884863', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'holger.pohlmann@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(40, 'Dr', 'William', 'Ingram', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', '', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'philb'),
(41, '', 'Jose', 'Rodríguez ', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', '', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(42, '', '', 'guestuser', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', '', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(43, 'Dr', 'Ag', 'Stephens', 1, 'BADC - Met Office Coordinator', '01392 884263', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'ag.stephens@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(44, 'Dr', 'Robin', 'Clark', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'robin.clark@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(45, 'Dr', 'Alistair', 'Sellar', 1, 'Manager, Ocean Assessment and Transitions', '01392 886392', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'alistair.sellar@metoffice.gov.uk', 'http://http://www-hc/~hadtq/home.html', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(46, 'Dr', 'Fraser', 'Lott', 1, 'Climate Monitoring and Attribution Scientist', '01392 885293', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'fraser.lott@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(47, 'Dr', 'Gill', 'Martin', 1, 'Manager of Global Water Cycle group', '01392 886893', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'gill.martin@metoffice.gov.uk', 'http://http://www-hc/~hadgi/home.html', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(48, 'Dr', 'Andrew', 'Wiltshire', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'andrew.wiltshire@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(49, '', 'Ruth', 'McDonald', 1, 'Research Scientist', '01392 886947 ', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'ruth.mcdonald@metoffice.gov.uk', 'http://http://www-hc/~hadcr/home.html', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(50, '', 'Nicola', 'Gedney', 1, 'Land-surface Processes', '01491 692530', '', 'Wallingford', 'Oxon', '', 'UK', 'nicola.gedney@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(51, 'Dr', 'Paul ', 'Halloran', 1, 'Ocean Biogeochemistry Research Scientist', '+44 (0)1392 884809', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'paul.halloran@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(52, 'Dr', 'Andy', 'Jones', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', '', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'spencer.liddicoat'),
(53, 'Dr', 'Steven', 'Hardiman', 1, 'Stratospheric Research Scientist', '01392 885982', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'steven.hardiman@metoffice.gov.uk', 'http://http://www-hc/~hadvh/home.html', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(54, 'Dr', 'Stephanie', 'Woodward', 1, 'Research Scientist - Climate Chemistry and Ecosystems', '01392 884519', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'stephanie.woodward@metoffice.go.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(55, 'Dr', 'Steve', 'Mullerworth', 1, 'FLUME Manager', '01392 886899 ', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'steve.mullerworth@metoffice.gov.uk', 'http://http://www-hc/~hadsm/home.html', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(56, 'Dr', 'Doug', 'Smith', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'doug.smith@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'philb'),
(57, '', 'Rosie', 'Eade', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'rosie.eade@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'philb'),
(58, 'Dr', 'Chris', 'Harris', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', '', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'spencer.liddicoat'),
(59, 'Dr', 'Tim', 'Graham', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', '', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'spencer.liddicoat'),
(60, 'Dr', 'Anne', 'Pardaens', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', '', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'spencer.liddicoat'),
(61, 'Dr', 'Erasmo', 'Buonomo', 1, 'Regional Climate Modeller', '(0)1392 886192', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'erasmo.buonomo@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(62, 'Dr', 'David', 'Hein', 1, 'Regional Modelling & PRECIS technical coordinator', '(0)1392 884089', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'david.hein@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(63, 'Dr', 'Tim', 'Andrews', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'tim.andrews@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 16:15:13', ''),
(64, 'Dr', 'Ron', 'Kahana', 1, 'Climate Impacts Scientist', '01392 884706', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'ron.kahana@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(65, '', 'Simon', 'Tucker', 1, '', '01392 884855', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'simon.tucker@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(66, 'Dr', 'Chaline', 'Marzin', 1, 'Unified Model Collaboration', '01392 885199', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'charline.marzin@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(67, '', 'Gillian', 'Kay', 1, '', '01392 886888', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'gillian.kay@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(68, 'Dr', 'Carol', 'McSweeney', 1, 'Regional Climate Scientist', '01392 885230', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'carol.mcsweeney@metoffice.gov.uk', 'http://http://www-hc/~hadcy/', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(69, 'Dr', 'Changgui', 'Wang', 1, 'PRECIS System Manager', '0118 378 5580', 'Room 2L60, Dept of Meteorology, PO BOX 243, University of Reading', 'Reading', 'Berkshire', 'RG6 6BB', 'UK', 'chang.wang@metoffice.gov.uk', 'http://http://www-rdg/~apgw/', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(70, 'Dr', 'Peter', 'Stott', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'peter.stott@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(71, 'Dr', 'Malcolm', 'Roberts', 1, 'Manager, High resolution global climate modelling', '01392 884537', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'malcolm.roberts@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(72, '', 'Bill', 'Roseblade', 1, 'UM support and development', '01392 884945', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'william.roseblade@metoffice.gov.uk', 'http://http://www-hc/~hadwr/home.html', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(73, 'Dr', 'Eddy', 'Robertson', 1, 'Carbon Cycle Research Scientist', '+44 (0)1392 884803', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'eddy.robertson@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(74, 'Dr', 'Pam', 'Vass', 1, 'Climate Data Analyst', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'pam.vass@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(75, 'Dr', 'Richard', 'Jones', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', '', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(76, '', 'Wilfran', 'Moufouma-Okia', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', '', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(77, 'Dr', 'Carlo', 'Buontempo', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'carlo.buontempo@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(78, 'Dr', 'Karina', 'Williams', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'karina.williams@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(79, 'Dr', 'David', 'Sexton', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'david.sexton@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(80, '', 'Camilla', 'Mathison', 1, '', '01392 886695', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'camilla.mathison@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(81, 'Dr', 'Jeff', 'Knight', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', '', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(82, 'Dr', 'Adam', 'Scaife', 1, '', '01392 884056', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'adam.scaife@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(83, 'Dr', 'David', 'Bentley', 1, 'Climate Consultant', '+44 (0)1392 885237', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'david.bentley@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(84, '', 'Chloe', 'Eagle', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', '', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'hadwr'),
(85, '', 'Grace', 'Redmond', 1, '', '(0)1392 884110', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'grace.redmond@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(87, '', 'Andrew', 'Ciavarella', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'andrew.ciavarella@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(88, '', 'Irina', 'Linova-Pavlova', 1, '', '', 'Fitzroy Road', 'Exeter', 'Devon', 'EX1 3PB', 'UK', 'irina.linova-pavlova@metoffice.gov.uk', 'http://www.metoffice.gov.uk', NULL, NULL, '2015-06-23 14:57:08', 'marke'),
(89, 'Dr', 'Yongming', 'Tang', 1, '', '', '', '', '', '', '', 'yongming.tang@metoffice.gov.uk', '', NULL, NULL, '2016-03-01 12:41:13', 'pamv'),
(90, 'Dr', 'Veronika', 'Eyring', 5, 'Senior Scientist and Head of Earth System Model Evaluation Group', '+49-8153-28-2533', 'Institut für Physik der Atmosphäre (IPA)', 'Oberpfaffenhofen', '82234 Wessling', '', 'Germany', 'veronika.eyring@dlr.de', 'http://www.pa.op.dlr.de/~VeronikaEyring/', NULL, NULL, '2016-03-01 14:09:39', 'pamv'),
(91, 'Professor', 'Jason', 'Lowe', 1, 'Head of Mitigation Advice', '', 'MOHC', '', '', '', '', '', '', NULL, NULL, '2016-03-01 14:59:32', 'pamv'),
(92, 'Dr', 'Brian', 'O\'Neill', 6, 'Leader of Integrated Assessment Modeling (IAM) group ', '303-497-8118', 'Integrated Assessment Modeling, Climate and Global Dynamics Laboratory', 'Boulder', 'CO 80307', '', 'USA', 'boneill@ucar.edu', 'http://staff.ucar.edu/users/boneill', NULL, NULL, '2016-03-01 15:14:52', 'pamv'),
(93, 'Professor', 'Pierre', 'Friedlingstein', 7, '', '', '', '', '', '', '', 'P.Friedlingstein@exeter.ac.uk', '', NULL, NULL, '2016-03-02 08:13:57', 'pamv'),
(94, 'Dr', 'Nathan', 'Gillett', 8, 'Research Scientist', '', 'School of Earth and Ocean Sciences, University of Victoria', '', '', '', '', 'nathan.gillett@ec.gc.ca', 'http://www.ec.gc.ca/scitech/default.asp?lang=En&n=F97AE834-1&xsl=scitechprofile&xml=F97AE834-A762-47A6-A2D9-9C397FD72F37&formid=9AB46F0E-0597-46B4-B01', NULL, NULL, '2016-03-02 08:30:51', 'pamv'),
(95, '', 'Rein', 'Haarsma', 9, 'Research Scientist', '', '', '', '', '', '', 'rein.haarsma@knmi.nl', 'https://www.knmi.nl/over-het-knmi/onze-mensen/rein-haarsma', NULL, NULL, '2016-03-02 09:09:25', 'pamv'),
(96, 'Dr', 'Robert', 'Pincus', 10, ' Image of Robert Pincus Forecast and Modeling Development Team', '(303) 497-6310', 'NOAA/ESRL Physical Sciences Division, R/PSD1 325 Broadway', 'Boulder', '', 'CO 80305', 'USA', 'robert.pincus@colorado.edu', 'http://www.esrl.noaa.gov/psd/people/robert.pincus/', NULL, NULL, '2016-03-02 09:20:00', 'pamv'),
(97, 'Professor', 'George', 'Hurttt', 11, 'Research Director', '(301) 405-8541', 'Department of Geographical Sciences, University of Maryland, 2181 Samuel J. LeFrak Hall, 7251 Preinkert Drive, College Park, ', '', '', 'MD 20742', 'USA', 'gchurtt@umd.edu', 'http://geog.umd.edu/facultyprofile/Hurtt/George', NULL, NULL, '2016-03-02 09:48:19', 'pamv'),
(98, 'Professor', 'Jim', 'Haywood', 1, 'Research Fellow', '01392 725279', '', '', '', '', '', 'J.M.Haywood@exeter.ac.uk', 'http://emps.exeter.ac.uk/mathematics/staff/jmh232', NULL, NULL, '2016-03-02 11:00:06', 'pamv'),
(99, 'Dr', 'Ben', 'Kravitz', 12, 'Earth Systems Analysis & Modeling Scientist', '', 'Pacific Northwest National Laboratory PO Box 999 MSIN: K9-24', 'Richland', '', 'WA 99352', 'USA', 'ben.kravitz@pnnl.gov', 'http://www.pnnl.gov/atmospheric/staff/staff_info.asp?staff_num=7886', NULL, NULL, '2016-03-02 11:09:49', 'pamv'),
(10000, '', 'Daley', 'Calvert', 1, '', '', '', '', '', '', '', 'daley.calvert@metoffice.gov.uk', '', NULL, NULL, '2017-02-06 16:49:33', 'pamv'),
(10001, 'Dr', 'David', 'Storkey', 1, '', '', '', '', '', '', '', 'dave.storkey@metoffice.gov.uk', '', NULL, NULL, '2017-03-22 11:50:29', 'pamv'),
(10002, 'Dr', 'Till', 'Kuhlbrodt', 10000, 'Senior Research Fellow', '+44 (0) 118 378 5100', 'Department of Meteorology Earley Gate PO Box 243', 'Reading', 'Berks', 'RG6 6BB', 'UK', 't.kuhlbrodt@reading.ac.uk', 'http://www.met.reading.ac.uk/userpages/till.php', NULL, NULL, '2017-03-22 12:10:59', 'pamv');

-- --------------------------------------------------------

--
-- Table structure for table `ut_quality`
--

CREATE TABLE IF NOT EXISTS `ut_quality` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for quality record',
  `o_id` int(11) NOT NULL COMMENT 'id of entity that quality record relates to',
  `o_type` enum('REQUEST','RUN','SIMULATION') CHARACTER SET utf8 NOT NULL COMMENT 'type of entity that quality report relates to',
  `o_name` varchar(60) CHARACTER SET utf8 NOT NULL COMMENT 'name of entity that quality record relates to',
  `status` varchar(40) CHARACTER SET utf8 NOT NULL COMMENT 'current status of quality issue (system codes)',
  `issue_type` varchar(40) CHARACTER SET utf8 NOT NULL COMMENT 'type of issue (system codes)',
  `severity` varchar(40) CHARACTER SET utf8 NOT NULL COMMENT 'severity of quality issue (system codes)',
  `date_found` date NOT NULL COMMENT 'date issue reported',
  `person_found` int(11) NOT NULL COMMENT 'person who reported issue',
  `info_issue` text CHARACTER SET utf8 NOT NULL COMMENT 'description of issue',
  `weblink_issue` varchar(150) CHARACTER SET utf8 DEFAULT NULL COMMENT 'link to additional information on the issue',
  `date_resolved` date DEFAULT NULL COMMENT 'date issue resolved',
  `person_resolved` int(11) DEFAULT NULL COMMENT 'person who reported the resolution',
  `info_resolved` text CHARACTER SET utf8 COMMENT 'description of issue resolution',
  `weblink_resolved` varchar(150) CHARACTER SET utf8 DEFAULT NULL COMMENT 'link to additional information on the issue resolution',
  `deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'flag set if quality record has been deleted',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` varchar(20) CHARACTER SET utf8 NOT NULL COMMENT 'person/process responsible for last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci COMMENT='describes quality record';

-- --------------------------------------------------------

--
-- Table structure for table `ut_qualitydetail`
--

CREATE TABLE IF NOT EXISTS `ut_qualitydetail` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for quality detail',
  `qualityid` int(11) NOT NULL COMMENT 'owning quality record id',
  `parameter` varchar(60) NOT NULL COMMENT 'parameter name',
  `value` varchar(60) NOT NULL COMMENT 'value for parameter',
  `issue` varchar(500) NOT NULL COMMENT 'issue/state relating to parameter',
  `info` text COMMENT 'additional information',
  `weblink` varchar(200) DEFAULT NULL COMMENT 'link to additional information',
  `upd_by` varchar(20) NOT NULL COMMENT 'person/process responsible for last update',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='maintains records for measurable quality parameters';

-- --------------------------------------------------------

--
-- Table structure for table `ut_reference`
--

CREATE TABLE IF NOT EXISTS `ut_reference` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for reference',
  `authors` varchar(500) NOT NULL COMMENT 'author list e.g. Bloggs, J.R, M.D.Elkington',
  `date` char(4) NOT NULL COMMENT 'publication date (year)',
  `title` varchar(200) NOT NULL COMMENT 'title of reference',
  `detail` varchar(200) NOT NULL COMMENT 'publication details for reference',
  `doi` varchar(45) DEFAULT NULL COMMENT 'DOI reference',
  `abstract` text COMMENT 'document abstract',
  `weblink` varchar(150) DEFAULT NULL COMMENT 'link to online copy of reference',
  `format` varchar(45) DEFAULT NULL COMMENT 'format (system code)',
  `reference` text COMMENT 'complete reference (authors+title+detail)',
  `cim_id` varchar(150) DEFAULT NULL COMMENT 'cim document identifier',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` char(20) NOT NULL COMMENT 'person/process responsible for last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='scientific references';

--
-- Dumping data for table `ut_reference`
--

INSERT INTO `ut_reference` (`id`, `authors`, `date`, `title`, `detail`, `doi`, `abstract`, `weblink`, `format`, `reference`, `cim_id`, `upd_date`, `upd_by`) VALUES
(5, 'Collins W.J. , N. Bellouin, M. Doutriaux-Boucher, N. Gedney, T. Hinton, C.D. Jones, S. Liddicoat, G. Martin, F. O\'Connor, J. Rae, C. Senior, I. Totterdell, and S. Woodward', '2008', 'Evaluation of the HadGEM2 model.', 'Meteorological Office Hadley Centre, Technical Note 74,', '', '', 'http://www.metoffice.gov.uk/publications/HCTN/HCTN_74.pdf', 'documentDigital', 'Collins W.J. , N. Bellouin, M. Doutriaux-Boucher, N. Gedney, T. Hinton, C.D. Jones, S. Liddicoat, G. Martin, F. O\'Connor, J. Rae, C. Senior, I. Totterdell, and S. Woodward (2008) Evaluation of the HadGEM2 model.. Meteorological Office Hadley Centre, Technical Note 74,', '', '0000-00-00 00:00:00', 'marke'),
(6, 'Bellouin N., O. Boucher, J. Haywood, C. Johnson, A. Jones, J. Rae, and S. Woodward.', '2007', 'Improved representation of aerosols for HadGEM2.', 'Meteorological Office Hadley Centre, Technical Note 73, March 2007', '', '', 'http://www.metoffice.gov.uk/publications/HCTN/HCTN_73.pdf', 'documentDigital', 'Bellouin N., O. Boucher, J. Haywood, C. Johnson, A. Jones, J. Rae, and S. Woodward. (2007) Improved representation of aerosols for HadGEM2.. Meteorological Office Hadley Centre, Technical Note 73, March 2007', '', '0000-00-00 00:00:00', 'marke'),
(7, 'Johns T.C., C.F. Durman, H.T. Banks, M.J. Roberts, A.J. McLaren, J.K. Ridley, C.A. Senior, K.D. Williams, A. Jones, G.J. Rickard, S. Cusack, W.J. Ingram, M. Crucifix, D.M.H. Sexton, M.M. Joshi, B-W. Dong, H. Spencer, R.S.R. Hill, J.M. Gregory, A.B. Keen, A.K. Pardaens, J.A. Lowe, A. Bodas-Salcedo, S', '2006', 'The new Hadley Centre climate model HadGEM1: Evaluation of coupled simulations.', 'Journal of Climate, American Meteorological Society, Vol. 19, No. 7, pages 1327-1353.', '', '', '', 'documentHardcopy', 'Johns T.C., C.F. Durman, H.T. Banks, M.J. Roberts, A.J. McLaren, J.K. Ridley, C.A. Senior, K.D. Williams, A. Jones, G.J. Rickard, S. Cusack, W.J. Ingram, M. Crucifix, D.M.H. Sexton, M.M. Joshi, B-W. Dong, H. Spencer, R.S.R. Hill, J.M. Gregory, A.B. Keen, A.K. Pardaens, J.A. Lowe, A. Bodas-Salcedo, S (2006) The new Hadley Centre climate model HadGEM1: Evaluation of coupled simulations.. Journal of Climate, American Meteorological Society, Vol. 19, No. 7, pages 1327-1353.', '', '0000-00-00 00:00:00', 'marke'),
(8, 'Martin G.M., M.A. Ringer, V.D. Pope, A. Jones, C. Dearden and T.J. Hinton', '2006', 'The physical properties of the atmosphere in the new Hadley Centre Global Environmental Model, HadGEM1 - Part 1: Model description and global climatology.', 'Journal of Climate, American Meteorological Society, Vol. 19, No.7, pages 1274-1301.', '', '', '', 'documentHardcopy', 'Martin G.M., M.A. Ringer, V.D. Pope, A. Jones, C. Dearden and T.J. Hinton (2006) The physical properties of the atmosphere in the new Hadley Centre Global Environmental Model, HadGEM1 - Part 1: Model description and global climatology. Journal of Climate, American Meteorological Society, Vol. 19, No.7, pages 1274-1301.', '', '0000-00-00 00:00:00', 'marke'),
(9, 'Ringer M.A., G.M. Martin, C.Z. Greeves, T.J. Hinton, P.M. James, V.D. Pope, A.A. Scaife, R.A. Stratton, P.M. Inness, J.M. Slingo, and G.-Y. Yang', '2006', 'The physical properties of the atmosphere in the new Hadley Centre Global Environmental Model, HadGEM1 - Part 2: Aspects of variability and regional climate.', 'Journal of Climate, American Meteorological Society, Vol. 19, No. 7, pages 1302-1326.', '', '', '', 'documentHardcopy', 'Ringer M.A., G.M. Martin, C.Z. Greeves, T.J. Hinton, P.M. James, V.D. Pope, A.A. Scaife, R.A. Stratton, P.M. Inness, J.M. Slingo, and G.-Y. Yang (2006) The physical properties of the atmosphere in the new Hadley Centre Global Environmental Model, HadGEM1 - Part 2: Aspects of variability and regional climate. Journal of Climate, American Meteorological Society, Vol. 19, No. 7, pages 1302-1326.', '', '0000-00-00 00:00:00', 'marke'),
(10, 'Stott P.A., G.S. Jones, J.A. Lowe, P.W. Thorne, C.F. Durman, T.C. Johns, and J.-C. Thelen', '2006', 'Transient climate simulations with the HadGEM1 climate model: Causes of past warming and future climate change.', 'Journal of Climate, American Meteorological Society, Vol. 19, No. 12, pages 2763-2782.', '', '', '', 'documentHardcopy', 'Stott P.A., G.S. Jones, J.A. Lowe, P.W. Thorne, C.F. Durman, T.C. Johns, and J.-C. Thelen (2006) Transient climate simulations with the HadGEM1 climate model: Causes of past warming and future climate change. Journal of Climate, American Meteorological Society, Vol. 19, No. 12, pages 2763-2782.', '', '0000-00-00 00:00:00', 'marke'),
(11, 'McLaren A.J., H. T. Banks, C. F. Durman, J. M. Gregory, T. C. Johns, A. B. Keen, J. K. Ridley, M. J. Roberts, W. H. Lipscomb, W. M. Connolley and S. W. Laxon', '2006', 'Evaluation of the sea ice simulation in a new coupled atmosphere-ocean climate model.', 'Journal of Geophysical Research - Oceans, American Geophysical Union, Vol. 111, C12014, doi:10.1029/2005JC003033.', 'doi:10.1029/2005JC003033.', '', '', 'documentHardcopy', 'McLaren A.J., H. T. Banks, C. F. Durman, J. M. Gregory, T. C. Johns, A. B. Keen, J. K. Ridley, M. J. Roberts, W. H. Lipscomb, W. M. Connolley and S. W. Laxon (2006) Evaluation of the sea ice simulation in a new coupled atmosphere-ocean climate model. Journal of Geophysical Research - Oceans, American Geophysical Union, Vol. 111, C12014, doi:10.1029/2005JC003033.', '', '0000-00-00 00:00:00', 'marke'),
(12, 'Davies T., M. J. P. Cullen, A. J. Malcolm, M. H. Mawson, A. Staniforth, A. A. White, and N. Wood', '2005', 'A new dynamical core for the Met Office\'s global and regional modelling of the atmosphere.', 'Quarterly Journal Royal Meteorology Society, 131, 1759-1782.', '', '', '', 'documentHardcopy', 'Davies T., M. J. P. Cullen, A. J. Malcolm, M. H. Mawson, A. Staniforth, A. A. White, and N. Wood (2005) A new dynamical core for the Met Office\'s global and regional modelling of the atmosphere.. Quarterly Journal Royal Meteorology Society, 131, 1759-1782.', '', '0000-00-00 00:00:00', 'marke'),
(13, 'Essery R., M. Best, and P. Cox', '2001', 'MOSES 2.2 technical documentation.', 'Hadley Centre Technical Note 30, 30 pp.', '', '', 'http://www.metoffice.gov.uk/publications/HCTN/HCTN_30.pdf', 'documentDigital', 'Essery R., M. Best, and P. Cox (2001) MOSES 2.2 technical documentation.. Hadley Centre Technical Note 30, 30 pp.', '', '0000-00-00 00:00:00', 'marke'),
(14, 'Cox P. M., R. A. Betts, C. B. Bunton, R. L. H. Essery, P. R. Rowntree, and J. Smith', '1999', 'The impact of new land surface physics on the GCM simulation of climate and climate sensitivity.', 'Climate Dynamics., 15, 183-203.', '', '', '', 'documentHardcopy', 'Cox P. M., R. A. Betts, C. B. Bunton, R. L. H. Essery, P. R. Rowntree, and J. Smith (1999) The impact of new land surface physics on the GCM simulation of climate and climate sensitivity.. Climate Dynamics., 15, 183-203.', '', '0000-00-00 00:00:00', 'marke'),
(15, 'Lock A.P., A.R. Brown, M.R. Bush, G.M. Martin, R.N.B. Smith et al. ', '2000', 'A new boundary layer mixing scheme. Part I: scheme description and single column model tests.', 'Monthly Weather Review, American Meteorological Society, 128, 3187-3199.', '', '', '', 'documentHardcopy', 'Lock A.P., A.R. Brown, M.R. Bush, G.M. Martin, R.N.B. Smith et al.  (2000) A new boundary layer mixing scheme. Part I: scheme description and single column model tests.. Monthly Weather Review, American Meteorological Society, 128, 3187-3199.', '', '0000-00-00 00:00:00', 'marke'),
(16, 'Smith R.N.B.,', '1993', 'Experience and developments with the layer cloud and boundary layer mixing schemes in the UK Meteorological Office Unified Model.', 'Proc. ECMWF/GCSS Workshop on Parametrization of the Cloud-Topped Boundary Layer, ECMWF, Reading, England, 319-339.', '', '', '', 'documentHardcopy', 'Smith R.N.B., (1993) Experience and developments with the layer cloud and boundary layer mixing schemes in the UK Meteorological Office Unified Model.. Proc. ECMWF/GCSS Workshop on Parametrization of the Cloud-Topped Boundary Layer, ECMWF, Reading, England, 319-339.', '', '0000-00-00 00:00:00', 'marke'),
(17, 'King J.C., W.M. Connolley, and S.H. Derbyshire', '2001', 'Sensitivity of modelled Antarctic climate to surface and boundarylayer flux parametrizations.', 'Quarterly Journal of Royal Meteorological Society, 127, 779-794.', '', '', '', 'documentHardcopy', 'King J.C., W.M. Connolley, and S.H. Derbyshire (2001) Sensitivity of modelled Antarctic climate to surface and boundarylayer flux parametrizations. Quarterly Journal of Royal Meteorological Society, 127, 779-794.', '', '0000-00-00 00:00:00', 'marke'),
(18, 'Brown A.R., and A.L.M. Grant', '1997', 'Non-local mixing of momentum in the convective boundary layer.', 'Boundary Layer Meteorology, 84, 1-22.', '', '', '', 'documentHardcopy', 'Brown A.R., and A.L.M. Grant (1997) Non-local mixing of momentum in the convective boundary layer.. Boundary Layer Meteorology, 84, 1-22.', '', '0000-00-00 00:00:00', 'marke'),
(19, 'Webster S., A.R. Brown, D.R. Cameron and C.P. Jones', '2003', 'Improvements to the Representation of Orography in the Met Office Unified Model.', 'Quarterly Journal of Royal Meteorological Society, 129 (591), 1989-2010 Part B.', '', '', '', 'documentHardcopy', 'Webster S., A.R. Brown, D.R. Cameron and C.P. Jones (2003) Improvements to the Representation of Orography in the Met Office Unified Model. Quarterly Journal of Royal Meteorological Society, 129 (591), 1989-2010 Part B.', '', '0000-00-00 00:00:00', 'marke'),
(20, 'Roberts M. J., H. Banks, N. Gedney, J. Gregory, R. Hill, S. Mullerworth, A. Paerdaens, G. Rickard, R.Thorpe and R. Wood', '2004', 'Impact of eddy permitting ocean resolution on control and climate change simulations with a global coupled GCM.', 'Journal of Climate, 17, 3-20.', '', '', '', 'documentHardcopy', 'Roberts M. J., H. Banks, N. Gedney, J. Gregory, R. Hill, S. Mullerworth, A. Paerdaens, G. Rickard, R.Thorpe and R. Wood (2004) Impact of eddy permitting ocean resolution on control and climate change simulations with a global coupled GCM. Journal of Climate, 17, 3-20.', '', '0000-00-00 00:00:00', 'marke'),
(21, 'Bryan K.,', '1969', 'A numerical method for the study of the circulation of the world ocean.', 'Journal of Computational Physics, 4, 347-376.', '', '', '', 'documentHardcopy', 'Bryan K., (1969) A numerical method for the study of the circulation of the world ocean.. Journal of Computational Physics, 4, 347-376.', '', '0000-00-00 00:00:00', 'marke'),
(22, 'Cox M.D.,', '1984', 'A primitive equation, three dimensional model of the ocean.', 'Ocean Group Technical Report 1, GFDL, Princeton.', '', '', '', 'documentHardcopy', 'Cox M.D., (1984) A primitive equation, three dimensional model of the ocean.. Ocean Group Technical Report 1, GFDL, Princeton.', '', '0000-00-00 00:00:00', 'marke'),
(24, 'Jones A., and D.L. Roberts ', '2004', 'An interactive DMS emissions scheme for the Unified Model.', 'Hadley Centre Technical Note 47, Met Office, Exeter.', '', '', 'http://www.metoffice.gov.uk/publications/HCTN/HCTN_47.pdf', 'documentDigital', 'Jones A., and D.L. Roberts  (2004) An interactive DMS emissions scheme for the Unified Model.. Hadley Centre Technical Note 47, Met Office, Exeter.', '', '0000-00-00 00:00:00', 'marke'),
(25, 'Roberts D.L., and A. Jones', '2004', 'Climate sensitivity to black carbon aerosol from fossil fuel combustion.', 'J. Geophys. Resr., 109, doi: 10.1029/2004JD004676.', 'doi: 10.1029/2004JD004676', '', '', 'documentHardcopy', 'Roberts D.L., and A. Jones (2004) Climate sensitivity to black carbon aerosol from fossil fuel combustion. J. Geophys. Resr., 109, doi: 10.1029/2004JD004676.', '', '0000-00-00 00:00:00', 'marke'),
(26, 'Jones A., D.L. Roberts, M.J. Woodage and C.E. Johnson', '2001', 'Indirect sulphate aerosol forcing in a climate model with an interactive sulpher cycle.', 'J. Geophys Res., 106, 20293-20310.', '', '', '', 'documentHardcopy', 'Jones A., D.L. Roberts, M.J. Woodage and C.E. Johnson (2001) Indirect sulphate aerosol forcing in a climate model with an interactive sulpher cycle.. J. Geophys Res., 106, 20293-20310.', '', '0000-00-00 00:00:00', 'marke'),
(27, 'Woodage M., P. Davison, and D.L. Roberts', '2003', 'Aerosol Processes.', 'Unified Model documentation Paper no. 20, Met Office, Exeter.', '', '', '', 'documentHardcopy', 'Woodage M., P. Davison, and D.L. Roberts (2003) Aerosol Processes.. Unified Model documentation Paper no. 20, Met Office, Exeter.', '', '0000-00-00 00:00:00', 'marke'),
(28, 'Gregory J., and P.R. Rowntree ', '1990', 'A mass flux convection scheme with representation of cloud ensemble characteristics and stability - dependent closure.', 'Monthly Weather Review, 118, 1483-1506.', '', '', '', 'documentHardcopy', 'Gregory J., and P.R. Rowntree  (1990) A mass flux convection scheme with representation of cloud ensemble characteristics and stability - dependent closure.. Monthly Weather Review, 118, 1483-1506.', '', '0000-00-00 00:00:00', 'marke'),
(29, 'Grant A.L.M.,', '2001', 'Cloud base fluxes in the cumulus-capped boundary layer.', 'Quarterly Journal of Royal Meteorological Society, 127: 407-421.', '', '', '', 'documentHardcopy', 'Grant A.L.M., (2001) Cloud base fluxes in the cumulus-capped boundary layer.. Quarterly Journal of Royal Meteorological Society, 127: 407-421.', '', '0000-00-00 00:00:00', 'marke'),
(30, 'Fritsch J. M., and C. F. Chappell', '1980', 'Numerical prediction of convectively driven mesoscale pressure systems - Part I: Convective parameterization.', 'Journal of Atmospheric Sciences, 37, 1722-1733.', '', '', '', 'documentHardcopy', 'Fritsch J. M., and C. F. Chappell (1980) Numerical prediction of convectively driven mesoscale pressure systems - Part I: Convective parameterization.. Journal of Atmospheric Sciences, 37, 1722-1733.', '', '0000-00-00 00:00:00', 'marke'),
(31, 'Gregory J.,', '1999', 'Representation of the radiative effects of convective anvils.', 'Hadley Centre Technical Note 7., Met. Office, Exeter', '', '', '', 'documentHardcopy', 'Gregory J., (1999) Representation of the radiative effects of convective anvils.. Hadley Centre Technical Note 7., Met. Office, Exeter', '', '0000-00-00 00:00:00', 'marke'),
(32, 'Grant A.L.M., and A. R. Brown,', '1999', 'A similarity hypothesis for shallow cumulus transports.', 'Quarterly Journal of Royal Meteorological Society, 125, 1913-1936.', '', '', '', 'documentHardcopy', 'Grant A.L.M., and A. R. Brown, (1999) A similarity hypothesis for shallow cumulus transports.. Quarterly Journal of Royal Meteorological Society, 125, 1913-1936.', '', '0000-00-00 00:00:00', 'marke'),
(33, 'Derbyshire S.H., A. V. Maidens,  S. F. Milton, R. A. Stratton and M. R. Willett', '2010', 'Adaptive detrainment in a convective parametrization.', 'Submitted to Q.J. Royal Meteorol. Soc.', '', '', '', 'documentHardcopy', 'Derbyshire S.H., A. V. Maidens,  S. F. Milton, R. A. Stratton and M. R. Willett (2010) Adaptive detrainment in a convective parametrization.. Submitted to Q.J. Royal Meteorol. Soc.', '', '0000-00-00 00:00:00', 'marke'),
(34, 'Wilson D. R., and S. P. Ballard', '1999', 'A microphysically based precipitation scheme for the Met Office Unified Model.', 'Quarterly Journal of Royal Meteorological Society, 125, 1607-1636.', '', '', '', 'documentHardcopy', 'Wilson D. R., and S. P. Ballard (1999) A microphysically based precipitation scheme for the Met Office Unified Model.. Quarterly Journal of Royal Meteorological Society, 125, 1607-1636.', '', '0000-00-00 00:00:00', 'marke'),
(35, 'Smith R. N. B.,', '1990', 'A scheme for predicting layer clouds and their water content in a general circulation model.', 'Quarterly Journal of Royal Meteorological Society, 116, 435-460.', '', '', '', 'documentHardcopy', 'Smith R. N. B., (1990) A scheme for predicting layer clouds and their water content in a general circulation model.. Quarterly Journal of Royal Meteorological Society, 116, 435-460.', '', '0000-00-00 00:00:00', 'marke'),
(36, 'Oki T., and Y.C. Sud', '1998', 'Design of the Total Runoff Integrating Pathways [TRIP] - A global river channel network.', 'Earth Interactions, 2.', '', '', '', 'documentHardcopy', 'Oki T., and Y.C. Sud (1998) Design of the Total Runoff Integrating Pathways [TRIP] - A global river channel network.. Earth Interactions, 2.', '', '0000-00-00 00:00:00', 'marke'),
(37, 'Pacanowski R. C., and S. M. Griffies', '1998', 'MOM 3.0 manual.', 'NOAA/Geophysical Fluid Dynamics Laboratory, Princeton, NJ, 692 pp. ', '', '', '', 'documentHardcopy', 'Pacanowski R. C., and S. M. Griffies (1998) MOM 3.0 manual.. NOAA/Geophysical Fluid Dynamics Laboratory, Princeton, NJ, 692 pp. ', '', '0000-00-00 00:00:00', 'marke'),
(38, 'Griffies S. M., A. Gnanadesikan, R. C. Pacanowski, V. D. Larichev, J. K. Dukowicz, and R. D. Smith', '1998', 'Isoneutral diffusion in a z-coordinate ocean model.', 'Journal of Physical Oceanography, 28, 805-830.', '', '', '', 'documentHardcopy', 'Griffies S. M., A. Gnanadesikan, R. C. Pacanowski, V. D. Larichev, J. K. Dukowicz, and R. D. Smith (1998) Isoneutral diffusion in a z-coordinate ocean model.. Journal of Physical Oceanography, 28, 805-830.', '', '0000-00-00 00:00:00', 'marke'),
(39, 'Gent P. R., and J. C. McWilliams', '1990', 'Isopycnal mixing in ocean circulation models.', 'Journal of Physical Oceanography, 20, 150-155.', '', '', '', 'documentHardcopy', 'Gent P. R., and J. C. McWilliams (1990) Isopycnal mixing in ocean circulation models.. Journal of Physical Oceanography, 20, 150-155.', '', '0000-00-00 00:00:00', 'marke'),
(40, 'Griffies S. M.,', '1998', 'The Gent-McWilliams skew flux.', 'Journal of Physical Oceanography, 28, 831-841.', '', '', '', 'documentHardcopy', 'Griffies S. M., (1998) The Gent-McWilliams skew flux.. Journal of Physical Oceanography, 28, 831-841.', '', '0000-00-00 00:00:00', 'marke'),
(41, 'Visbeck M., J. Marshall, T. Haine, and M. Spall', '1997', 'Specification of eddy transfer coefficients in coarse-resolution ocean circulation models.', 'Journal of Physical Oceanography, 27, 381-402.', '', '', '', 'documentHardcopy', 'Visbeck M., J. Marshall, T. Haine, and M. Spall (1997) Specification of eddy transfer coefficients in coarse-resolution ocean circulation models.. Journal of Physical Oceanography, 27, 381-402.', '', '0000-00-00 00:00:00', 'marke'),
(42, 'Roberts M. J.,', '2004', 'The Gent and McWilliams parameterisation scheme, including Visbeck and biharmonic GM schemes.', 'Tech. Rep., Unified Model Documentation Paper UMDP54, Met Office, 23 pp.', '', '', '', 'documentHardcopy', 'Roberts M. J., (2004) The Gent and McWilliams parameterisation scheme, including Visbeck and biharmonic GM schemes.. Tech. Rep., Unified Model Documentation Paper UMDP54, Met Office, 23 pp.', '', '0000-00-00 00:00:00', 'marke'),
(43, 'Roberts M. J., and D. Marshall', '1998', 'Do we require adiabatic dissipation schemes in eddy-resolving ocean models?', 'Journal of Physical Oceanography, 28, 2050-2063.', '', '', '', 'documentHardcopy', 'Roberts M. J., and D. Marshall (1998) Do we require adiabatic dissipation schemes in eddy-resolving ocean models?. Journal of Physical Oceanography, 28, 2050-2063.', '', '0000-00-00 00:00:00', 'marke'),
(44, 'Moum J.N., and T.R. Osborn', '1986', 'Mixing in the main thermocline.', 'Journal of Physical Oceanography, Vol 16, Issue 7, pp1250-1259.', '', '', '', 'documentHardcopy', 'Moum J.N., and T.R. Osborn (1986) Mixing in the main thermocline.. Journal of Physical Oceanography, Vol 16, Issue 7, pp1250-1259.', '', '0000-00-00 00:00:00', 'marke'),
(45, 'Paulson C. A., and J. J. Simpson', '1977', 'Irradiance Measurements in the Upper Ocean.', 'Journal of Physical Oceanography, 7, 952-956.', '', '', '', 'documentHardcopy', 'Paulson C. A., and J. J. Simpson (1977) Irradiance Measurements in the Upper Ocean.. Journal of Physical Oceanography, 7, 952-956.', '', '0000-00-00 00:00:00', 'marke'),
(46, 'Kraus E. B., and J. S. Turner', '1967', 'A one-dimensional model of the seasonal thermocline, Part II.', 'Tellus, 19, 98-105.', '', '', '', 'documentHardcopy', 'Kraus E. B., and J. S. Turner (1967) A one-dimensional model of the seasonal thermocline, Part II.. Tellus, 19, 98-105.', '', '0000-00-00 00:00:00', 'marke'),
(47, 'Peters H., M. C. Gregg, and J. M. Toole', '1988', 'On the parameterization of equatorial turbulence.', 'Journal of Geophysical Research, 93, 1199-1218.', '', '', '', 'documentHardcopy', 'Peters H., M. C. Gregg, and J. M. Toole (1988) On the parameterization of equatorial turbulence. Journal of Geophysical Research, 93, 1199-1218.', '', '0000-00-00 00:00:00', 'marke'),
(48, 'Large W. G., J. C. McWilliams and S.C. Doney', '1994', 'Ocean vertical mixing: A review and a nonlocal boundary layer parameterization.', 'Reviews of Geophysics, 32, 363-403.', '', '', '', 'documentHardcopy', 'Large W. G., J. C. McWilliams and S.C. Doney (1994) Ocean vertical mixing: A review and a nonlocal boundary layer parameterization. Reviews of Geophysics, 32, 363-403.', '', '0000-00-00 00:00:00', 'marke'),
(49, 'Dukowicz J. K., and R. D. Smith', '1994', 'Implicit free surface method for the Bryan-Cox-Semtner ocean model.', 'Journal of Geophysical Research, C4, 7991-8014.', '', '', '', 'documentHardcopy', 'Dukowicz J. K., and R. D. Smith (1994) Implicit free surface method for the Bryan-Cox-Semtner ocean model.. Journal of Geophysical Research, C4, 7991-8014.', '', '0000-00-00 00:00:00', 'marke'),
(50, 'Rahmstorf S.,', '1993', 'A fast and complete convection scheme for ocean models.', 'Ocean Modelling, 101, 9-11.', '', '', '', 'documentHardcopy', 'Rahmstorf S., (1993) A fast and complete convection scheme for ocean models.. Ocean Modelling, 101, 9-11.', '', '0000-00-00 00:00:00', 'marke'),
(51, 'Roether W., V. M. Roussenov and R. Well', '1994', 'A tracer study of the thermohaline circulation of the eastern Mediterranean.', 'In: Malanotte-Rizzoli P, Robinson AR (eds) Ocean Processes in climate dynamics, global and Mediterranean example, Kluwer Academic Press, Dordrecht, pp 371-394.', '', '', '', 'documentHardcopy', 'Roether W., V. M. Roussenov and R. Well (1994) A tracer study of the thermohaline circulation of the eastern Mediterranean.. In: Malanotte-Rizzoli P, Robinson AR (eds) Ocean Processes in climate dynamics, global and Mediterranean example, Kluwer Academic Press, Dordrecht, pp 371-394.', '', '0000-00-00 00:00:00', 'marke'),
(52, 'Johns T.C., et al.', '2005', 'HadGEM1 - Model description and analysis of preliminary experiments for the IPCC Fourth Assessment Report.', 'Hadley Centre Technical Note 55, Met, Office, Exeter 74pp.', '', '', 'http://www.metoffice.gov.uk/publications/HCTN/HCTN_55.pdf', 'documentDigital', 'Johns T.C., et al. (2005) HadGEM1 - Model description and analysis of preliminary experiments for the IPCC Fourth Assessment Report.. Hadley Centre Technical Note 55, Met, Office, Exeter 74pp.', '', '0000-00-00 00:00:00', 'marke'),
(53, 'Hunke E., and J. Dukowicz', '1997', 'An elastic-viscous-plastic model for sea-ice dynamics.', 'Journal of Physical Oceanography, 27, 1849-1867.', '', '', '', 'documentHardcopy', 'Hunke E., and J. Dukowicz (1997) An elastic-viscous-plastic model for sea-ice dynamics.. Journal of Physical Oceanography, 27, 1849-1867.', '', '0000-00-00 00:00:00', 'marke'),
(54, 'Semtner A.,', '1976', 'A model for the thermodynamic growth of sea ice in numerical investigations of climate.', 'Journal of Physical Oceanography, 6, 379-389', '', '', '', 'documentHardcopy', 'Semtner A., (1976) A model for the thermodynamic growth of sea ice in numerical investigations of climate.. Journal of Physical Oceanography, 6, 379-389', '', '0000-00-00 00:00:00', 'marke'),
(55, 'Lipscomb W.,', '2001', 'Remapping the thickness distribution in sea ice models.', 'Journal of Geophysical Research, 106, 13989-14000', '', '', '', 'documentHardcopy', 'Lipscomb W., (2001) Remapping the thickness distribution in sea ice models.. Journal of Geophysical Research, 106, 13989-14000', '', '0000-00-00 00:00:00', 'marke'),
(56, 'McPhee M. G.,', '1992', 'Turbulent heat-flux in the upper ocean under sea ice.', 'Journal of Geophysical Research-Oceans, American Geophysical Union, 97(C4), 5365-5379.', '', '', '', 'documentHardcopy', 'McPhee M. G., (1992) Turbulent heat-flux in the upper ocean under sea ice.. Journal of Geophysical Research-Oceans, American Geophysical Union, 97(C4), 5365-5379.', '', '0000-00-00 00:00:00', 'marke'),
(57, 'Ebert E. E., and J. A. Curry', '1993', 'An intermediate one-dimensional thermodynamic sea ice model for investigating ice-atmosphere interactions.', 'Journal of Geophysical Research, 98, 10085-10109.', '', '', '', 'documentHardcopy', 'Ebert E. E., and J. A. Curry (1993) An intermediate one-dimensional thermodynamic sea ice model for investigating ice-atmosphere interactions. Journal of Geophysical Research, 98, 10085-10109.', '', '0000-00-00 00:00:00', 'marke'),
(58, 'Semtner A.,', '1987', 'A numerical study of sea ice and ocean circulation in the Arctic.', 'Journal of Physical Oceanography, 17, 1077-1099.', '', '', '', 'documentHardcopy', 'Semtner A., (1987) A numerical study of sea ice and ocean circulation in the Arctic.. Journal of Physical Oceanography, 17, 1077-1099.', '', '0000-00-00 00:00:00', 'marke'),
(59, 'Pope, V., M.L. Gallani, P.R. Rowntree, R.A. Stratton', '2000', 'The impact of new physical parameterisations in the Hadley Centre climate model: HadAM3.', 'Climate Dynamics, 16, pp123-146.', '', '', '', 'documentHardcopy', 'Pope, V., M.L. Gallani, P.R. Rowntree, R.A. Stratton (2000) The impact of new physical parameterisations in the Hadley Centre climate model: HadAM3. Climate Dynamics, 16, pp123-146.', '', '0000-00-00 00:00:00', 'marke'),
(60, 'Gordon, C., C. Cooper, C.A. Senior, H.T. Banks, J.M. Gregory, T.C. Johns, J.F.B Mitchell and R.A. Wood', '2000', 'The simulation of SST, sea ice extents and ocean heat transports in a version of the Hadley Centre coupled model without flux adjustments.', 'Climate Dynamics, 16, pp147-168.', '', '', '', 'documentHardcopy', 'Gordon, C., C. Cooper, C.A. Senior, H.T. Banks, J.M. Gregory, T.C. Johns, J.F.B Mitchell and R.A. Wood (2000) The simulation of SST, sea ice extents and ocean heat transports in a version of the Hadley Centre coupled model without flux adjustments. Climate Dynamics, 16, pp147-168.', '', '0000-00-00 00:00:00', 'marke'),
(61, 'Booth, B. B. B., C. D. Jones, M. Collins, I. J. Totterdell, P. M. Cox, S. Sitch, C. Huntingford and R. A. Betts', '2009', 'Global warming uncertainties due to carbon cycle feedbacks exceed those due to CO2 emissions', '	\r\n	EGU General Assembly 2009, held 19-24 April, 2009 in Vienna, Austria', '', '', 'http://adsabs.harvard.edu/abs/2009EGUGA..11.4179B', 'documentDigital', 'Booth, B. B. B., C. D. Jones, M. Collins, I. J. Totterdell, P. M. Cox, S. Sitch, C. Huntingford and R. A. Betts (2009) Global warming uncertainties due to carbon cycle feedbacks exceed those due to CO2 emissions. 	\r\n	EGU General Assembly 2009, held 19-24 April, 2009 in Vienna, Austria', '', '0000-00-00 00:00:00', 'pamv'),
(62, 'Johns, T.C., J.M. Gregory, W.J. Ingram, C.E. Johnson, A. Jones, J.A. Lowe, J.F.B. Mitchell, D.L. Roberts, D.M.H Sexton, D.S Stevenson, S.F.B. Tett, and M.J. Woodage', '2003', 'Anthropogenic climate change for 1860 to 2100 simulated with the HadCM3 model under updated emissions scenarios.', 'Climate Dynamics, 20, 583-612.', '', '', '', 'documentHardcopy', 'Johns, T.C., J.M. Gregory, W.J. Ingram, C.E. Johnson, A. Jones, J.A. Lowe, J.F.B. Mitchell, D.L. Roberts, D.M.H Sexton, D.S Stevenson, S.F.B. Tett, and M.J. Woodage (2003) Anthropogenic climate change for 1860 to 2100 simulated with the HadCM3 model under updated emissions scenarios. Climate Dynamics, 20, 583-612.', '', '0000-00-00 00:00:00', 'marke'),
(63, 'Murphy, J.M., B.B.B. Booth, M. Collins, G.R. Harris, D.M.H. Sexton and M.J. Webb ', '2007', 'A methodology for probabilistic predictions of regional climate change from perturbed physics ensembles.', ' Philosophical Transactions of the Royal Society A - Mathematical Physical and Engineering Sciences 365/1857, 1993-2028.', '', '', '', 'documentHardcopy', 'Murphy, J.M., B.B.B. Booth, M. Collins, G.R. Harris, D.M.H. Sexton and M.J. Webb  (2007) A methodology for probabilistic predictions of regional climate change from perturbed physics ensembles.  Philosophical Transactions of the Royal Society A - Mathematical Physical and Engineering Sciences 365/1857, 1993-2028.', '', '0000-00-00 00:00:00', 'marke'),
(64, 'Cox, P.M.', '2001', 'Description of the TRIFFID dynamic global vegetation model.', 'Hadley Centre Technical Note 24, Hadley Centre, Met Office, UK.', '', '', 'http://www.metoffice.gov.uk/publications/HCTN/HCTN_24.pdf', 'documentDigital', 'Cox, P.M. (2001) Description of the TRIFFID dynamic global vegetation model.. Hadley Centre Technical Note 24, Hadley Centre, Met Office, UK.', '', '0000-00-00 00:00:00', 'marke'),
(65, 'Taylor, K.E, R.J Stouffer, and G.A Meehl', '2009', 'A Summary of the CMIP5 Experiment Design', 'IPCC document, 18 December 2009.', '', '', 'cmip-pcmdi.llnl.gov/cmip5/docs/Taylor_CMIP5_design.pdf', 'documentDigital', 'Taylor, K.E, R.J Stouffer, and G.A Meehl (2009) A Summary of the CMIP5 Experiment Design. IPCC document, 18 December 2009.', '', '0000-00-00 00:00:00', 'marke'),
(66, 'Derwent, R.G., Collins, W.J., Jenkin, M.E., and Johnson, C.E.', '2003', 'The global distribution of secondary particulate matter in a 3-D Lagrangian chemistry transport model.', 'J. Atmos. Chem., 44, 57-95, 2003.', '', '', '', 'documentHardcopy', 'Derwent, R.G., Collins, W.J., Jenkin, M.E., and Johnson, C.E. (2003) The global distribution of secondary particulate matter in a 3-D Lagrangian chemistry transport model. J. Atmos. Chem., 44, 57-95, 2003.', '', '0000-00-00 00:00:00', 'marke'),
(67, 'Lamarque, J.F. et al.', '2009', 'Gridded emissions in support of IPCC AR5.', 'IGACtivities 41, 12-18, May 2009.', '', '', '', 'documentHardcopy', 'Lamarque, J.F. et al. (2009) Gridded emissions in support of IPCC AR5.. IGACtivities 41, 12-18, May 2009.', '', '0000-00-00 00:00:00', 'marke'),
(68, 'Spiro, P.A., Jacob, D.J., and Logan, J.A.', '1992', 'Global inventory of sulfur emissions with 1x1 resolution.', 'J. Geophys. Res., 97, 6023-6036, 1992.', '', '', '', 'documentHardcopy', 'Spiro, P.A., Jacob, D.J., and Logan, J.A. (1992) Global inventory of sulfur emissions with 1x1 resolution. J. Geophys. Res., 97, 6023-6036, 1992.', '', '0000-00-00 00:00:00', 'marke'),
(69, 'Woodward S.,', '2001', 'Modelling the atmospheric life cycle and radiative impact of mineral dust in the Hadley Centre climate model.', 'J. Geophys. Res., 106, D16, 18,155-18,166, 2001.', '', '', '', 'documentHardcopy', 'Woodward S., (2001) Modelling the atmospheric life cycle and radiative impact of mineral dust in the Hadley Centre climate model.. J. Geophys. Res., 106, D16, 18,155-18,166, 2001.', '', '0000-00-00 00:00:00', 'marke'),
(70, 'Andres, R.J. and Kasgnoc, A.D.', '1998', 'A time-averaged inventory of subaerial volcanic sulfur emissions.', 'J. Geophys. Res., 103, 25251-25261, 1998.', '', '', '', 'documentHardcopy', 'Andres, R.J. and Kasgnoc, A.D. (1998) A time-averaged inventory of subaerial volcanic sulfur emissions. J. Geophys. Res., 103, 25251-25261, 1998.', '', '0000-00-00 00:00:00', 'marke'),
(71, 'O\'Connor, F.M., C.E. Johnson, O. Morgenstern, and W.J. Collins', '2009', 'Interactions between tropospheric chemistry and climate model temperature and humidity biases', 'Geophys. Res. Lett., 36, L16801, doi:10.1029/2009GL039152,2009.', 'doi:10.1029/2009GL039152,2009', '', '', 'documentHardcopy', 'O\'Connor, F.M., C.E. Johnson, O. Morgenstern, and W.J. Collins (2009) Interactions between tropospheric chemistry and climate model temperature and humidity biases Geophys. Res. Lett., 36, L16801, doi:10.1029/2009GL039152,2009.', '', '0000-00-00 00:00:00', 'marke'),
(72, 'O\'Connor, F. M., C.E. Johnson, O. Morgenstern, M.G. Sanderson, P. Young, G. Zeng, W.J. Collins, and J.A. Pyle', '2010', 'Evaluation of the new UKCA climate-composition model. Part II. The troposphere', 'Geosci. Model Dev. Disc., In preparation, 2010.', '', '', '', 'documentHardcopy', 'O\'Connor, F. M., C.E. Johnson, O. Morgenstern, M.G. Sanderson, P. Young, G. Zeng, W.J. Collins, and J.A. Pyle (2010) Evaluation of the new UKCA climate-composition model. Part II. The troposphere Geosci. Model Dev. Disc., In preparation, 2010.', '', '0000-00-00 00:00:00', 'marke'),
(73, 'Gedney N., Cox, P. M., and Huntingford, C.', '2004', 'Climate feedback from wetland methane emissions', 'Geophys. Res. Lett., 31 (20), L20503, 2004.', '', '', '', 'documentHardcopy', 'Gedney N., Cox, P. M., and Huntingford, C. (2004) Climate feedback from wetland methane emissions. Geophys. Res. Lett., 31 (20), L20503, 2004.', '', '0000-00-00 00:00:00', 'marke'),
(74, 'Price, C. and Rind, D.', '1994', 'Modelling global lightning distributions in a general circulation model', 'Mon. Weath. Rev., 122, 1930-1939, 1994.', '', '', '', 'documentHardcopy', 'Price, C. and Rind, D. (1994) Modelling global lightning distributions in a general circulation model Mon. Weath. Rev., 122, 1930-1939, 1994.', '', '0000-00-00 00:00:00', 'marke'),
(75, 'Law, K. S. and Pyle, J. A.', '1993', 'Modelling trace gas budgets in the troposphere. 1. ozone and odd nitrogen', 'J. Geophys. Res., 98, 18377-18400, 1993.', '', '', '', 'documentHardcopy', 'Law, K. S. and Pyle, J. A. (1993) Modelling trace gas budgets in the troposphere. 1. ozone and odd nitrogen J. Geophys. Res., 98, 18377-18400, 1993.', '', '0000-00-00 00:00:00', 'marke'),
(76, 'Hough, A. M.', '1998', 'The calculation of photolysis rates for use in global tropospheric modelling studies', 'AERE Report, 13259, At. Energy Res. Estab., Harwell, U.K., 1988', '', '', '', 'documentHardcopy', 'Hough, A. M. (1998) The calculation of photolysis rates for use in global tropospheric modelling studies AERE Report, 13259, At. Energy Res. Estab., Harwell, U.K., 1988', '', '0000-00-00 00:00:00', 'marke'),
(77, 'Essery, R. L. H., Best, M. J., Betts, R. A., Cox, P. M., and Taylor, C. M.', '2003', 'Explicit representation of subgrid heterogeneity in a GCM land-surface scheme', 'J. Hydrometeorol., 43, 530-543.', '', '', '', 'documentHardcopy', 'Essery, R. L. H., Best, M. J., Betts, R. A., Cox, P. M., and Taylor, C. M. (2003) Explicit representation of subgrid heterogeneity in a GCM land-surface scheme J. Hydrometeorol., 43, 530-543.', '', '0000-00-00 00:00:00', 'marke'),
(78, 'Collatz, G. J., Ball, J. T., Grivet, C., and Berry, J. A. ', '1991', 'Physiological and environmental-regulation of stomatal conductance, photosynthesis and transpiration - a model that includes a laminar boundary-layer', 'Agr. Forest Meteorol., 54, 107-136.', '', '', '', 'documentHardcopy', 'Collatz, G. J., Ball, J. T., Grivet, C., and Berry, J. A.  (1991) Physiological and environmental-regulation of stomatal conductance, photosynthesis and transpiration - a model that includes a laminar boundary-layer Agr. Forest Meteorol., 54, 107-136.', '', '0000-00-00 00:00:00', 'marke'),
(79, 'Collatz, G. J., Ribas-Carbo, M., and Berry, J. A.', '1992', 'Coupled photosynthesis-stomatal conductance model for leaves of C4 plants', 'Aust. J. Plant Physiol., 19, 519-538.', '', '', '', 'documentHardcopy', 'Collatz, G. J., Ribas-Carbo, M., and Berry, J. A. (1992) Coupled photosynthesis-stomatal conductance model for leaves of C4 plants Aust. J. Plant Physiol., 19, 519-538.', '', '0000-00-00 00:00:00', 'marke'),
(80, 'Mercado, L. M., Huntingford, C., Gash, J. H. C., Cox, P. M., and Jogireddy, V.', '2007', 'Improving the representation of radiation interception and photosynthesis for climate model applications', 'Tellus, 59B, 553-565.', '', '', '', 'documentHardcopy', 'Mercado, L. M., Huntingford, C., Gash, J. H. C., Cox, P. M., and Jogireddy, V. (2007) Improving the representation of radiation interception and photosynthesis for climate model applications Tellus, 59B, 553-565.', '', '0000-00-00 00:00:00', 'marke'),
(81, 'Coleman K, Jenkinson D. S', '1999', 'RothC-26.3, A Model for the Turnover of Carbon in Soil: Model Description and User\'s Guide', 'Lawes Agricultural Trust, Harpenden, UK', '', '', '', 'documentHardcopy', 'Coleman K, Jenkinson D. S (1999) RothC-26.3, A Model for the Turnover of Carbon in Soil: Model Description and User\'s Guide Lawes Agricultural Trust, Harpenden, UK', '', '0000-00-00 00:00:00', 'marke'),
(82, 'Clark, D. B., and Gedney, N.', '2008', 'Representing the effects of subgrid variability of soil moisture on runoff generation in a land surface model', 'J. Geophys. Res., 113, D10, D10111.', '', '', '', 'documentHardcopy', 'Clark, D. B., and Gedney, N. (2008) Representing the effects of subgrid variability of soil moisture on runoff generation in a land surface model J. Geophys. Res., 113, D10, D10111.', '', '0000-00-00 00:00:00', 'marke'),
(83, 'Gedney, N., and Cox, P. M.', '2003', 'The sensitivity of global climate model simulations to the representation of soil moisture heterogeneity', 'J. Hydromet., 4, 6, 1265-1275', '', '', '', 'documentHardcopy', 'Gedney, N., and Cox, P. M. (2003) The sensitivity of global climate model simulations to the representation of soil moisture heterogeneity J. Hydromet., 4, 6, 1265-1275', '', '0000-00-00 00:00:00', 'marke'),
(84, 'Best, M.J., Beljaars, A., Polcher, J., Viterbo, P.,', '2004', 'A proposed structure for coupling tiled land-surfaces with the planetary boundary layer', 'Journal of Hydrometeorology, 5, 1271-1278', '', '', '', 'documentHardcopy', 'Best, M.J., Beljaars, A., Polcher, J., Viterbo, P., (2004) A proposed structure for coupling tiled land-surfaces with the planetary boundary layer Journal of Hydrometeorology, 5, 1271-1278', '', '0000-00-00 00:00:00', 'marke'),
(85, 'Hunke E., and Lipscomb W. ', '2004', 'CICE: The Los Alamos Sea Ice Model, documentation and software, version 3.1', 'LA-CC-98-16, Los Alamos Natl. Lab., U.S.A.', '', '', '', 'documentHardcopy', 'Hunke E., and Lipscomb W.  (2004) CICE: The Los Alamos Sea Ice Model, documentation and software, version 3.1. LA-CC-98-16, Los Alamos Natl. Lab., U.S.A.', '', '0000-00-00 00:00:00', 'marke'),
(86, 'Thorndike, A. S., D. A. Rothrock, G. A. Maykut and R. Colony', '1975', 'The thickness distribution of sea ice', 'Journal of Geophysical Research, 80, 4501-4513.', '', '', '', 'documentHardcopy', 'Thorndike, A. S., D. A. Rothrock, G. A. Maykut and R. Colony (1975) The thickness distribution of sea ice Journal of Geophysical Research, 80, 4501-4513.', '', '0000-00-00 00:00:00', 'marke'),
(87, 'Fasham, M.J.R., Ducklow, H.W. & McKelvie, S.M.', '1990', 'A nitrogen-based model of plankton dynamics in the oceanic mixed layer', 'J. Mar. Res., 48, 591-639', '', '', '', 'documentHardcopy', 'Fasham, M.J.R., Ducklow, H.W. & McKelvie, S.M. (1990) A nitrogen-based model of plankton dynamics in the oceanic mixed layer J. Mar. Res., 48, 591-639', '', '0000-00-00 00:00:00', 'marke'),
(88, 'Goldman, J.C. & Brewer, P.G.', '1980', 'Effect of nitrogen source and growth rate on phytoplankton-mediated changes in alkalinity', 'Limnol. Oceanogr., 25, 352-357', '', '', '', 'documentHardcopy', 'Goldman, J.C. & Brewer, P.G. (1980) Effect of nitrogen source and growth rate on phytoplankton-mediated changes in alkalinity Limnol. Oceanogr., 25, 352-357', '', '0000-00-00 00:00:00', 'marke'),
(89, 'Aranami, K. & Tsunogai, S.', '2004', 'Seasonal and regional comparison of oceanic and atmospheric dimethylsulfide in the northern North Pacific: Dilution effects on its concentration during winter', 'J. Geophys. Res., 109, D12303, doi:10.1029/2003JD004288', 'doi:10.1029/2003JD004288', '', '', 'documentHardcopy', 'Aranami, K. & Tsunogai, S. (2004) Seasonal and regional comparison of oceanic and atmospheric dimethylsulfide in the northern North Pacific: Dilution effects on its concentration during winter J. Geophys. Res., 109, D12303, doi:10.1029/2003JD004288', '', '0000-00-00 00:00:00', 'marke'),
(90, 'Bacastow, R.', '1981', 'Numerical evaluation of the evasion factor, pp95-101 in: Scope 16: Carbon Cycle Modelling', 'Bolin, B., editor, John Wiley, New York', '', '', '', 'documentHardcopy', 'Bacastow, R. (1981) Numerical evaluation of the evasion factor, pp95-101 in: Scope 16: Carbon Cycle Modelling Bolin, B., editor, John Wiley, New York', '', '0000-00-00 00:00:00', 'marke'),
(91, 'Dickson, A.G. ', '1990', 'Thermodynamics of the dissociation of boric acid in synthetic seawater from 273.15 to 318.15 K, ', 'Deep-Sea Res., 37, 755-766', '', '', '', 'documentHardcopy', 'Dickson, A.G.  (1990) Thermodynamics of the dissociation of boric acid in synthetic seawater from 273.15 to 318.15 K,  Deep-Sea Res., 37, 755-766', '', '0000-00-00 00:00:00', 'marke'),
(92, 'DOE,', '1994', 'Handbook of methods for the analysis of the various parameters of the carbon dioxide system in sea water; version 2', 'Dickson, A.G. & Goyet, C., editors, ORNL/CDIAC-74', '', '', '', 'documentHardcopy', 'DOE, (1994) Handbook of methods for the analysis of the various parameters of the carbon dioxide system in sea water; version 2. Dickson, A.G. & Goyet, C., editors, ORNL/CDIAC-74', '', '0000-00-00 00:00:00', 'marke'),
(93, 'Jahne, B., Heinz, G. & Dietrich, W. ', '1987', 'Measurement of the diffusion coefficients of sparingly soluble gases in water with a modified Barrer method, ', 'J. Geophys. Res., 92, 10,767-10,776', '', '', '', 'documentHardcopy', 'Jahne, B., Heinz, G. & Dietrich, W.  (1987) Measurement of the diffusion coefficients of sparingly soluble gases in water with a modified Barrer method,  J. Geophys. Res., 92, 10,767-10,776', '', '0000-00-00 00:00:00', 'marke'),
(94, 'Peng, T.-H., Takahashi, T., Broecker, W.S. & Olafsson J.', '1987', 'Seasonal variability of carbon dioxide, nutrients and oxygen in the northern North Atlantic surface water: observations and a model, ', 'Tellus, 39B, 439-458', '', '', '', 'documentHardcopy', 'Peng, T.-H., Takahashi, T., Broecker, W.S. & Olafsson J. (1987) Seasonal variability of carbon dioxide, nutrients and oxygen in the northern North Atlantic surface water: observations and a model,  Tellus, 39B, 439-458', '', '0000-00-00 00:00:00', 'marke'),
(95, 'Roy, R.N., Roy, L.N., Vogel, K.M., Porter-Moore, C.,Pearson, T., Good, C.E., Millero, F.J. & Campbell, D.M. ', '1993', 'The dissociation constants of carbonic acid in seawater at salinities 5 to 45 and temperatures 0 to 45C, ', 'Mar. Chem., 44, 249-267', '', '', '', 'documentHardcopy', 'Roy, R.N., Roy, L.N., Vogel, K.M., Porter-Moore, C.,Pearson, T., Good, C.E., Millero, F.J. & Campbell, D.M.  (1993) The dissociation constants of carbonic acid in seawater at salinities 5 to 45 and temperatures 0 to 45C,  Mar. Chem., 44, 249-267', '', '0000-00-00 00:00:00', 'marke'),
(96, 'Saltzman, E.S., King, D.B., Holmen, K. & Leck, C. ', '1993', 'Experimental Determination of the Diffusion Coefficient of Dimethylsulfide in Water', 'J. Geophys. Res., 98C, 16481-16486', '', '', '', 'documentHardcopy', 'Saltzman, E.S., King, D.B., Holmen, K. & Leck, C.  (1993) Experimental Determination of the Diffusion Coefficient of Dimethylsulfide in Water J. Geophys. Res., 98C, 16481-16486', '', '0000-00-00 00:00:00', 'marke'),
(97, 'Simo, R. & Dachs, J. ', '2002', 'Global ocean emission of dimethylsulfide predicted from biogeophysical data, ', 'Global Biogeochem. Cycles, 16(4), 1018, doi:10.1029/2001GB001829', 'doi:10.1029/2001GB001829', '', '', 'documentHardcopy', 'Simo, R. & Dachs, J.  (2002) Global ocean emission of dimethylsulfide predicted from biogeophysical data,  Global Biogeochem. Cycles, 16(4), 1018, doi:10.1029/2001GB001829', '', '0000-00-00 00:00:00', 'marke'),
(98, 'Wanninkhof, R. ', '1992', 'Relationship between wind speed and gas exchange over the ocean', 'J. Geophys. Res., 97C, 7373-7382', '', '', '', 'documentHardcopy', 'Wanninkhof, R.  (1992) Relationship between wind speed and gas exchange over the ocean J. Geophys. Res., 97C, 7373-7382', '', '0000-00-00 00:00:00', 'marke'),
(99, 'Weiss, R.F. ', '1974', 'Carbon dioxide in water and seawater: The solubility of a non-ideal gas', 'Mar. Chem., 2, 203-215', '', '', '', 'documentHardcopy', 'Weiss, R.F.  (1974) Carbon dioxide in water and seawater: The solubility of a non-ideal gas Mar. Chem., 2, 203-215', '', '0000-00-00 00:00:00', 'marke'),
(100, 'Garcia, H.E. & Gordon, L.I. ', '1992', 'Oxygen solubility in seawater: Better fitting equations. ', 'Limnol. Oceanogr., 37, 1307-1312', '', '', '', 'documentHardcopy', 'Garcia, H.E. & Gordon, L.I.  (1992) Oxygen solubility in seawater: Better fitting equations.  Limnol. Oceanogr., 37, 1307-1312', '', '0000-00-00 00:00:00', 'marke'),
(101, 'Edwards, J.M. and A. Slingo', '1996', 'Studies with a flexible new radiation code. I: choosing a configuration for a large-scale model', 'Q. J. R. Meteorol. Soc., 122, 689-720', '', '', '', 'documentHardcopy', 'Edwards, J.M. and A. Slingo (1996) Studies with a flexible new radiation code. I: choosing a configuration for a large-scale model Q. J. R. Meteorol. Soc., 122, 689-720', '', '0000-00-00 00:00:00', 'marke'),
(102, 'Rothman, L. S., et al.', '2003', 'The HITRAN molecular spectroscopic database: edition of 2000 including updates through 2001.', 'J. Quant. Spectrosc. Radiat. Transfer, 82, 5-44', 'doi: 10.1016/S0022-4073(03)00146-8', '', '', 'documentHardcopy', 'Rothman, L. S., et al. (2003) The HITRAN molecular spectroscopic database: edition of 2000 including updates through 2001. J. Quant. Spectrosc. Radiat. Transfer, 82, 5-44', '', '0000-00-00 00:00:00', 'marke'),
(103, 'Clough, S.A, M.J. Iacono, and J. L. Moncet', '1992', 'Line-by-line calculations of atmospheric fluxes and cooling rates: application to water vapour.', 'J. Geophys. Res., 97(D14), 15671-15785', '', '', '', 'documentHardcopy', 'Clough, S.A, M.J. Iacono, and J. L. Moncet (1992) Line-by-line calculations of atmospheric fluxes and cooling rates: application to water vapour. J. Geophys. Res., 97(D14), 15671-15785', '', '0000-00-00 00:00:00', 'marke'),
(104, 'Kristjansson, J.E., J.M. Edwards, and D.L. Mitchell', '2000', 'Impact of a new scheme for optical properties of ice crystals on climates of two GCM\'s', 'J. Geophys. Res., 105(D8), 10063-10079', '', '', '', 'documentHardcopy', 'Kristjansson, J.E., J.M. Edwards, and D.L. Mitchell (2000) Impact of a new scheme for optical properties of ice crystals on climates of two GCM\'s J. Geophys. Res., 105(D8), 10063-10079', '', '0000-00-00 00:00:00', 'marke'),
(105, 'Barker, H.W. and Z. Li', '1995', 'Improved simulation of clear-sky shortwave radiative transfer in the CCC-GCM', 'J. Climate, 8, 2213-2223', '', '', '', 'documentHardcopy', 'Barker, H.W. and Z. Li (1995) Improved simulation of clear-sky shortwave radiative transfer in the CCC-GCM J. Climate, 8, 2213-2223', '', '0000-00-00 00:00:00', 'marke'),
(106, 'Collins, M., S.F.B Tett, and C. Cooper', '2001', 'The Internal Climate Variability of HadCM3, a Version of the Hadley Centre Coupled Model without Flux Adjustments.', 'Climate Dynamics, 17 (1): 61-81.', '', '', '', 'documentHardcopy', 'Collins, M., S.F.B Tett, and C. Cooper (2001) The Internal Climate Variability of HadCM3, a Version of the Hadley Centre Coupled Model without Flux Adjustments.. Climate Dynamics, 17 (1): 61-81.', '', '0000-00-00 00:00:00', 'marke'),
(107, 'Roe, P. L. ', '1985', 'Some contributions to the modeling of discontinuous flows. ', 'in Large-Scale Computations in Fluid Mechanics, vol. 22, Lectures in Applied Mathematics, pp. 163-193, Am. Math. Soc., Providence, R. I.', '', '', '', 'documentHardcopy', 'Roe, P. L.  (1985) Some contributions to the modeling of discontinuous flows. . in Large-Scale Computations in Fluid Mechanics, vol. 22, Lectures in Applied Mathematics, pp. 163-193, Am. Math. Soc., Providence, R. I.', '', '0000-00-00 00:00:00', 'marke'),
(108, 'Cullen M.J.P.,', '1993', 'The unified forecast/climate model', 'Meteorol Mag 122: 81D-94D', '', '', '', 'documentHardcopy', 'Cullen M.J.P., (1993) The unified forecast/climate model. Meteorol Mag 122: 81D-94D', '', '0000-00-00 00:00:00', 'pamv'),
(109, 'Cusack, S., J.M. Edward, and J.M. Crowther', '1999', 'Investigating k-distribution methods for parametrizing gaseous absorption in the Hadley Centre climate model.', 'Journal Geophysical Research 104, 2051-2057.', '', '', '', 'documentHardcopy', 'Cusack, S., J.M. Edward, and J.M. Crowther (1999) Investigating k-distribution methods for parametrizing gaseous absorption in the Hadley Centre climate model. Journal Geophysical Research 104, 2051-2057.', '', '0000-00-00 00:00:00', 'marke'),
(110, 'Gregory, D., R. Kershaw, and P. M. Innes ', '1997', 'Parametrisation of momentum transport by convection II - tests in single column and general circulation models. ', 'Quarterly Journal Royal Meteorological Society 123; 1153-1183.', '', '', '', 'documentHardcopy', 'Gregory, D., R. Kershaw, and P. M. Innes  (1997) Parametrisation of momentum transport by convection II - tests in single column and general circulation models.  Quarterly Journal Royal Meteorological Society 123; 1153-1183.', '', '0000-00-00 00:00:00', 'marke'),
(111, 'Gregory, J. and S. Allen', '1991', 'The effect of convective scale downdrafts upon NWP and climate simulations. ', 'Ninth Conference on Numerical Weather Prediction. Denver, Colorado. American Meteorological Society pp 122-123.', '', '', '', 'documentHardcopy', 'Gregory, J. and S. Allen (1991) The effect of convective scale downdrafts upon NWP and climate simulations.  Ninth Conference on Numerical Weather Prediction. Denver, Colorado. American Meteorological Society pp 122-123.', '', '0000-00-00 00:00:00', 'marke'),
(112, 'Hibler, W.', '1979', 'A dynamical thermodynamic sea ice model', 'J. Phys. Oceanogr., 9, 817-846.\r\n\r\n', '', '', '', 'documentHardcopy', 'Hibler, W. (1979) A dynamical thermodynamic sea ice model J. Phys. Oceanogr., 9, 817-846.\r\n\r\n', '', '0000-00-00 00:00:00', 'marke');
INSERT INTO `ut_reference` (`id`, `authors`, `date`, `title`, `detail`, `doi`, `abstract`, `weblink`, `format`, `reference`, `cim_id`, `upd_date`, `upd_by`) VALUES
(113, 'Curry, J., J. Schramm, D. Perovich and J. Pinto', '2001', 'Applications of SHEBA/FIRE data to evaluation of snow/ice albedo parameterizations. \r\n', ' J. Geophys.  Res., 106, 15345-15355.\r\n', '', '', '', 'documentHardcopy', 'Curry, J., J. Schramm, D. Perovich and J. Pinto (2001) Applications of SHEBA/FIRE data to evaluation of snow/ice albedo parameterizations. \r\n  J. Geophys.  Res., 106, 15345-15355.\r\n', '', '0000-00-00 00:00:00', 'marke'),
(114, 'Senior C., and J. F. B Mitchell ', '1993', 'CO2 and climate: the impact of cloud parametrisation. ', 'Journal of Climatology, 6, 393-418.', '', '', '', 'documentHardcopy', 'Senior C., and J. F. B Mitchell  (1993) CO2 and climate: the impact of cloud parametrisation. . Journal of Climatology, 6, 393-418.', '', '0000-00-00 00:00:00', 'marke'),
(115, 'Martin G.M., D.W. Johnson, and A. Spice', '1994', ' The measurement and parametrisation of effective radius of droplets in warm stratocumulus clouds. ', 'Journal of Atmospheric Science, 51, 1823-1842.', '', '', '', 'documentHardcopy', 'Martin G.M., D.W. Johnson, and A. Spice (1994)  The measurement and parametrisation of effective radius of droplets in warm stratocumulus clouds.  Journal of Atmospheric Science, 51, 1823-1842.', '', '0000-00-00 00:00:00', 'marke'),
(116, 'Gregory D.,', '1995', 'A consistent treatment of the evaporation of rain and snow for use in large-scale models. ', 'Monthly Weather Review, 123, 2716-2732. ', '', '', '', 'documentHardcopy', 'Gregory D., (1995) A consistent treatment of the evaporation of rain and snow for use in large-scale models. . Monthly Weather Review, 123, 2716-2732. ', '', '0000-00-00 00:00:00', 'marke'),
(117, 'Gregory D. and D. Morris', '1996', 'The sensitivity of climate simulations to the specification of mixed phase clouds. ', 'Climate Dynamics, 12, 641-651.', '', '', '', 'documentHardcopy', 'Gregory D. and D. Morris (1996) The sensitivity of climate simulations to the specification of mixed phase clouds.  Climate Dynamics, 12, 641-651.', '', '0000-00-00 00:00:00', 'marke'),
(118, 'Wilson, M. F., and A. Henderson-Sellers', '1985', 'A global archive of land cover and soils data for use in general circulation climate models. ', 'Journal of Climate,5, 119-143.', '', '', '', 'documentHardcopy', 'Wilson, M. F., and A. Henderson-Sellers (1985) A global archive of land cover and soils data for use in general circulation climate models.  Journal of Climate,5, 119-143.', '', '0000-00-00 00:00:00', 'marke'),
(119, 'Wright, D.K.', '1997', 'A new eddy mixing parametrization and ocean general circulation model. ', 'International WOCE News, 26, 27-29.', '', '', '', 'documentHardcopy', 'Wright, D.K. (1997) A new eddy mixing parametrization and ocean general circulation model.  International WOCE News, 26, 27-29.', '', '0000-00-00 00:00:00', 'marke'),
(120, 'Pacanowski R.C., and S.C. Philander', '1981', 'Parametrization of vertical mixing in numerical models of tropical oceans.', ' Journal Physical Oceanography, 11, 1443-1451.', '', '', '', 'documentHardcopy', 'Pacanowski R.C., and S.C. Philander (1981) Parametrization of vertical mixing in numerical models of tropical oceans.  Journal Physical Oceanography, 11, 1443-1451.', '', '0000-00-00 00:00:00', 'marke'),
(121, 'ETOPO5,', '1988', 'Global 5\' x 5\' depth and elevation. ', 'Technical Report, National Geophysical Data Centre, NOAA, US Department of Commerce, Boulder, USA.. Journal of Computational Physics, 4, 347-376', '', '', '', 'documentHardcopy', 'ETOPO5, (1988) Global 5\' x 5\' depth and elevation. . Technical Report, National Geophysical Data Centre, NOAA, US Department of Commerce, Boulder, USA.. Journal of Computational Physics, 4, 347-376', '', '0000-00-00 00:00:00', 'marke'),
(122, 'Dickson, R.R. and J. Brown.', '1994', 'The production of North Atlantic deep water: sources, rates and pathways. ', 'Journal of Geophysical Research, 12, 319-341.', '', '', '', 'documentHardcopy', 'Dickson, R.R. and J. Brown. (1994) The production of North Atlantic deep water: sources, rates and pathways.  Journal of Geophysical Research, 12, 319-341.', '', '0000-00-00 00:00:00', 'marke'),
(123, 'Cattle, H. and J. Crossley', '1995', 'Modelling Arctic climate change. ', 'Philosophical Transactions of the Royal Society, London, A352, 201-213.', '', '', '', 'documentHardcopy', 'Cattle, H. and J. Crossley (1995) Modelling Arctic climate change.  Philosophical Transactions of the Royal Society, London, A352, 201-213.', '', '0000-00-00 00:00:00', 'marke'),
(124, 'Ledley, T. S.', '1985', 'Sea Ice: multiyear cycles and white ice.', 'Journal of Geophysical Research, 90, 5676-5686. ', '', '', '', 'documentHardcopy', 'Ledley, T. S. (1985) Sea Ice: multiyear cycles and white ice. Journal of Geophysical Research, 90, 5676-5686. ', '', '0000-00-00 00:00:00', 'marke'),
(125, 'Bryan, K.', '1969', 'Climate and the ocean circulation III: The ocean model. ', 'Monthly Weather Review, 97, 806-827.', '', '', '', 'documentHardcopy', 'Bryan, K. (1969) Climate and the ocean circulation III: The ocean model.  Monthly Weather Review, 97, 806-827.', '', '0000-00-00 00:00:00', 'marke'),
(126, 'Steele, M., J. Zhang, D. Rothrock, and H. Stern', '1997', 'The force balance of sea ice in a numerical model of the Arctic Ocean. ', 'Journal of Geophysical Research, 102, 21 061 - 21 079.', '', '', '', 'documentHardcopy', 'Steele, M., J. Zhang, D. Rothrock, and H. Stern (1997) The force balance of sea ice in a numerical model of the Arctic Ocean.  Journal of Geophysical Research, 102, 21 061 - 21 079.', '', '0000-00-00 00:00:00', 'marke'),
(127, 'Gregory, D., G.J Shutts, and J.R. Mitchell', '1998', 'A new gravity wave drag scheme incorporating anisotropic orography and low level wave breaking: impact upon the climate of the UK Meteorological Office Unified Model. ', 'Quarterly Journal Royal Meteorological Society, 124, 463-493.', '', '', '', 'documentHardcopy', 'Gregory, D., G.J Shutts, and J.R. Mitchell (1998) A new gravity wave drag scheme incorporating anisotropic orography and low level wave breaking: impact upon the climate of the UK Meteorological Office Unified Model.  Quarterly Journal Royal Meteorological Society, 124, 463-493.', '', '0000-00-00 00:00:00', 'marke'),
(128, 'Milton, S. F., and C.A. Wilson', '1996', 'The impact of parameterised sub-grid scale orographic forcing on systematic errors in a global NWL model. ', 'Monthly Weather Review, 124, 2023-2045.', '', '', '', 'documentHardcopy', 'Milton, S. F., and C.A. Wilson (1996) The impact of parameterised sub-grid scale orographic forcing on systematic errors in a global NWL model.  Monthly Weather Review, 124, 2023-2045.', '', '0000-00-00 00:00:00', 'marke'),
(129, 'Moss R. H., et al.', '2010', 'The next generation of scenarios for climate change research and assessment.', 'Nature, 463, 747-756, doi:10.1038/nature08823', 'doi:10.1038/nature08823', NULL, '<enter URL for paper link>', 'documentHardcopy', 'Moss R. H., et al. (2010) The next generation of scenarios for climate change research and assessment. Nature, 463, 747-756, doi:10.1038/nature08823', '', '0000-00-00 00:00:00', 'marke'),
(130, 'Houldcroft C., W. Grey, M. Barnsley, C. Taylor, S. Los and P. North', '2008', 'New vegetation albedo parameters and global fields of background albedo derived from MODIS for use in a climate model.', 'J. Hydrometeorology, Vol 10, No. 1, pp 183-198, doi:10.1175/2008JHM1021.1', 'doi:10.1175/2008JHM1021.1', NULL, '<enter URL for paper link>', 'documentHardcopy', 'Houldcroft C., W. Grey, M. Barnsley, C. Taylor, S. Los and P. North (2008) New vegetation albedo parameters and global fields of background albedo derived from MODIS for use in a climate model. J. Hydrometeorology, Vol 10, No. 1, pp 183-198, doi:10.1175/2008JHM1021.1', '', '0000-00-00 00:00:00', 'marke'),
(131, 'Bodas-Salcedo, A.  et al. ', '2008', 'Evaluating cloud systems in the Met Office global forecast model using simulated CloudSat radar reflectivities. ', 'J. Geophys. Res., 113, D00A13. ', 'doi:10.1029/2007JD009620.', '', '', 'documentHardcopy', 'Bodas-Salcedo, A.  et al.  (2008) Evaluating cloud systems in the Met Office global forecast model using simulated CloudSat radar reflectivities.  J. Geophys. Res., 113, D00A13. ', '', '0000-00-00 00:00:00', 'marke'),
(132, 'Bodas-Salcedo, A. et al. ', '2011', 'COSP: satellite simulation software for model assessment.', 'Bull. Am. Meteorol. Soc. submitted,', '', '', '', 'documentHardcopy', 'Bodas-Salcedo, A. et al.  (2011) COSP: satellite simulation software for model assessment. Bull. Am. Meteorol. Soc. submitted,', '', '0000-00-00 00:00:00', 'marke'),
(133, 'Chepfer, H. et al.', '2008', 'Use of CALIPSO lidar observations to evaluate the cloudiness simulated by a climate model', 'Geophys. Res. Lett., 35, L15 704', 'doi:10.1029/2008GL034207.', '', '', 'documentHardcopy', 'Chepfer, H. et al. (2008) Use of CALIPSO lidar observations to evaluate the cloudiness simulated by a climate model Geophys. Res. Lett., 35, L15 704', '', '0000-00-00 00:00:00', 'marke'),
(134, 'Haynes, J.M', '2007', 'A multipurpose radar simulation package: Quickbeam', 'Bull. Am. Meteorol. Soc., 88 (11), 1723-1727', 'doi:10.1175/BAMS-88-11-1723.', '', '', 'documentHardcopy', 'Haynes, J.M (2007) A multipurpose radar simulation package: Quickbeam Bull. Am. Meteorol. Soc., 88 (11), 1723-1727', '', '0000-00-00 00:00:00', 'marke'),
(135, 'Klein, S.A., and C. Jakob', '1999', 'Validation and sensitivities of frontal clouds simulated by the ECMWF model.', 'Mon. Weather Rev., 127 (10), 2514-2531', '', '', '', 'documentHardcopy', 'Klein, S.A., and C. Jakob (1999) Validation and sensitivities of frontal clouds simulated by the ECMWF model. Mon. Weather Rev., 127 (10), 2514-2531', '', '0000-00-00 00:00:00', 'marke'),
(136, 'Marchand, R. and T. Ackerman', '2010', 'An analysis of cloud cover in multiscale modeling framework global climate model simulations using 4 and 1 km horizontal grids.', 'J. Geophys. Res., 115, D16 207', 'doi:10.1029/2009JD013423.', '', '', 'documentHardcopy', 'Marchand, R. and T. Ackerman (2010) An analysis of cloud cover in multiscale modeling framework global climate model simulations using 4 and 1 km horizontal grids. J. Geophys. Res., 115, D16 207', '', '0000-00-00 00:00:00', 'marke'),
(137, 'Webb, M. et al.,', '2001', 'Combining ERBE and ISCCP data to assess clouds in the Hadley Centre, ECMWF and LMD atmospheric climate models. ', 'Clim. Dyn., 17, 905-922', '', '', '', 'documentHardcopy', 'Webb, M. et al., (2001) Combining ERBE and ISCCP data to assess clouds in the Hadley Centre, ECMWF and LMD atmospheric climate models.  Clim. Dyn., 17, 905-922', '', '0000-00-00 00:00:00', 'marke'),
(138, 'UNESCO', '1981', 'Tenth report of the joint panel on oceanographic tables and standards', 'Technical Papers in Marine Science 36, UNESCO, Paris', '', '', '', 'documentHardcopy', 'UNESCO (1981) Tenth report of the joint panel on oceanographic tables and standards Technical Papers in Marine Science 36, UNESCO, Paris', '', '0000-00-00 00:00:00', 'marke'),
(139, 'Sato, M., J.E. Hansen, M.P. McCormick, and J.B. Pollack', '1993', 'Stratospheric aerosol optical depths (1850 - 1990)', 'Journal of Geophysical Research, 98, 22987-22994', '', '', '', 'documentHardcopy', 'Sato, M., J.E. Hansen, M.P. McCormick, and J.B. Pollack (1993) Stratospheric aerosol optical depths (1850 - 1990) Journal of Geophysical Research, 98, 22987-22994', '', '0000-00-00 00:00:00', 'marke'),
(140, 'Andreae, M.O., and P. Merlet ', '2001', 'Emission of Trace Gases and Aerosols From Biomass Burning', 'Global Biogeochem. Cy., 15(4), 955-966', '', '', '', 'documentHardcopy', 'Andreae, M.O., and P. Merlet  (2001) Emission of Trace Gases and Aerosols From Biomass Burning Global Biogeochem. Cy., 15(4), 955-966', '', '0000-00-00 00:00:00', 'marke'),
(141, 'Guenther, A., Hewitt, C.N., Erickson, D., Fall, R., Geron, C., Graedel, T., Harley, P., Klinger, L., Lerdau, M., McKay, W.A., T. Pierce, B. Scholes, R. Steinbrecher, R. Tallamraju, J. Taylor, and P. Zimmerman', '1995', 'A global model of natural volatile organic compound emissions', 'J. Geophys. Res., 100(D5), 8873--8892', '', '', '', 'documentHardcopy', 'Guenther, A., Hewitt, C.N., Erickson, D., Fall, R., Geron, C., Graedel, T., Harley, P., Klinger, L., Lerdau, M., McKay, W.A., T. Pierce, B. Scholes, R. Steinbrecher, R. Tallamraju, J. Taylor, and P. Zimmerman (1995) A global model of natural volatile organic compound emissions J. Geophys. Res., 100(D5), 8873--8892', '', '0000-00-00 00:00:00', 'marke'),
(142, 'Lamarque, J.-F., T. C. Bond, V. Eyring, C. Granier, A. Heil, Z. Klimont, D. Lee, C. Liousse, A. Mieville, B. Owen, M. G. Schultz, D. Shindell, S. J. Smith, E. Stehfest, J. Van Aardenne, O. R. Cooper, M. Kainuma, N. Mahowald, J. R. McConnell, V. Naik, K. Riahi, and D. P. van Vuuren', '2010', 'Historical (1850–2000) gridded anthropogenic and biomass burning emissions of reactive gases and aerosols: methodology and application.', 'Atmos. Chem. Phys., 10, 7017-7039', '', '', '', 'documentHardcopy', 'Lamarque, J.-F., T. C. Bond, V. Eyring, C. Granier, A. Heil, Z. Klimont, D. Lee, C. Liousse, A. Mieville, B. Owen, M. G. Schultz, D. Shindell, S. J. Smith, E. Stehfest, J. Van Aardenne, O. R. Cooper, M. Kainuma, N. Mahowald, J. R. McConnell, V. Naik, K. Riahi, and D. P. van Vuuren (2010) Historical (1850–2000) gridded anthropogenic and biomass burning emissions of reactive gases and aerosols: methodology and application. Atmos. Chem. Phys., 10, 7017-7039', '', '0000-00-00 00:00:00', 'marke'),
(143, 'Lamarque, J.-F., K. Riahi, S. Smith, D. van Vuuren, and F. Vitt', '2010', 'Simulated evolution of the distribution of short-lived greenhouse gases and aerosols using the emissions from the Representative Concentration Pathways', 'in preparation', '', '', '', 'documentHardcopy', 'Lamarque, J.-F., K. Riahi, S. Smith, D. van Vuuren, and F. Vitt (2010) Simulated evolution of the distribution of short-lived greenhouse gases and aerosols using the emissions from the Representative Concentration Pathways in preparation', '', '0000-00-00 00:00:00', 'marke'),
(144, 'Pfister, G.G., Emmons, L.K., Hess, P.G., Lamarque, J.-F., J.J. Orlando, S. Walters, A. Guenther, P.I Palmer, and P.J. Lawrence', '2008', 'Contribution of isoprene to chemical budgets: A model tracer study with the NCAR CTM MOZART-4', 'J. Geophys. Res., 113, D05308', 'doi:10.1029/2007JD008948', '', '', 'documentHardcopy', 'Pfister, G.G., Emmons, L.K., Hess, P.G., Lamarque, J.-F., J.J. Orlando, S. Walters, A. Guenther, P.I Palmer, and P.J. Lawrence (2008) Contribution of isoprene to chemical budgets: A model tracer study with the NCAR CTM MOZART-4 J. Geophys. Res., 113, D05308', '', '0000-00-00 00:00:00', 'marke'),
(145, 'Yienger, K., and H. Levy II', '1995', 'Empirical model of global soil-biogenic NOx emissions', 'J. Geophys. Res., 100(D6), 11447-11464', '', '', '', 'documentHardcopy', 'Yienger, K., and H. Levy II (1995) Empirical model of global soil-biogenic NOx emissions J. Geophys. Res., 100(D6), 11447-11464', '', '0000-00-00 00:00:00', 'marke'),
(146, 'Lean, J.L, O.R. White and A. Skumanich', '1995', 'On the solar ultraviolet spectral irradiance during the Maunder Minimum', 'Global Biogeochemical Cycles,\r\n\r\n9, 2, 171-182\r\n\r\n', '', '', '', 'documentHardcopy', 'Lean, J.L, O.R. White and A. Skumanich (1995) On the solar ultraviolet spectral irradiance during the Maunder Minimum Global Biogeochemical Cycles,\r\n\r\n9, 2, 171-182\r\n\r\n', '', '0000-00-00 00:00:00', 'marke'),
(147, 'Lean J.L.', '2009', 'SOLARIS - calculation of solar irradiance', '', '', '', 'http://www.geo.fu-berlin.de/en/met/ag/strat/forschung/SOLARIS/Input_data/Calculations_of_Solar_Irradiance.pdf', 'documentDigital', 'Lean J.L. (2009) SOLARIS - calculation of solar irradiance ', '', '0000-00-00 00:00:00', 'marke'),
(148, 'SOLARIS', '2009', 'CMIP5 solar irradiance', '', '', '', 'http://www.geo.fu-berlin.de/en/met/ag/strat/forschung/SOLARIS/Input_data/CMIP5_solar_irradiance.html', 'documentDigital', 'SOLARIS (2009) CMIP5 solar irradiance ', '', '0000-00-00 00:00:00', 'marke'),
(149, 'Klein Goldewijk K, A. Beusen, and P. Janssen', '2010', 'Long term dynamic modeling of global population and built-up area in a spatially explicit way: HYDE 3.1', 'The Holocene, 20, 565-573', '', '', '', 'documentHardcopy', 'Klein Goldewijk K, A. Beusen, and P. Janssen (2010) Long term dynamic modeling of global population and built-up area in a spatially explicit way: HYDE 3.1 The Holocene, 20, 565-573', '', '0000-00-00 00:00:00', 'marke'),
(150, 'Klein Goldewijk K, Beusen A, van Drecht G, de Vos M ', '2010', 'The HYDE 3.1 spatially explicit database of human induced land use change over the past 12,000 years', 'Global Ecology and Biogeography, in press', '', '', '', 'documentHardcopy', 'Klein Goldewijk K, Beusen A, van Drecht G, de Vos M  (2010) The HYDE 3.1 spatially explicit database of human induced land use change over the past 12,000 years Global Ecology and Biogeography, in press', '', '0000-00-00 00:00:00', 'marke'),
(151, 'Hurtt, G. C. , L. P. Chini, S. Frolking, R. Betts, J. Feddema, G. Fischer, J. P. Fisk, K. Hibbard, R. A. Houghton, A. Janetos, C. Jones, G. Kindermann, T. Kinoshita, K. Klein Goldewijk, K. Riahi, E. Shevliakova, S. Smith, E. Stehfest, A. Thomson, P. Thornton, D. P. van Vuuren, Y. Wang', '2010', 'Harmonization of Land-Use Scenarios for the Period 1500-2100: 600 Years of Global Gridded Annual Land-Use Transitions, Wood Harvest, and Resulting Secondary Lands', 'Climatic Change, submitted', '', '', '<enter URL for paper link>', 'documentHardcopy', 'Hurtt, G. C. , L. P. Chini, S. Frolking, R. Betts, J. Feddema, G. Fischer, J. P. Fisk, K. Hibbard, R. A. Houghton, A. Janetos, C. Jones, G. Kindermann, T. Kinoshita, K. Klein Goldewijk, K. Riahi, E. Shevliakova, S. Smith, E. Stehfest, A. Thomson, P. Thornton, D. P. van Vuuren, Y. Wang (2010) Harmonization of Land-Use Scenarios for the Period 1500-2100: 600 Years of Global Gridded Annual Land-Use Transitions, Wood Harvest, and Resulting Secondary Lands. Climatic Change, submitted', '', '0000-00-00 00:00:00', 'marke'),
(152, 'Smith, D. M., S. Cusack, A. W. Colman, C. K. Folland, G. R. Harris and J. M. Murphy', '2007', 'Improved surface temperature prediction for the coming decade from a global climate model', 'Science, 317, 796-799', 'doi:10.1126/science.1139540', '', '', 'documentHardcopy', 'Smith, D. M., S. Cusack, A. W. Colman, C. K. Folland, G. R. Harris and J. M. Murphy (2007) Improved surface temperature prediction for the coming decade from a global climate model Science, 317, 796-799', '', '0000-00-00 00:00:00', 'marke'),
(153, 'Smith, D. M., R. Eade, N. J. Dunstone, D. Fereday, J. M. Murphy, H. Pohlmann, and A. A. Scaife', '2010', 'Skilful multi-year predictions of Atlantic hurricane frequency', 'Nature Geoscience', 'doi:  10.1038/NGEO1004', '', '', 'documentHardcopy', 'Smith, D. M., R. Eade, N. J. Dunstone, D. Fereday, J. M. Murphy, H. Pohlmann, and A. A. Scaife (2010) Skilful multi-year predictions of Atlantic hurricane frequency Nature Geoscience', '', '0000-00-00 00:00:00', 'marke'),
(154, 'Jones, C.D. et al.', '2011', 'The HadGEM2-ES implementation of CMIP5 centennial simulations', 'Geosci. Model Dev., 4, 543-570, 2011', 'doi:10.5194/gmd-4-543-2011', '', 'http://www.geosci-model-dev.net/4/543/2011/gmd-4-543-2011.html', 'documentDigital', 'Jones, C.D. et al. (2011) The HadGEM2-ES implementation of CMIP5 centennial simulations. Geosci. Model Dev., 4, 543-570, 2011', '', '0000-00-00 00:00:00', 'marke'),
(155, 'Martin G.M. et al.', '2011', 'The HadGEM2 family of Met Office Unified Model climate configurations', 'Geosci. Model Dev., 4, 723-757, 2011', 'doi:10.5194/gmd-4-723-2011', '', 'http://www.geosci-model-dev.net/4/723/2011/gmd-4-723-2011.html', 'documentDigital', 'Martin G.M. et al. (2011) The HadGEM2 family of Met Office Unified Model climate configurations. Geosci. Model Dev., 4, 723-757, 2011', '', '0000-00-00 00:00:00', 'marke'),
(156, 'Collins, W. J., Bellouin, N., Doutriaux-Boucher, M., Gedney, N., Halloran, P., Hinton, T., Hughes, J., Jones, C. D., Joshi, M., Liddicoat, S., Martin, G., O\'Connor, F., Rae, J., Senior, C., Sitch, S., Totterdell, I., Wiltshire, A., and Woodward, S', '2011', 'Development and evaluation of an Earth-system model – HadGEM2', 'Geosci. Model Dev. Discuss., 4, 997-1062, 2011', 'doi:10.5194/gmdd-4-997-2011', '', 'http://www.geosci-model-dev-discuss.net/4/997/2011/gmdd-4-997-2011.html', 'documentDigital', 'Collins, W. J., Bellouin, N., Doutriaux-Boucher, M., Gedney, N., Halloran, P., Hinton, T., Hughes, J., Jones, C. D., Joshi, M., Liddicoat, S., Martin, G., O\'Connor, F., Rae, J., Senior, C., Sitch, S., Totterdell, I., Wiltshire, A., and Woodward, S (2011) Development and evaluation of an Earth-system model – HadGEM2 Geosci. Model Dev. Discuss., 4, 997-1062, 2011', '', '0000-00-00 00:00:00', 'marke'),
(157, 'McSweeney, C. F., R. G. Jones, and B. Booth', '2011', 'Selecting ensemble members to provide regional climate information', 'Submitted to Journal of Climate', '', NULL, '<enter URL for paper link>', 'documentHardcopy', 'McSweeney, C. F., R. G. Jones, and B. Booth (2011) Selecting ensemble members to provide regional climate information Submitted to Journal of Climate', '', '0000-00-00 00:00:00', 'marke'),
(158, 'Hardiman, S. C., Butchart, N., Hinton, T. J., Osprey, S. M., and L. J. Gray', '2012', 'The Effect of a Well-Resolved Stratosphere on Surface Climate: Differences between CMIP5 Simulations with High and Low Top Versions of the Met Office Climate Model', ' J. Climate, 25, 7083–7099', '', '', 'http://dx.doi.org/10.1175/JCLI-D-11-00579.1', 'documentDigital', 'Hardiman, S. C., Butchart, N., Hinton, T. J., Osprey, S. M., and L. J. Gray (2012) The Effect of a Well-Resolved Stratosphere on Surface Climate: Differences between CMIP5 Simulations with High and Low Top Versions of the Met Office Climate Model.  J. Climate, 25, 7083–7099', '', '0000-00-00 00:00:00', 'pamv'),
(159, 'Hardiman, S. C., N. Butchart, S. M. Osprey, L. J. Gray, A. C. Bushell, and T. J. Hinton\r\n', '2010', 'The climatology of the middle atmosphere in a vertically extended version of the Met Office’s climate model. Part I: Mean state. ', ' J. Atmos. Sci., 67, 1509–1525', '', '', 'http://dx.doi.org/10.1175/2009JAS3337.1', 'documentDigital', 'Hardiman, S. C., N. Butchart, S. M. Osprey, L. J. Gray, A. C. Bushell, and T. J. Hinton\r\n (2010) The climatology of the middle atmosphere in a vertically extended version of the Met Office’s climate model. Part I: Mean state. .  J. Atmos. Sci., 67, 1509–1525', '', '0000-00-00 00:00:00', 'pamv'),
(184, 'Jones, A., D. L. Roberts and A. Slingo.', '1994', 'A climate model study of indirect radiative forcing by anthropogenic sulphate aerosols.', 'Nature, 370, 450–453.', '', NULL, 'http://aerosols.ucsd.edu/classes/A_SIO209_WK4_Jones.pdf', 'documentDigital', 'Jones, A., D. L. Roberts and A. Slingo. (1994) A climate model study of indirect radiative forcing by anthropogenic sulphate aerosols. Nature, 370, 450–453.', '', '0000-00-00 00:00:00', 'pamv'),
(160, 'Osprey, S. M., Gray, L. J., Hardiman, S. J.,Butchart, N., Bushell, A. C., and T. J. Hinton ', '2010', 'The Climatology of the Middle Atmosphere in a Vertically Extended Version of the Met Office’s Climate Model. Part II: Variability', ' J. Atmos. Sci., 67, 3637–3651', '', '', ' http://dx.doi.org/10.1175/2010JAS3338.1', 'documentDigital', 'Osprey, S. M., Gray, L. J., Hardiman, S. J.,Butchart, N., Bushell, A. C., and T. J. Hinton  (2010) The Climatology of the Middle Atmosphere in a Vertically Extended Version of the Met Office’s Climate Model. Part II: Variability  J. Atmos. Sci., 67, 3637–3651', '', '0000-00-00 00:00:00', 'pamv'),
(161, 'Osprey, S. M., Gray, L. J., Hardiman, S. C., Butchart, N., and T. J. Hinton.', '2013', 'Stratospheric Variability in Twentieth-Century CMIP5 Simulations of the Met Office Climate Model: High Top versus Low Top.', 'J. Climate, 26, 1595–1606.', '', '', 'http://dx.doi.org/10.1175/JCLI-D-12-00147.1', 'peer reviewed article', ' Osprey, S. M., Gray, L. J., Hardiman, S. C., Butchart, N., and T. J. Hinton. (2013) Stratospheric Variability in Twentieth-Century CMIP5 Simulations of the Met Office Climate Model: High Top versus Low Top. J. Climate, 26, 1595–1606.', '', '2017-02-11 13:59:04', 'pamv'),
(162, 'Hewitt, H. T., Copsey, D., Culverwell, I. D., Harris, C. M., Hill, R. S. R., Keen, A. B., McLaren, A. J., and E. C. Hunke', '2011', 'Design and implementation of the infrastructure of HadGEM3: the next-generation Met Office climate modelling system', 'Geosci. Model Dev., 4, 223-253', '', NULL, 'www.geosci-model-dev.net/4/223/2011/ doi:10.5194/gmd-4-223-2011', 'documentDigital', 'Hewitt, H. T., Copsey, D., Culverwell, I. D., Harris, C. M., Hill, R. S. R., Keen, A. B., McLaren, A. J., and E. C. Hunke (2011) Design and implementation of the infrastructure of HadGEM3: the next-generation Met Office climate modelling system Geosci. Model Dev., 4, 223-253', '', '0000-00-00 00:00:00', 'pamv'),
(163, 'van Genuchten, M. Th', '1980', 'A closed-form equation for predicting the hydraulic conductivity of unsaturated soils', 'Soil Science Society of America Journal, 44:892–898', '', NULL, 'https://dl.sciencesocieties.org/publications/sssaj/abstracts/44/5/SS0440050892', 'documentDigital', 'van Genuchten, M. Th (1980) A closed-form equation for predicting the hydraulic conductivity of unsaturated soils Soil Science Society of America Journal, 44:892–898', '', '0000-00-00 00:00:00', 'pamv'),
(164, 'Randel, W. J. and F. Wu', '2007', 'A  stratospheric ozone profile data set for 1979–2005: Variability, trends, and comparisons with column ozone data', ' J. Geophys. Res., 112, D06313', '', NULL, 'http://onlinelibrary.wiley.com/doi/10.1029/2006JD007339/full', 'documentDigital', 'Randel, W. J. and F. Wu (2007) A  stratospheric ozone profile data set for 1979–2005: Variability, trends, and comparisons with column ozone data  J. Geophys. Res., 112, D06313', '', '0000-00-00 00:00:00', 'pamv'),
(165, 'Edwards, J. M.', '2007', 'Oceanic latent heat fluxes: Consistency with the atmospheric hydrological and energy cycles and general circulation modeling', ' J. Geophys. Res., 112, D06115', '', NULL, 'http://onlinelibrary.wiley.com/doi/10.1029/2006JD007324/full', 'documentDigital', 'Edwards, J. M. (2007) Oceanic latent heat fluxes: Consistency with the atmospheric hydrological and energy cycles and general circulation modeling  J. Geophys. Res., 112, D06115', '', '0000-00-00 00:00:00', 'pamv'),
(166, 'Wilson, D. R., Bushell, A. C., Kerr-Munslow, A. M., Price, J. D. and C. J. Morcrette', '2008', 'A prognostic cloud fraction and condensation scheme. I: Scheme description', 'Q.J.R. Meteorol. Soc., 134: 2093–2107', '', NULL, 'http://onlinelibrary.wiley.com/doi/10.1002/qj.333', 'documentDigital', 'Wilson, D. R., Bushell, A. C., Kerr-Munslow, A. M., Price, J. D. and C. J. Morcrette (2008) A prognostic cloud fraction and condensation scheme. I: Scheme description Q.J.R. Meteorol. Soc., 134: 2093–2107', '', '0000-00-00 00:00:00', 'pamv'),
(167, 'Wilson, D. R., Bushell, Andrew. C., Kerr-Munslow, A. M., Price, J. D., Morcrette, C. J. and A. Bodas-Salcedo', '2008', 'PC2: A prognostic cloud fraction and condensation scheme. II: Climate model simulations', ' Q.J.R. Meteorol. Soc., 134: 2109–2125', '', NULL, 'http://onlinelibrary.wiley.com/doi/10.1002/qj.332', 'documentDigital', 'Wilson, D. R., Bushell, Andrew. C., Kerr-Munslow, A. M., Price, J. D., Morcrette, C. J. and A. Bodas-Salcedo (2008) PC2: A prognostic cloud fraction and condensation scheme. II: Climate model simulations  Q.J.R. Meteorol. Soc., 134: 2109–2125', '', '0000-00-00 00:00:00', 'pamv'),
(168, 'Wood, N., Diamantakis, M. and A. Staniforth', '2997', 'A monotonically-damping second-order-accurate unconditionally-stable numerical scheme for diffusion', ' Q.J.R. Meteorol. Soc., 133: 1559–1573', '', NULL, 'http://onlinelibrary.wiley.com/doi/10.1002/qj.116', 'documentDigital', 'Wood, N., Diamantakis, M. and A. Staniforth (2997) A monotonically-damping second-order-accurate unconditionally-stable numerical scheme for diffusion  Q.J.R. Meteorol. Soc., 133: 1559–1573', '', '0000-00-00 00:00:00', 'pamv'),
(169, 'Raymond, W. H.', '1988', 'High-order low-pass implicit tangent filters for use in finite area calculations', 'Monthly weather review 116.11, 2132-2141', '', NULL, 'http://journals.ametsoc.org/doi/abs/10.1175/1520-0493%281988%29116%3C2132%3AHOLPIT%3E2.0.CO%3B2', 'documentDigital', 'Raymond, W. H. (1988) High-order low-pass implicit tangent filters for use in finite area calculations Monthly weather review 116.11, 2132-2141', '', '0000-00-00 00:00:00', 'pamv'),
(170, 'Christidis, N., Stott, P. A., Scaife, A. A., Arribas, A., Jones, G. S., Copsey, D., Knight, J. R. and W. J. Tennant', '2013', 'A New HadGEM3-A-Based System for Attribution of Weather- and Climate-Related Extreme Events', 'J. Climate, 26, 2756–2783', '', NULL, 'http://journals.ametsoc.org/doi/abs/10.1175/JCLI-D-12-00169.1', 'documentDigital', 'Christidis, N., Stott, P. A., Scaife, A. A., Arribas, A., Jones, G. S., Copsey, D., Knight, J. R. and W. J. Tennant (2013) A New HadGEM3-A-Based System for Attribution of Weather- and Climate-Related Extreme Events J. Climate, 26, 2756–2783', '', '0000-00-00 00:00:00', 'pamv'),
(171, 'Smith, S. J., Andres, R., Conception, E. and J. Lurz', '2004', 'Historical Sulfur Dioxide Emissions\r\n1850-2000: Methods and Results', 'PNNL Research Report 14537\r\n', '', NULL, 'http://www.osti.gov/bridge/purl.cover.jsp?purl=/15020102-hnrUiC/', 'documentDigital', 'Smith, S. J., Andres, R., Conception, E. and J. Lurz (2004) Historical Sulfur Dioxide Emissions\r\n1850-2000: Methods and Results PNNL Research Report 14537\r\n', '', '0000-00-00 00:00:00', 'pamv'),
(172, 'Mesinger, F.,', '1981', 'Horizontal Advection Schemes of a Staggered Grid - An Enstrophy and Energy-Conserving Model', 'Mon. Wea. Rev. 109, 467-478', '', '', ' http://dx.doi.org/10.1175/1520-0493(1981)109<0467:HASOAS>2.0.CO;2', 'documentDigital', 'Mesinger, F., (1981) Horizontal Advection Schemes of a Staggered Grid - An Enstrophy and Energy-Conserving Model Mon. Wea. Rev. 109, 467-478', '', '0000-00-00 00:00:00', 'pamv'),
(173, 'Collins, W., Stevenson, D. and C. Johnson', '1997', 'Tropospheric Ozone in a Global-Scale Three-Dimensional Lagrangian Model and Its Response to NOX Emission Controls', 'Journal of Atmospheric Chemistry 26: 223–274, 1997', '', NULL, 'http://rd.springer.com/article/10.1023/A%3A1005836531979#page-2', 'documentDigital', 'Collins, W., Stevenson, D. and C. Johnson (1997) Tropospheric Ozone in a Global-Scale Three-Dimensional Lagrangian Model and Its Response to NOX Emission Controls Journal of Atmospheric Chemistry 26: 223–274, 1997', '', '0000-00-00 00:00:00', 'pamv'),
(174, 'Smith, W. H. FR., and D. T. Sandwell', '1997', 'Global Sea Floor Topography from Satellite Altimetry and Ship Depth Soundings', 'Science, Vol 277, No 5334, 1956-1962 ', '', '', 'http://www.sciencemag.org/content/277/5334/1956.full', 'documentDigital', 'Smith, W. H. FR., and D. T. Sandwell (1997) Global Sea Floor Topography from Satellite Altimetry and Ship Depth Soundings Science, Vol 277, No 5334, 1956-1962 ', '', '0000-00-00 00:00:00', 'pamv'),
(175, 'Flato, G. M., and W. D. Hibler III', '1995', 'Ridging and strength in modeling the thickness distribution of Arctic sea ice', 'J. Geophys. Res., 100(C9), 18611–18626', '', '', 'http://onlinelibrary.wiley.com/doi/10.1029/95JC02091/full', 'documentDigital', 'Flato, G. M., and W. D. Hibler III (1995) Ridging and strength in modeling the thickness distribution of Arctic sea ice J. Geophys. Res., 100(C9), 18611–18626', '', '0000-00-00 00:00:00', 'pamv'),
(176, 'Hibler III, W. D., ', '1980', 'Modeling a variable thickness sea ice cover', 'Mon. Weather Rev., 108, 1943–1973', '', '', 'http://journals.ametsoc.org/doi/abs/10.1175/1520-0493%281980%29108%3C1943%3AMAVTSI%3E2.0.CO%3B2', 'documentDigital', 'Hibler III, W. D.,  (1980) Modeling a variable thickness sea ice cover Mon. Weather Rev., 108, 1943–1973', '', '0000-00-00 00:00:00', 'pamv'),
(177, 'Richards, L. A.', '1931', 'Capillary conduction of liquids in porous mediums', 'Physics, 1, 318–333', '', NULL, 'http://jap.aip.org/resource/1/japiau/v1/i5/p318_s1?isAuthorized=no', 'documentDigital', 'Richards, L. A. (1931) Capillary conduction of liquids in porous mediums Physics, 1, 318–333', '', '0000-00-00 00:00:00', 'pamv'),
(178, 'Clapp, R. B., and G. M. Hornberger', '1978', 'Empirical equations for some soil hydraulic properties', 'Water Resour. Res., 14(4), 601–604', '', NULL, 'doi:10.1029/WR014i004p00601', 'documentDigital', 'Clapp, R. B., and G. M. Hornberger (1978) Empirical equations for some soil hydraulic properties Water Resour. Res., 14(4), 601–604', '', '0000-00-00 00:00:00', 'pamv'),
(179, 'Neale, R. B. and B. J. Hoskins', '2000', 'A standard test for AGCMs including their physical parametrizations: I: the proposal', 'Atmosph. Sci. Lett., 1: 101–107. ', '', NULL, 'http://onlinelibrary.wiley.com/doi/10.1006/asle.2000.0022/abstract', 'documentDigital', 'Neale, R. B. and B. J. Hoskins (2000) A standard test for AGCMs including their physical parametrizations: I: the proposal Atmosph. Sci. Lett., 1: 101–107. ', '', '0000-00-00 00:00:00', 'pamv'),
(180, 'Warner, C. D. and M. E. McIntyre.', '1996', 'On the propagation and dissipation of gravity wave spectra through a realistic middle atmosphere.', 'J. Atmos. Sci., 53, 3213–3235.', '', '', 'http://dx.doi.org/10.1175/1520-0469(1996)053<3213:OTPADO>2.0.CO;2 ', 'documentDigital', 'Warner, C. D. and M. E. McIntyre. (1996) On the propagation and dissipation of gravity wave spectra through a realistic middle atmosphere.. J. Atmos. Sci., 53, 3213–3235.', '', '0000-00-00 00:00:00', 'pamv'),
(181, 'Warner, C. D. and M. E. McIntyre', '1999', ' Toward an ultra-simple spectral gravity wave parameterization for general circulation models. ', 'Earth Planets Space, Vol. 51 (Nos. 7, 8), pp. 475-484.', '', '', 'http://www.terrapub.co.jp/journals/EPS/abstract/5107_08/51070475.html', 'documentDigital', 'Warner, C. D. and M. E. McIntyre (1999)  Toward an ultra-simple spectral gravity wave parameterization for general circulation models.  Earth Planets Space, Vol. 51 (Nos. 7, 8), pp. 475-484.', '', '0000-00-00 00:00:00', 'pamv'),
(182, 'Scaife, A. A., N. Butchart, C. D. Warner and R. Swinbank', '2002', 'Impact of a spectral gravity wave parameterization on the stratosphere in the Met Office Unified Model.', ' J. Atmos. Sci., 59, 1473–1489.', '', '', ' http://dx.doi.org/10.1175/1520-0469(2002)059<1473:IOASGW>2.0.CO;2 ', 'documentDigital', 'Scaife, A. A., N. Butchart, C. D. Warner and R. Swinbank (2002) Impact of a spectral gravity wave parameterization on the stratosphere in the Met Office Unified Model.  J. Atmos. Sci., 59, 1473–1489.', '', '0000-00-00 00:00:00', 'pamv'),
(183, 'Scaife, A. A., N. Butchart, C. D. Warner, D. Stainforth, W. Norton and J. Austin.', '2002', 'Realistic quasi-biennial oscillations in a simulation of the global climate.', 'Geophysical Research Letters, 27, 21, 3481–3484,', '', '', 'http://onlinelibrary.wiley.com/doi/10.1029/2000GL011625/full', 'documentDigital', 'Scaife, A. A., N. Butchart, C. D. Warner, D. Stainforth, W. Norton and J. Austin. (2002) Realistic quasi-biennial oscillations in a simulation of the global climate. Geophysical Research Letters, 27, 21, 3481–3484,', '', '0000-00-00 00:00:00', 'pamv'),
(185, 'Jones R.G, M Noguer, D.C Hassell, D.A Hudson, S.S Wilson, G.J Jenkins and J.F.B Mitchell', '2004', 'Generating High Resolution Climate Change Scenarios using PRECIS', 'Met Office Hadley Centre, Exeter, UK, 40pp, April 2004. http;//www.metoffice.gov.uk/media/pdf/6/5/PRECIS_Handbook.pdf', '', '', '', 'documentDigital', 'Jones R.G, M Noguer, D.C Hassell, D.A Hudson, S.S Wilson, G.J Jenkins and J.F.B Mitchell (2004) Generating High Resolution Climate Change Scenarios using PRECIS Met Office Hadley Centre, Exeter, UK, 40pp, April 2004. http;//www.metoffice.gov.uk/media/pdf/6/5/PRECIS_Handbook.pdf', '', '0000-00-00 00:00:00', 'marke'),
(186, 'Walters, D. N., Williams, K. D., Boutle, I. A., Bushell, A. C., Edwards, J. M., Field, P. R., Lock, A. P., Morcrette, C. J., Stratton, R. A., Wilkinson, J. M., Willett, M. R., Bellouin, N., Bodas-Salcedo, A., Brooks, M. E., Copsey, D., Earnshaw, P. D., Hardiman, S. C., Harris, C. M., Levine, R. C., MacLachlan, C., Manners, J. C., Martin, G. M., Milton, S. F., Palmer, M. D., Roberts, M. J., Rodriguez, J. M., Tennant, W. J., and Vidale, P. L', '2013', 'The Met Office Unified Model Global Atmosphere 4.0 and JULES Global Land 4.0 configurations.', 'Geosci. Model Dev. Discuss., 6, 2813-2881, doi:10.5194/gmdd-6-2813-2013.', 'doi:10.5194/gmdd-6-2813-2013', '', '', 'documentHardcopy', 'Walters, D. N., Williams, K. D., Boutle, I. A., Bushell, A. C., Edwards, J. M., Field, P. R., Lock, A. P., Morcrette, C. J., Stratton, R. A., Wilkinson, J. M., Willett, M. R., Bellouin, N., Bodas-Salcedo, A., Brooks, M. E., Copsey, D., Earnshaw, P. D., Hardiman, S. C., Harris, C. M., Levine, R. C., MacLachlan, C., Manners, J. C., Martin, G. M., Milton, S. F., Palmer, M. D., Roberts, M. J., Rodriguez, J. M., Tennant, W. J., and Vidale, P. L (2013) The Met Office Unified Model Global Atmosphere 4.0 and JULES Global Land 4.0 configurations.. Geosci. Model Dev. Discuss., 6, 2813-2881, doi:10.5194/gmdd-6-2813-2013.', '', '0000-00-00 00:00:00', 'marke'),
(187, 'Best, M. J., Pryor, M., Clark, D. B., Rooney, G. G., Essery, R. L. H., Menard, C. B., Edwards, J. M., Hendry, M. A., Gedney, N., Mercado, L. M., Sitch, S., Blyth, E., Boucher, O., Cox, P. M., Grimmond, C. S. B., and R. J. Harding', '2011', 'The Joint UK Land Environment Simulator (JULES), model\r\ndescription Part 1: Energy and water fluxes', 'Geosci. Model Dev., 4, 677-699', '', NULL, 'www.geosci-model-dev.net/4/677/2011/', 'documentDigital', 'Best, M. J., Pryor, M., Clark, D. B., Rooney, G. G., Essery, R. L. H., Menard, C. B., Edwards, J. M., Hendry, M. A., Gedney, N., Mercado, L. M., Sitch, S., Blyth, E., Boucher, O., Cox, P. M., Grimmond, C. S. B., and R. J. Harding (2011) The Joint UK Land Environment Simulator (JULES), model\r\ndescription – Part 1: Energy and water fluxes Geosci. Model Dev., 4, 677–\r\n699', '', '0000-00-00 00:00:00', 'pamv'),
(188, 'Clark, D. B., Mercado, L. M., Sitch, S., Jones, C. D., Gedney, N., Best, M. J., Pryor, M., Rooney, G. G., Essery, R. L. H., Blyth, E., Boucher, O., Harding, R. J., Huntingford, C., and Cox, P. M', '2011', 'The Joint UK Land Environment Simulator (JULES), model description – Part 2: Carbon fluxes and vegetation dynamics', 'Geosci. Model Dev., 4, 701-722', '', NULL, 'http://www.geosci-model-dev.net/4/701/2011/gmd-4-701-2011.html', 'documentDigital', 'Clark, D. B., Mercado, L. M., Sitch, S., Jones, C. D., Gedney, N., Best, M. J., Pryor, M., Rooney, G. G., Essery, R. L. H., Blyth, E., Boucher, O., Harding, R. J., Huntingford, C., and Cox, P. M (2011) The Joint UK Land Environment Simulator (JULES), model description – Part 2: Carbon fluxes and vegetation dynamics Geosci. Model Dev., 4, 701-722', '', '0000-00-00 00:00:00', 'pamv'),
(189, 'Madec, G.', '2008', 'NEMO ocean engine ', 'Note du Pole de modélisation, Institut Pierre-Simon Laplace (IPSL), France, No 27 ISSN No 1288-1619', '', '', 'http://www.nemo-ocean.eu/About-NEMO/Reference-manuals', 'internal report', 'Madec G. (2008) NEMO ocean engine  Note du Pole de modélisation, Institut Pierre-Simon Laplace (IPSL), France, No 27 ISSN No 1288-1619', '', '2017-02-07 09:58:54', 'pamv'),
(190, 'Vancoppenolle M., Bouillon S., Fichefet T., Goosse H., Lecomte O., Morales Maqueda M.A., and G. Madec', '2012', 'LIM The Louvain-la-Neuve sea Ice Model', 'Note du Pole de modélisation, Institut Pierre-Simon Laplace (IPSL), France, No 31 ISSN No 1288-1619', '', NULL, 'http://www.nemo-ocean.eu/About-NEMO/Reference-manuals', 'documentDigital', 'Vancoppenolle M., Bouillon S., Fichefet T., Goosse H., Lecomte O., Morales Maqueda M.A., and G. Madec (2012) LIM The Louvain-la-Neuve sea Ice Model Note du Pole de modélisation, Institut Pierre-Simon Laplace (IPSL), France, No 31 ISSN No 1288-1619', '', '0000-00-00 00:00:00', 'pamv'),
(191, 'Hardiman, Steven; Butchart, Neal; Hinton, Tim; Osprey, Scott; Gray, Lesley; Jones, Chris; Hughes, John ', '2014', 'HadGEM2-CC model output prepared for CMIP5 piControl, served by ESGF.', 'WDCC at DKRZ. doi: 10.1594/WDCC/CMIP5.MOGCpc', 'doi: 10.1594/WDCC/CMIP5.MOGCpc', '', '', 'documentDigital', 'Hardiman, Steven; Butchart, Neal; Hinton, Tim; Osprey, Scott; Gray, Lesley; Jones, Chris; Hughes, John  (2014) HadGEM2-CC model output prepared for CMIP5 piControl, served by ESGF.. WDCC at DKRZ. doi: 10.1594/WDCC/CMIP5.MOGCpc', '', '0000-00-00 00:00:00', 'pamv'),
(192, 'Hardiman,Steven; Butchart,Neal; Hinton,Tim; Osprey,Scott; Gray,Lesley; Jones,Chris; Hughes,John', '2014', 'HadGEM2-CC model output prepared for CMIP5 historical, served by ESGF.', 'WDCC at DKRZ. doi:10.1594/WDCC/CMIP5.MOGChi', 'doi:10.1594/WDCC/CMIP5.MOGChi', '', '', 'documentDigital', 'Hardiman,Steven; Butchart,Neal; Hinton,Tim; Osprey,Scott; Gray,Lesley; Jones,Chris; Hughes,John (2014) HadGEM2-CC model output prepared for CMIP5 historical, served by ESGF.. WDCC at DKRZ. doi:10.1594/WDCC/CMIP5.MOGChi', '', '0000-00-00 00:00:00', 'pamv'),
(193, 'Hardiman,Steven; Butchart,Neal; Hinton,Tim; Osprey,Scott; Gray,Lesley; Jones,Chris; Hughes,John ', '2014', 'HadGEM2-CC model output prepared for CMIP5 RCP8.5, served by ESGF', 'WDCC at DKRZ. doi:10.1594/WDCC/CMIP5.MOGCr8', 'doi:10.1594/WDCC/CMIP5.MOGCr8', '', '', 'documentDigital', 'Hardiman,Steven; Butchart,Neal; Hinton,Tim; Osprey,Scott; Gray,Lesley; Jones,Chris; Hughes,John  (2014) HadGEM2-CC model output prepared for CMIP5 RCP8.5, served by ESGF. WDCC at DKRZ. doi:10.1594/WDCC/CMIP5.MOGCr8', '', '0000-00-00 00:00:00', 'pamv'),
(194, 'Hardiman,Steven; Butchart,Neal; Hinton,Tim; Osprey,Scott; Gray,Lesley; Jones,Chris; Hughes,John ', '2014', 'HadGEM2-CC model output prepared for CMIP5 RCP4.5, served by ESGF. ', 'WDCC at DKRZ. doi:10.1594/WDCC/CMIP5.MOGCr4', 'doi:10.1594/WDCC/CMIP5.MOGCr4', '', '<enter URL for paper link>', 'documentDigital', 'Hardiman,Steven; Butchart,Neal; Hinton,Tim; Osprey,Scott; Gray,Lesley; Jones,Chris; Hughes,John  (2014) HadGEM2-CC model output prepared for CMIP5 RCP4.5, served by ESGF.  WDCC at DKRZ. doi:10.1594/WDCC/CMIP5.MOGCr4', '', '0000-00-00 00:00:00', 'pamv'),
(195, 'Smith, Doug; Pohlmann, Holger; Eade, Rosie', '2014', 'HadCM3 model output prepared for CMIP5 decadal experiments, served by ESGF. ', 'WDCC at DKRZ. doi:10.1594/WDCC/CMIP5.MOC3DEC\r\n', 'doi:10.1594/WDCC/CMIP5.MOC3DEC', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOC3DEC', 'documentDigital', 'Smith, Doug; Pohlmann, Holger; Eade, Rosie (2014) HadCM3 model output prepared for CMIP5 decadal experiments, served by ESGF. . WDCC at DKRZ. doi:10.1594/WDCC/CMIP5.MOC3DEC\r\n', '', '0000-00-00 00:00:00', 'pamv'),
(196, 'Smith, Doug; Pohlmann, Holger; Eade, Rosie \r\n\r\n', '2014', 'HadCM3 model output prepared for CMIP5 historical, served by ESGF. ', 'WDCC at DKRZ.\r doi:10.1594/WDCC/CMIP5.MOC3hi', 'doi:10.1594/WDCC/CMIP5.MOC3hi', NULL, 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOC3hi', 'documentDigital', 'Smith, Doug; Pohlmann, Holger; Eade, Rosie \r\n\r\n (2014) HadCM3 model output prepared for CMIP5 historical, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOC3hi', '', '0000-00-00 00:00:00', 'pamv'),
(197, 'Smith, Doug; Pohlmann, Holger; Eade, Rosie', '2014', 'HadCM3 model output prepared for CMIP5 RCP4.5, served by ESGF. \r\n', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOC3r4', 'doi: 10.1594/WDCC/CMIP5.MOC3r4', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOC3r4', 'documentDigital', 'Smith, Doug; Pohlmann, Holger; Eade, Rosie (2014) HadCM3 model output prepared for CMIP5 RCP4.5, served by ESGF. \r\n WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOC3r4', '', '0000-00-00 00:00:00', 'pamv'),
(198, 'Jones, Chris; Hughes, John; Jones, Gareth; Christidis, Nikos; Lott, Fraser; Sellar, Alistair; Webb, Mark; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Martin, Gill', '2014', 'HadGEM2-A model output prepared for CMIP5 amip, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAam', 'doi: 10.1594/WDCC/CMIP5.MOGAam', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGAam', 'documentDigital', 'Jones, Chris; Hughes, John; Jones, Gareth; Christidis, Nikos; Lott, Fraser; Sellar, Alistair; Webb, Mark; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Martin, Gill (2014) HadGEM2-A model output prepared for CMIP5 amip, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAam', '', '0000-00-00 00:00:00', 'pamv'),
(199, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris', '2014', 'HadGEM2-A model output prepared for CMIP5 sstClim, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAsc', 'doi: 10.1594/WDCC/CMIP5.MOGAsc', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGAsc', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014) HadGEM2-A model output prepared for CMIP5 sstClim, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAsc', '', '0000-00-00 00:00:00', 'pamv'),
(200, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014): ', '2014', 'HadGEM2-A model output prepared for CMIP5 sstClim4xCO2, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAs2 at ', 'doi: 10.1594/WDCC/CMIP5.MOGAs2', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGAs2', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014):  (2014) HadGEM2-A model output prepared for CMIP5 sstClim4xCO2, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAs2 at ', '', '0000-00-00 00:00:00', 'pamv'),
(201, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris', '2014', ' HadGEM2-A model output prepared for CMIP5 sstClimAerosol, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAsa', 'doi: 10.1594/WDCC/CMIP5.MOGAsa', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGAsa', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014)  HadGEM2-A model output prepared for CMIP5 sstClimAerosol, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAsa', '', '0000-00-00 00:00:00', 'pamv'),
(202, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris ', '2014', 'HadGEM2-A model output prepared for CMIP5 amip4xCO2, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAa2', 'doi: 10.1594/WDCC/CMIP5.MOGAa2', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGAa2', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris  (2014) HadGEM2-A model output prepared for CMIP5 amip4xCO2, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAa2', '', '0000-00-00 00:00:00', 'pamv'),
(203, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris', '2014', 'HadGEM2-A model output prepared for CMIP5 sstClimSulfate, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAss ', 'doi: 10.1594/WDCC/CMIP5.MOGAss', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGAss', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014) HadGEM2-A model output prepared for CMIP5 sstClimSulfate, served by ESGF. . WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAss ', '', '0000-00-00 00:00:00', 'pamv'),
(210, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris', '2014', 'HadGEM2-ES model output prepared for CMIP5 1pctCO2, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEc1', 'doi: 10.1594/WDCC/CMIP5.MOGEc1', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEc1', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014) HadGEM2-ES model output prepared for CMIP5 1pctCO2, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEc1', '', '0000-00-00 00:00:00', 'pamv'),
(204, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris', '2014', 'HadGEM2-A model output prepared for CMIP5 amip4xCO2, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAa2', 'doi: 10.1594/WDCC/CMIP5.MOGAa2', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGAa2', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014) HadGEM2-A model output prepared for CMIP5 amip4xCO2, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAa2', '', '0000-00-00 00:00:00', 'pamv'),
(205, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris', '2014', 'HadGEM2-A model output prepared for CMIP5 amipFuture, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAaf', 'doi: 10.1594/WDCC/CMIP5.MOGAaf ', '', ' http://dx.doi.org/10.1594/WDCC/CMIP5.MOGAaf ', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014) HadGEM2-A model output prepared for CMIP5 amipFuture, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAaf', '', '0000-00-00 00:00:00', 'pamv');
INSERT INTO `ut_reference` (`id`, `authors`, `date`, `title`, `detail`, `doi`, `abstract`, `weblink`, `format`, `reference`, `cim_id`, `upd_date`, `upd_by`) VALUES
(206, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris', '2014', 'HadGEM2-A model output prepared for CMIP5 aquaControl, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAqc', 'doi: 10.1594/WDCC/CMIP5.MOGAqc', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGAqc', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014) HadGEM2-A model output prepared for CMIP5 aquaControl, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAqc', '', '0000-00-00 00:00:00', 'pamv'),
(207, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris', '2014', ' HadGEM2-A model output prepared for CMIP5 aqua4xCO2, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAq2', 'doi: 10.1594/WDCC/CMIP5.MOGAq2', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGAq2', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014)  HadGEM2-A model output prepared for CMIP5 aqua4xCO2, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAq2', '', '0000-00-00 00:00:00', 'pamv'),
(208, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris', '2014', 'HadGEM2-A model output prepared for CMIP5 aqua4K, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAq4', 'doi: 10.1594/WDCC/CMIP5.MOGAq4', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGAq4', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014) HadGEM2-A model output prepared for CMIP5 aqua4K, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAq4', '', '0000-00-00 00:00:00', 'pamv'),
(209, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris', '2014', 'HadGEM2-A model output prepared for CMIP5 amip4K, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAa4', 'doi:10.1594/WDCC/CMIP5.MOGAa4', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGAa4', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014) HadGEM2-A model output prepared for CMIP5 amip4K, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGAa4', '', '0000-00-00 00:00:00', 'pamv'),
(211, 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris', '2014', 'HadGEM2-ES model output prepared for CMIP5 abrupt4xCO2, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEc2', 'doi:10.1594/WDCC/CMIP5.MOGEc2', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEc2', 'documentDigital', 'Webb, Mark; Williams, Jonny; Andrews, Tim; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Hughes, John; Jones, Chris (2014) HadGEM2-ES model output prepared for CMIP5 abrupt4xCO2, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEc2', '', '0000-00-00 00:00:00', 'pamv'),
(212, 'Jones, Gareth; Christidis, Nikos; Lott, Fraser; Hughes, John; Jones, Chris', '2014', 'HadGEM2-ES model output prepared for CMIP5 historicalNat, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEhn', 'doi:10.1594/WDCC/CMIP5.MOGEhn', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEhn', 'documentDigital', 'Jones, Gareth; Christidis, Nikos; Lott, Fraser; Hughes, John; Jones, Chris (2014) HadGEM2-ES model output prepared for CMIP5 historicalNat, served by ESGF. . WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEhn', '', '0000-00-00 00:00:00', 'pamv'),
(213, 'Jones, Gareth; Christidis, Nikos; Lott, Fraser; Hughes, John; Jones, Chris', '2014', 'HadGEM2-ES model output prepared for CMIP5 historicalGHG, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEhg', 'doi:10.1594/WDCC/CMIP5.MOGEhg', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEhg', 'documentDigital', 'Jones, Gareth; Christidis, Nikos; Lott, Fraser; Hughes, John; Jones, Chris (2014) HadGEM2-ES model output prepared for CMIP5 historicalGHG, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEhg', '', '0000-00-00 00:00:00', 'pamv'),
(214, 'Jones, Gareth; Christidis, Nikos; Lott, Fraser; Hughes, John; Jones, Chris', '2014', 'HadGEM2-ES model output prepared for CMIP5 historicalExt, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEhx', 'doi:10.1594/WDCC/CMIP5.MOGEhx', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEhx', 'documentDigital', 'Jones, Gareth; Christidis, Nikos; Lott, Fraser; Hughes, John; Jones, Chris (2014) HadGEM2-ES model output prepared for CMIP5 historicalExt, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEhx', '', '0000-00-00 00:00:00', 'pamv'),
(215, 'Marzin, Charline; Kahana, Ron; Jones, Chris', '2014', 'HadGEM2-CC model output prepared for CMIP5 midHolocene, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGCmh', 'doi:10.1594/WDCC/CMIP5.MOGCmh', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGCmh', 'documentDigital', 'Marzin, Charline; Kahana, Ron; Jones, Chris (2014) HadGEM2-CC model output prepared for CMIP5 midHolocene, served by ESGF.. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGCmh', '', '0000-00-00 00:00:00', 'pamv'),
(216, 'Marzin, Charline; Kahana, Ron; Jones, Chris', '2014', 'HadGEM2-ES model output prepared for CMIP5 midHolocene, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEmh', 'doi:10.1594/WDCC/CMIP5.MOGEmh', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEmh', 'documentDigital', 'Marzin, Charline; Kahana, Ron; Jones, Chris (2014) HadGEM2-ES model output prepared for CMIP5 midHolocene, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEmh', '', '0000-00-00 00:00:00', 'pamv'),
(217, 'Sanderson, Michael; Hughes, John; Jones, Chris', '2014', 'HadGEM2-ES model output prepared for CMIP5 RCP4.5, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEr4', 'doi:10.1594/WDCC/CMIP5.MOGEr4', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEr4', 'documentDigital', 'Sanderson, Michael; Hughes, John; Jones, Chris (2014) HadGEM2-ES model output prepared for CMIP5 RCP4.5, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEr4', '', '0000-00-00 00:00:00', 'pamv'),
(218, 'Sanderson, Michael; Hughes, John; Jones, Chris', '2014', 'HadGEM2-ES model output prepared for CMIP5 RCP8.5, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEr8', 'doi:10.1594/WDCC/CMIP5.MOGEr8', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEr8', 'documentDigital', 'Sanderson, Michael; Hughes, John; Jones, Chris (2014) HadGEM2-ES model output prepared for CMIP5 RCP8.5, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEr8', '', '0000-00-00 00:00:00', 'pamv'),
(219, 'Sanderson, Michael; Hughes, John; Jones, Chris', '2014', 'HadGEM2-ES model output prepared for CMIP5 RCP2.6, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEr2', 'doi:10.1594/WDCC/CMIP5.MOGEr2', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEr2', 'documentDigital', 'Sanderson, Michael; Hughes, John; Jones, Chris (2014) HadGEM2-ES model output prepared for CMIP5 RCP2.6, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEr2', '', '0000-00-00 00:00:00', 'pamv'),
(220, 'Sanderson, Michael; Hughes, John; Jones, Chris', '2014', 'HadGEM2-ES model output prepared for CMIP5 RCP6, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEr6', 'doi:10.1594/WDCC/CMIP5.MOGEr6', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEr6', 'documentDigital', 'Sanderson, Michael; Hughes, John; Jones, Chris (2014) HadGEM2-ES model output prepared for CMIP5 RCP6, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEr6', '', '0000-00-00 00:00:00', 'pamv'),
(221, 'Jones, Chris; Hughes, John; Jones, Gareth; Christidis, Nikos; Lott, Fraser; Sellar, Alistair; Webb, Mark; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Martin, Gill', '2014', 'HadGEM2-ES model output prepared for CMIP5 piControl, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEpc', 'doi: /10.1594/WDCC/CMIP5.MOGEpc', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEpc', 'documentDigital', 'Jones, Chris; Hughes, John; Jones, Gareth; Christidis, Nikos; Lott, Fraser; Sellar, Alistair; Webb, Mark; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Martin, Gill (2014) HadGEM2-ES model output prepared for CMIP5 piControl, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEpc', '', '0000-00-00 00:00:00', 'pamv'),
(222, 'Jones, Chris; Hughes, John; Jones, Gareth; Christidis, Nikos; Lott, Fraser; Sellar, Alistair; Webb, Mark; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Martin, Gill', '2014', 'HadGEM2-ES model output prepared for CMIP5 historical, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEhi', 'doi: 10.1594/WDCC/CMIP5.MOGEhi', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEhi', 'documentDigital', 'Jones, Chris; Hughes, John; Jones, Gareth; Christidis, Nikos; Lott, Fraser; Sellar, Alistair; Webb, Mark; Bodas-Salcedo, Alejandro; Tsushima, Yoko; Martin, Gill (2014) HadGEM2-ES model output prepared for CMIP5 historical, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEhi', '', '0000-00-00 00:00:00', 'pamv'),
(223, 'Liddicoat, Spencer; Jones, Chris; Hughes, John', '2014', 'HadGEM2-ES model output prepared for CMIP5 esmControl, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEec<publication details>', 'doi: 10.1594/WDCC/CMIP5.MOGEec', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEec', 'documentDigital', 'Liddicoat, Spencer; Jones, Chris; Hughes, John (2014) HadGEM2-ES model output prepared for CMIP5 esmControl, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEec<publication details>', '', '0000-00-00 00:00:00', 'pamv'),
(224, 'Liddicoat, Spencer; Jones, Chris; Hughes, John', '2014', 'HadGEM2-ES model output prepared for CMIP5 esmHistorical, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEeh', 'doi: 10.1594/WDCC/CMIP5.MOGEeh', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEeh', 'documentDigital', 'Liddicoat, Spencer; Jones, Chris; Hughes, John (2014) HadGEM2-ES model output prepared for CMIP5 esmHistorical, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEeh', '', '0000-00-00 00:00:00', 'pamv'),
(225, 'Liddicoat, Spencer; Jones, Chris; Hughes, John', '2014', 'HadGEM2-ES model output prepared for CMIP5 esmrcp85, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEe8', 'doi: 10.1594/WDCC/CMIP5.MOGEe8', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEe8', 'documentDigital', 'Liddicoat, Spencer; Jones, Chris; Hughes, John (2014) HadGEM2-ES model output prepared for CMIP5 esmrcp85, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEe8', '', '0000-00-00 00:00:00', 'pamv'),
(226, 'Liddicoat, Spencer; Jones, Chris; Hughes, John', '2014', 'HadGEM2-ES model output prepared for CMIP5 esmFixClim1, served by ESGF. ', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEx1', 'doi: 10.1594/WDCC/CMIP5.MOGEx1', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEx1', 'documentDigital', 'Liddicoat, Spencer; Jones, Chris; Hughes, John (2014) HadGEM2-ES model output prepared for CMIP5 esmFixClim1, served by ESGF.  WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEx1', '', '0000-00-00 00:00:00', 'pamv'),
(227, 'Liddicoat, Spencer; Jones, Chris; Hughes, John', '2014', 'HadGEM2-ES model output prepared for CMIP5 esmFixClim2, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEx2', 'doi: 10.1594/WDCC/CMIP5.MOGEx2', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEx2', 'documentDigital', 'Liddicoat, Spencer; Jones, Chris; Hughes, John (2014) HadGEM2-ES model output prepared for CMIP5 esmFixClim2, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEx2', '', '0000-00-00 00:00:00', 'pamv'),
(228, 'Liddicoat, Spencer; Jones, Chris; Hughes, John', '2014', 'HadGEM2-ES model output prepared for CMIP5 esmFdbk1, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEe1', 'doi: 10.1594/WDCC/CMIP5.MOGEe1', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEe1', 'documentDigital', 'Liddicoat, Spencer; Jones, Chris; Hughes, John (2014) HadGEM2-ES model output prepared for CMIP5 esmFdbk1, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEe1', '', '0000-00-00 00:00:00', 'pamv'),
(229, 'Liddicoat, Spencer; Jones, Chris; Hughes, John', '2014', 'HadGEM2-ES model output prepared for CMIP5 esmFdbk2, served by ESGF.', 'WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEe2', 'doi: 10.1594/WDCC/CMIP5.MOGEe2', '', 'http://dx.doi.org/10.1594/WDCC/CMIP5.MOGEe2', 'documentDigital', 'Liddicoat, Spencer; Jones, Chris; Hughes, John (2014) HadGEM2-ES model output prepared for CMIP5 esmFdbk2, served by ESGF. WDCC at DKRZ.\r\ndoi:10.1594/WDCC/CMIP5.MOGEe2', '', '0000-00-00 00:00:00', 'pamv'),
(230, 'W. Moufouma-Okia and \r\nR. Jones ', '2015', 'Resolution dependence in simulating the African hydroclimate with the HadGEM3-RA regional climate model', 'Climate Dynamics, Volume 44, Issue 3-4, pp 609-632, February 2015', 'doi:10.1007/s00382-014-2322-2', '1432-0894', 'link.springer.com/article/10.1007%2Fs00382-014-2322-2', 'documentHardcopy', 'W. Moufouma-Okia and \r\nR. Jones  (2015) Resolution dependence in simulating the African hydroclimate with the HadGEM3-RA regional climate model Climate Dynamics, Volume 44, Issue 3-4, pp 609-632, February 2015', '', '0000-00-00 00:00:00', 'marke'),
(10000, 'Barnier, B., Madec, G., Penduff, T., Molines, J.-M., Treguier, A.-M., Le Sommer, J., Beckmann, A., Biastoch, A., Böning, C., Dengg, J., Derval, C., Durand, E., Gulev, S., Remy, E., Talandier, C., Theetten, S., Maltrud, M., McClean, J., and De Cuevas, B.\r\n', '2006', 'Impact of partial steps and momentum advection schemes in a global ocean circulation model at eddy-permitting resolution.', 'Ocean Dynamics, 56, 543–567.', 'http://dx.doi.org/10.1007/s10236-006-0082-1', '', 'http://archimer.ifremer.fr/doc/2006/publication-3514.pdf', 'peer reviewed article', NULL, '', '2017-02-07 09:49:04', 'pamv'),
(10002, 'Arakawa, A. and Lamb, V. R.', '1981', 'A Potential Enstrophy and Energy Conserving Scheme for the Shallow Water Equations', 'Monthly Weather Review, 109, 18–36', 'http://dx.doi.org/10.1175/1520-0493(1981)109 ', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:03:04', 'pamv'),
(10003, 'Hollingsworth, A., Kallberg, P., Renner, V., and Burridge, D. M.', '1983', 'An internal symmetric computational instability,\r\n', 'Quarterly Journal of the Royal Meteorological Society, 109, 417–428', ' http://dx.doi.org/10.1002/qj.49710946012', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:04:38', 'pamv'),
(10004, 'Zalesak, S. T.\r\n', '1979', 'Fully multidimensional flux corrected transport algorithms for fluids', 'J. Comput. Phys., 31, 335–362', '', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:06:15', 'pamv'),
(10005, 'Axell, L. B.\r\n', '2002', 'Wind-driven Internal Waves and Langmuir Circulations in a Numerical Ocean Model of the Southern Baltic Sea', 'J. Geophys. Res., 107. 3204', 'doi:10.1029/2001JC000922, 2002.', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:10:22', 'pamv'),
(10006, 'Craig, P. D. and Banner, M. L.', '1994', 'Layer Modelling Wave-Enhanced Turbulence in the Ocean Surface', 'J. Phys. Oceanogr., 24, 2546–2559', '', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:11:43', 'pamv'),
(10007, 'Gaspar, P., Grégoris, Y., and Lefevre, J.-M.', '1990', 'A simple eddy kinetic energy model for simulations of the oceanic vertical mixing: tests at Station Papa and long-term upper ocean study site', ' J. Geophys. Res., 95, 16179–16193', 'doi:10.1029/JC095iC09p16179', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:13:05', 'pamv'),
(10008, 'Gregg, M. C., Sanford, T. B., and Winkel, D. P.', '2003', 'Reduced mixing from the breaking of internal waves in equatorial waters', 'Nature, 422, 513–515', '', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:15:51', 'pamv'),
(10009, 'Koch-Larrouy, A., Madec, G., Blanke, B., and Molcard, R.', '2008', 'Water mass transformation along the Indonesian throughflow in an OGCM', 'Ocean Dynam., 58, 289–309', '', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:17:09', 'pamv'),
(10010, 'Merryfield, W. J., Holloway, G., and Gargett, A. E.', '1999', 'A global ocean model with double-diffusive mixing', 'J. Phys. Ocean., 29, 1124–1142', '', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:18:19', 'pamv'),
(10011, 'Rodgers, K. B., Aumont, O., Mikaloff Fletcher, S. E., Plancherel, Y., Bopp, L., de Boyer Montégut, C., Iudicone, D., Keeling, R. F., Madec, G., and Wanninkhof, R.', '2014', 'Strong sensitivity of Southern Ocean carbon uptake and nutrient cycling to wind stirring', 'Biogeosciences, 11, 4077–4098', 'http://www.biogeosciences.net/11/4077/2014', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:19:38', 'pamv'),
(10012, 'Simmons, H., Jayne, S., Laurent, L. S., and Weaver, A.\r\n', '2004', 'Tidally driven mixing in a numerical model of the ocean general circulation', 'Ocean Model., 6, 245–263', '', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:20:47', 'pamv'),
(10013, 'Adcroft, A. and Campin, J.-M.', '2004', 'Rescaled height coordinates for accurate representation of free-surface flows in ocean circulation models', 'Ocean Modelling, 7, 269 – 284', 'http://www.sciencedirect.com/science/article/', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:22:40', 'pamv'),
(10014, 'Beckmann, A. and Doscher, R.', '1997', 'A method for improved representation of dense water spreading over topography in geopotential-coordinate models', 'J. Phys. Oceanogr., 27, 581–591', '', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:24:30', 'pamv'),
(10015, 'Roullet, G. and Madec, G.', '2000', 'Salt conservation, free surface, and varying levels: A new formulation for ocean general circulation models', 'Journal of Geophysical Research: Oceans, 105, 23 927–23 942', 'http://dx.doi.org/10.1029/2000JC900089', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:25:59', 'pamv'),
(10016, 'Bigg, G. R., Wadley, M. R., Stevens, D. P., and Johnson, J. A.', '1997', 'Modelling dynamics and thermodynamics of icebergs', 'Cold Regions Science and Technology, 26, 113–135', '', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:27:03', 'pamv'),
(10017, 'Marsh, R., Ivchenko, V. O., Skliris, N., Alderson, S., Bigg, G. R., Madec, G., Blaker, A. T., Aksenov, Y., Sinha, B., Coward, A. C., Le Sommer, J., Merino, I., and Zalesny, V.', '2015', 'NEMO–ICB (v1.0): interactive icebergs in the NEMO ocean model globally configured at eddy-permitting resolution', 'Geoscientific Model Development, 8, 1547–1562', 'https://hal-insu.archives-ouvertes.fr/insu-01', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:28:34', 'pamv'),
(10018, 'Martin, T. and Adcroft, A.', '2010', 'Parameterizing the fresh-water flux from land ice to ocean with interactive icebergs in a coupled climate model', 'Ocean Modelling, 34, 111 – 124', 'http://www.sciencedirect.com/science/article/', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:29:57', 'pamv'),
(10019, 'Stein, C. A. and Stein, S.', '1992', 'A model for the global variation in oceanic depth and heat flow with lithospheric age', 'Nature, 359, 123–129', '', '', '', 'peer reviewed article', NULL, '', '2017-02-11 14:30:55', 'pamv'),
(10020, 'Goutorbe, B., J. Poort, F. Lucazeau, and S. Raillard', '2011', 'Global heat flow trends resolved from multiple\r\ngeological and geophysical proxies, ', 'Geophys. J. Int., 187, 1405–1419.', '', '', '', 'peer reviewed article', NULL, '', '2017-03-05 16:54:14', 'pamv'),
(10021, 'IOC, IHO and BODC', '2008', 'Centenary Edition of the GEBCO Digital Atlas', 'Published on CD-ROM on behalf of the Intergovernmental Oceanographic Commission and the International Hydrographic Organization as part of the General Bathymetric Chart of the Oceans, British Oceanogr', '', '', '', 'other', NULL, '', '2017-03-06 09:28:29', 'pamv'),
(10022, 'Mathiot, P., Jenkins, A., Harris, C., and Madec, G.', '2017', 'Different ways to represent ice shelf melting in a z* coordinate ocean model', 'Geoscientific Model Development', '', '', '', 'peer reviewed article', NULL, '', '2017-03-06 09:32:30', 'pamv'),
(10023, 'Lengaigne, M., Menkes, C., Aumont, O., Gorgues, T., Bopp, L., André, J.-M. and Madec, G.', '2007', 'Influence of the oceanic biology on the tropical Pacific climate in a coupled general circulation model', 'Climate Dynamics, 28(5), 503-516.', '', '', '', 'peer reviewed article', NULL, '', '2017-03-06 09:33:31', 'pamv');

-- --------------------------------------------------------

--
-- Table structure for table `ut_referencelist`
--

CREATE TABLE IF NOT EXISTS `ut_referencelist` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id for the link',
  `o_id` int(11) NOT NULL COMMENT 'id for object in object table',
  `o_type` varchar(40) NOT NULL COMMENT 'type of object',
  `o_name` varchar(60) DEFAULT NULL COMMENT 'name of object',
  `referenceid` int(11) NOT NULL COMMENT 'id for reference record',
  `purpose` varchar(30) DEFAULT NULL COMMENT 'purpose of reference (code list)',
  `reference` varchar(1000) DEFAULT NULL COMMENT 'citation for reference',
  `upd_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` char(20) NOT NULL COMMENT 'person/process responsible for last update',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='link table for references and other entities';

--
-- Dumping data for table `ut_referencelist`
--

INSERT INTO `ut_referencelist` (`id`, `o_id`, `o_type`, `o_name`, `referenceid`, `purpose`, `reference`, `upd_date`, `upd_by`) VALUES
(10000, 10001, 'MODEL', 'NEMO', 10000, 'reference', '	 Barnier, B., Madec, G., Penduff, T., Molines, J.-M., Treguier, A.-M., Le Sommer, J., Beckmann, A., Biastoch, A., Böning, C., Dengg, J., Derval, C., Durand, E., Gulev, S., Remy, E., Talandier, C., Theetten, S., Maltrud, M., McClean, J., and De Cuevas, B.\r\n [2006]: <br>\r\n	 <span style="color: darkred; font-weight: bold">Impact of partial steps and momentum advection schemes in a global ocean circulation model at eddy-permitting resolution.. </span><br>\r\n	 http://dx.doi.org/10.1007/s10236-006-0082-1 <a href="" target="_blank"></a>', '2017-02-07 09:49:04', 'pamv'),
(10001, 10001, 'MODEL', 'NEMO', 189, 'reference', '	     Madec, G. [2008]: <br>\r\n		 <span style="color: darkred; font-weight: bold">NEMO ocean engine . </span>Note du Pole de modélisation, Institut Pierre-Simon Laplace (IPSL), France, No 27 ISSN No 1288-1619<br>\r\n		  ', '2017-02-07 10:01:42', 'pamv'),
(10002, 2, 'TOPIC', 'Advection', 10002, 'reference', '      Arakawa, A. and Lamb, V. R. [1981]: <br>\r\n      <span style="color: darkred;">A Potential Enstrophy and Energy Conserving Scheme for the Shallow Water Equations</span><br>\r\n      Monthly Weather Review, 109, 18–36 http://dx.doi.org/10.1175/1520-0493(1981)109  ', '2017-03-06 08:42:13', 'pamv'),
(10003, 2, 'TOPIC', 'Advection', 10003, 'reference', '      Hollingsworth, A., Kallberg, P., Renner, V., and Burridge, D. M. [1983]: <br>\r\n      <span style="color: darkred;">An internal symmetric computational instability,\r\n</span><br>\r\n      Quarterly Journal of the Royal Meteorological Society, 109, 417–428  http://dx.doi.org/10.1002/qj.49710946012 ', '2017-03-06 08:43:31', 'pamv'),
(10004, 2, 'TOPIC', 'Advection', 10004, 'reference', '      Zalesak, S. T.\r\n [1979]: <br>\r\n      <span style="color: darkred;">Fully multidimensional flux corrected transport algorithms for fluids</span><br>\r\n      J. Comput. Phys., 31, 335–362  ', '2017-03-06 08:44:02', 'pamv'),
(10005, 3, 'TOPIC', 'Momentum', 10002, 'reference', '      Arakawa, A. and Lamb, V. R. [1981]: <br>\r\n      <span style="color: darkred;">A Potential Enstrophy and Energy Conserving Scheme for the Shallow Water Equations</span><br>\r\n      Monthly Weather Review, 109, 18–36 http://dx.doi.org/10.1175/1520-0493(1981)109  ', '2017-03-06 08:45:09', 'pamv'),
(10006, 3, 'TOPIC', 'Momentum', 10003, 'reference', '      Hollingsworth, A., Kallberg, P., Renner, V., and Burridge, D. M. [1983]: <br>\r\n      <span style="color: darkred;">An internal symmetric computational instability,\r\n</span><br>\r\n      Quarterly Journal of the Royal Meteorological Society, 109, 417–428  http://dx.doi.org/10.1002/qj.49710946012 ', '2017-03-06 08:45:30', 'pamv'),
(10007, 4, 'TOPIC', 'Lateral Tracers', 10004, 'reference', '      Zalesak, S. T.\r\n [1979]: <br>\r\n      <span style="color: darkred;">Fully multidimensional flux corrected transport algorithms for fluids</span><br>\r\n      J. Comput. Phys., 31, 335–362  ', '2017-03-06 08:46:47', 'pamv'),
(10008, 5, 'TOPIC', 'Vertical Tracers', 10004, 'reference', '      Zalesak, S. T.\r\n [1979]: <br>\r\n      <span style="color: darkred;">Fully multidimensional flux corrected transport algorithms for fluids</span><br>\r\n      J. Comput. Phys., 31, 335–362  ', '2017-03-06 08:47:36', 'pamv'),
(10009, 6, 'TOPIC', 'Lateral Physics', 39, 'reference', '      Gent P. R., and J. C. McWilliams [1990]: <br>\r\n      <span style="color: darkred;">Isopycnal mixing in ocean circulation models.</span><br>\r\n      Journal of Physical Oceanography, 20, 150-155.  ', '2017-03-06 08:48:38', 'pamv'),
(10010, 7, 'TOPIC', 'Momentum', 43, 'reference', '      Roberts M. J., and D. Marshall [1998]: <br>\r\n      <span style="color: darkred;">Do we require adiabatic dissipation schemes in eddy-resolving ocean models?</span><br>\r\n      Journal of Physical Oceanography, 28, 2050-2063.  ', '2017-03-06 08:49:47', 'pamv'),
(10011, 8, 'TOPIC', 'Tracers', 39, 'reference', '      Gent P. R., and J. C. McWilliams [1990]: <br>\r\n      <span style="color: darkred;">Isopycnal mixing in ocean circulation models.</span><br>\r\n      Journal of Physical Oceanography, 20, 150-155.  ', '2017-03-06 08:50:21', 'pamv'),
(10012, 9, 'TOPIC', 'Vertical Physics', 10012, 'reference', '      Simmons, H., Jayne, S., Laurent, L. S., and Weaver, A.\r\n [2004]: <br>\r\n      <span style="color: darkred;">Tidally driven mixing in a numerical model of the ocean general circulation</span><br>\r\n      Ocean Model., 6, 245–263  ', '2017-03-06 08:58:24', 'pamv'),
(10013, 9, 'TOPIC', 'Vertical Physics', 10011, 'reference', '      Rodgers, K. B., Aumont, O., Mikaloff Fletcher, S. E., Plancherel, Y., Bopp, L., de Boyer Montégut, C., Iudicone, D., Keeling, R. F., Madec, G., and Wanninkhof, R. [2014]: <br>\r\n      <span style="color: darkred;">Strong sensitivity of Southern Ocean carbon uptake and nutrient cycling to wind stirring</span><br>\r\n      Biogeosciences, 11, 4077–4098 http://www.biogeosciences.net/11/4077/2014 ', '2017-03-06 08:58:24', 'pamv'),
(10014, 9, 'TOPIC', 'Vertical Physics', 10010, 'reference', '      Merryfield, W. J., Holloway, G., and Gargett, A. E. [1999]: <br>\r\n      <span style="color: darkred;">A global ocean model with double-diffusive mixing</span><br>\r\n      J. Phys. Ocean., 29, 1124–1142  ', '2017-03-06 08:58:24', 'pamv'),
(10015, 9, 'TOPIC', 'Vertical Physics', 189, 'reference', '      Madec, G. [2008]: <br>\r\n      <span style="color: darkred;">NEMO ocean engine </span><br>\r\n      Note du Pole de modélisation, Institut Pierre-Simon Laplace (IPSL), France, No 27 ISSN No 1288-1619  ', '2017-03-06 08:58:24', 'pamv'),
(10016, 9, 'TOPIC', 'Vertical Physics', 10009, 'reference', '      Koch-Larrouy, A., Madec, G., Blanke, B., and Molcard, R. [2008]: <br>\r\n      <span style="color: darkred;">Water mass transformation along the Indonesian throughflow in an OGCM</span><br>\r\n      Ocean Dynam., 58, 289–309  ', '2017-03-06 08:58:24', 'pamv'),
(10017, 9, 'TOPIC', 'Vertical Physics', 10008, 'reference', '      Gregg, M. C., Sanford, T. B., and Winkel, D. P. [2003]: <br>\r\n      <span style="color: darkred;">Reduced mixing from the breaking of internal waves in equatorial waters</span><br>\r\n      Nature, 422, 513–515  ', '2017-03-06 08:58:24', 'pamv'),
(10018, 9, 'TOPIC', 'Vertical Physics', 10007, 'reference', '      Gaspar, P., Grégoris, Y., and Lefevre, J.-M. [1990]: <br>\r\n      <span style="color: darkred;">A simple eddy kinetic energy model for simulations of the oceanic vertical mixing: tests at Station Papa and long-term upper ocean study site</span><br>\r\n       J. Geophys. Res., 95, 16179–16193 doi:10.1029/JC095iC09p16179 ', '2017-03-06 08:58:24', 'pamv'),
(10019, 9, 'TOPIC', 'Vertical Physics', 10005, 'reference', '      Axell, L. B.\r\n [2002]: <br>\r\n      <span style="color: darkred;">Wind-driven Internal Waves and Langmuir Circulations in a Numerical Ocean Model of the Southern Baltic Sea</span><br>\r\n      J. Geophys. Res., 107. 3204 doi:10.1029/2001JC000922, 2002. ', '2017-03-06 08:58:24', 'pamv'),
(10020, 9, 'TOPIC', 'Vertical Physics', 10006, 'reference', '      Craig, P. D. and Banner, M. L. [1994]: <br>\r\n      <span style="color: darkred;">Layer Modelling Wave-Enhanced Turbulence in the Ocean Surface</span><br>\r\n      J. Phys. Oceanogr., 24, 2546–2559  ', '2017-03-06 08:58:24', 'pamv'),
(10021, 10, 'TOPIC', 'Boundary Layer Mixing', 10011, 'reference', '      Rodgers, K. B., Aumont, O., Mikaloff Fletcher, S. E., Plancherel, Y., Bopp, L., de Boyer Montégut, C., Iudicone, D., Keeling, R. F., Madec, G., and Wanninkhof, R. [2014]: <br>\r\n      <span style="color: darkred;">Strong sensitivity of Southern Ocean carbon uptake and nutrient cycling to wind stirring</span><br>\r\n      Biogeosciences, 11, 4077–4098 http://www.biogeosciences.net/11/4077/2014 ', '2017-03-06 09:02:10', 'pamv'),
(10022, 10, 'TOPIC', 'Boundary Layer Mixing', 10008, 'reference', '      Gregg, M. C., Sanford, T. B., and Winkel, D. P. [2003]: <br>\r\n      <span style="color: darkred;">Reduced mixing from the breaking of internal waves in equatorial waters</span><br>\r\n      Nature, 422, 513–515  ', '2017-03-06 09:02:10', 'pamv'),
(10023, 10, 'TOPIC', 'Boundary Layer Mixing', 10007, 'reference', '      Gaspar, P., Grégoris, Y., and Lefevre, J.-M. [1990]: <br>\r\n      <span style="color: darkred;">A simple eddy kinetic energy model for simulations of the oceanic vertical mixing: tests at Station Papa and long-term upper ocean study site</span><br>\r\n       J. Geophys. Res., 95, 16179–16193 doi:10.1029/JC095iC09p16179 ', '2017-03-06 09:02:10', 'pamv'),
(10024, 10, 'TOPIC', 'Boundary Layer Mixing', 10006, 'reference', '      Craig, P. D. and Banner, M. L. [1994]: <br>\r\n      <span style="color: darkred;">Layer Modelling Wave-Enhanced Turbulence in the Ocean Surface</span><br>\r\n      J. Phys. Oceanogr., 24, 2546–2559  ', '2017-03-06 09:02:10', 'pamv'),
(10025, 10, 'TOPIC', 'Boundary Layer Mixing', 10005, 'reference', '      Axell, L. B.\r\n [2002]: <br>\r\n      <span style="color: darkred;">Wind-driven Internal Waves and Langmuir Circulations in a Numerical Ocean Model of the Southern Baltic Sea</span><br>\r\n      J. Geophys. Res., 107. 3204 doi:10.1029/2001JC000922, 2002. ', '2017-03-06 09:02:10', 'pamv'),
(10026, 10, 'TOPIC', 'Boundary Layer Mixing', 189, 'reference', '      Madec, G. [2008]: <br>\r\n      <span style="color: darkred;">NEMO ocean engine </span><br>\r\n      Note du Pole de modélisation, Institut Pierre-Simon Laplace (IPSL), France, No 27 ISSN No 1288-1619  ', '2017-03-06 09:02:11', 'pamv'),
(10027, 11, 'TOPIC', 'Interior Mixing', 10012, 'reference', '      Simmons, H., Jayne, S., Laurent, L. S., and Weaver, A.\r\n [2004]: <br>\r\n      <span style="color: darkred;">Tidally driven mixing in a numerical model of the ocean general circulation</span><br>\r\n      Ocean Model., 6, 245–263  ', '2017-03-06 09:03:49', 'pamv'),
(10028, 11, 'TOPIC', 'Interior Mixing', 10010, 'reference', '      Merryfield, W. J., Holloway, G., and Gargett, A. E. [1999]: <br>\r\n      <span style="color: darkred;">A global ocean model with double-diffusive mixing</span><br>\r\n      J. Phys. Ocean., 29, 1124–1142  ', '2017-03-06 09:03:49', 'pamv'),
(10029, 11, 'TOPIC', 'Interior Mixing', 10009, 'reference', '      Koch-Larrouy, A., Madec, G., Blanke, B., and Molcard, R. [2008]: <br>\r\n      <span style="color: darkred;">Water mass transformation along the Indonesian throughflow in an OGCM</span><br>\r\n      Ocean Dynam., 58, 289–309  ', '2017-03-06 09:03:49', 'pamv'),
(10030, 11, 'TOPIC', 'Interior Mixing', 10008, 'reference', '      Gregg, M. C., Sanford, T. B., and Winkel, D. P. [2003]: <br>\r\n      <span style="color: darkred;">Reduced mixing from the breaking of internal waves in equatorial waters</span><br>\r\n      Nature, 422, 513–515  ', '2017-03-06 09:03:49', 'pamv'),
(10031, 11, 'TOPIC', 'Interior Mixing', 10007, 'reference', '      Gaspar, P., Grégoris, Y., and Lefevre, J.-M. [1990]: <br>\r\n      <span style="color: darkred;">A simple eddy kinetic energy model for simulations of the oceanic vertical mixing: tests at Station Papa and long-term upper ocean study site</span><br>\r\n       J. Geophys. Res., 95, 16179–16193 doi:10.1029/JC095iC09p16179 ', '2017-03-06 09:03:49', 'pamv'),
(10032, 12, 'TOPIC', 'Uplow Boundaries', 10015, 'reference', '      Roullet, G. and Madec, G. [2000]: <br>\r\n      <span style="color: darkred;">Salt conservation, free surface, and varying levels: A new formulation for ocean general circulation models</span><br>\r\n      Journal of Geophysical Research: Oceans, 105, 23 927–23 942 http://dx.doi.org/10.1029/2000JC900089 ', '2017-03-06 09:12:52', 'pamv'),
(10033, 12, 'TOPIC', 'Uplow Boundaries', 10014, 'reference', '      Beckmann, A. and Doscher, R. [1997]: <br>\r\n      <span style="color: darkred;">A method for improved representation of dense water spreading over topography in geopotential-coordinate models</span><br>\r\n      J. Phys. Oceanogr., 27, 581–591  ', '2017-03-06 09:12:52', 'pamv'),
(10034, 12, 'TOPIC', 'Uplow Boundaries', 10013, 'reference', '      Adcroft, A. and Campin, J.-M. [2004]: <br>\r\n      <span style="color: darkred;">Rescaled height coordinates for accurate representation of free-surface flows in ocean circulation models</span><br>\r\n      Ocean Modelling, 7, 269 – 284 http://www.sciencedirect.com/science/article/ ', '2017-03-06 09:12:52', 'pamv'),
(10035, 13, 'TOPIC', 'Boundary Forcing', 10019, 'reference', '      Stein, C. A. and Stein, S. [1992]: <br>\r\n      <span style="color: darkred;">A model for the global variation in oceanic depth and heat flow with lithospheric age</span><br>\r\n      Nature, 359, 123–129  ', '2017-03-06 09:15:10', 'pamv'),
(10036, 13, 'TOPIC', 'Boundary Forcing', 10018, 'reference', '      Martin, T. and Adcroft, A. [2010]: <br>\r\n      <span style="color: darkred;">Parameterizing the fresh-water flux from land ice to ocean with interactive icebergs in a coupled climate model</span><br>\r\n      Ocean Modelling, 34, 111 – 124 http://www.sciencedirect.com/science/article/ ', '2017-03-06 09:15:10', 'pamv'),
(10037, 13, 'TOPIC', 'Boundary Forcing', 10017, 'reference', '      Marsh, R., Ivchenko, V. O., Skliris, N., Alderson, S., Bigg, G. R., Madec, G., Blaker, A. T., Aksenov, Y., Sinha, B., Coward, A. C., Le Sommer, J., Merino, I., and Zalesny, V. [2015]: <br>\r\n      <span style="color: darkred;">NEMO–ICB (v1.0): interactive icebergs in the NEMO ocean model globally configured at eddy-permitting resolution</span><br>\r\n      Geoscientific Model Development, 8, 1547–1562 https://hal-insu.archives-ouvertes.fr/insu-01 ', '2017-03-06 09:15:10', 'pamv'),
(10038, 13, 'TOPIC', 'Boundary Forcing', 10016, 'reference', '      Bigg, G. R., Wadley, M. R., Stevens, D. P., and Johnson, J. A. [1997]: <br>\r\n      <span style="color: darkred;">Modelling dynamics and thermodynamics of icebergs</span><br>\r\n      Cold Regions Science and Technology, 26, 113–135  ', '2017-03-06 09:15:10', 'pamv'),
(10039, 15, 'TOPIC', 'Tracers', 10016, 'reference', '      Bigg, G. R., Wadley, M. R., Stevens, D. P., and Johnson, J. A. [1997]: <br>\r\n      <span style="color: darkred;">Modelling dynamics and thermodynamics of icebergs</span><br>\r\n      Cold Regions Science and Technology, 26, 113–135  ', '2017-03-06 09:16:56', 'pamv'),
(10040, 15, 'TOPIC', 'Tracers', 10017, 'reference', '      Marsh, R., Ivchenko, V. O., Skliris, N., Alderson, S., Bigg, G. R., Madec, G., Blaker, A. T., Aksenov, Y., Sinha, B., Coward, A. C., Le Sommer, J., Merino, I., and Zalesny, V. [2015]: <br>\r\n      <span style="color: darkred;">NEMO–ICB (v1.0): interactive icebergs in the NEMO ocean model globally configured at eddy-permitting resolution</span><br>\r\n      Geoscientific Model Development, 8, 1547–1562 https://hal-insu.archives-ouvertes.fr/insu-01 ', '2017-03-06 09:16:56', 'pamv'),
(10041, 15, 'TOPIC', 'Tracers', 10018, 'reference', '      Martin, T. and Adcroft, A. [2010]: <br>\r\n      <span style="color: darkred;">Parameterizing the fresh-water flux from land ice to ocean with interactive icebergs in a coupled climate model</span><br>\r\n      Ocean Modelling, 34, 111 – 124 http://www.sciencedirect.com/science/article/ ', '2017-03-06 09:16:56', 'pamv'),
(10042, 10001, 'MODEL', 'NEMO', 10021, 'reference', '      IOC, IHO and BODC [2008]: <br>\r\n      <span style="color: darkred;">Centenary Edition of the GEBCO Digital Atlas</span><br>\r\n      Published on CD-ROM on behalf of the Intergovernmental Oceanographic Commission and the International Hydrographic Organization as part of the General Bathymetric Chart of the Oceans, British Oceanogr  ', '2017-03-06 10:07:11', 'pamv'),
(10043, 10001, 'MODEL', 'NEMO', 10022, 'reference', '      Mathiot, P., Jenkins, A., Harris, C., and Madec, G. [2017]: <br>\r\n      <span style="color: darkred;">Different ways to represent ice shelf melting in a z* coordinate ocean model</span><br>\r\n      Geoscientific Model Development  ', '2017-03-06 10:07:44', 'pamv'),
(10044, 13, 'TOPIC', 'Boundary Forcing', 10023, 'reference', '      Lengaigne, M., Menkes, C., Aumont, O., Gorgues, T., Bopp, L., André, J.-M. and Madec, G. [2007]: <br>\r\n      <span style="color: darkred;">Influence of the oceanic biology on the tropical Pacific climate in a coupled general circulation model</span><br>\r\n      Climate Dynamics, 28(5), 503-516.  ', '2017-03-06 10:17:03', 'pamv'),
(10045, 20, 'TOPIC', 'Advection', 10002, 'reference', '      Arakawa, A. and Lamb, V. R. [1981]: <br>\r\n      <span style="color: darkred;">A Potential Enstrophy and Energy Conserving Scheme for the Shallow Water Equations</span><br>\r\n      Monthly Weather Review, 109, 18–36 http://dx.doi.org/10.1175/1520-0493(1981)109  ', '2017-03-14 21:28:52', 'clone_10002'),
(10046, 20, 'TOPIC', 'Advection', 10003, 'reference', '      Hollingsworth, A., Kallberg, P., Renner, V., and Burridge, D. M. [1983]: <br>\r\n      <span style="color: darkred;">An internal symmetric computational instability,\r\n</span><br>\r\n      Quarterly Journal of the Royal Meteorological Society, 109, 417–428  http://dx.doi.org/10.1002/qj.49710946012 ', '2017-03-14 21:28:52', 'clone_10003'),
(10047, 20, 'TOPIC', 'Advection', 10004, 'reference', '      Zalesak, S. T.\r\n [1979]: <br>\r\n      <span style="color: darkred;">Fully multidimensional flux corrected transport algorithms for fluids</span><br>\r\n      J. Comput. Phys., 31, 335–362  ', '2017-03-14 21:28:52', 'clone_10004'),
(10048, 21, 'TOPIC', 'Momentum', 10002, 'reference', '      Arakawa, A. and Lamb, V. R. [1981]: <br>\r\n      <span style="color: darkred;">A Potential Enstrophy and Energy Conserving Scheme for the Shallow Water Equations</span><br>\r\n      Monthly Weather Review, 109, 18–36 http://dx.doi.org/10.1175/1520-0493(1981)109  ', '2017-03-14 21:28:52', 'clone_10005'),
(10049, 21, 'TOPIC', 'Momentum', 10003, 'reference', '      Hollingsworth, A., Kallberg, P., Renner, V., and Burridge, D. M. [1983]: <br>\r\n      <span style="color: darkred;">An internal symmetric computational instability,\r\n</span><br>\r\n      Quarterly Journal of the Royal Meteorological Society, 109, 417–428  http://dx.doi.org/10.1002/qj.49710946012 ', '2017-03-14 21:28:52', 'clone_10006'),
(10050, 22, 'TOPIC', 'Lateral Tracers', 10004, 'reference', '      Zalesak, S. T.\r\n [1979]: <br>\r\n      <span style="color: darkred;">Fully multidimensional flux corrected transport algorithms for fluids</span><br>\r\n      J. Comput. Phys., 31, 335–362  ', '2017-03-14 21:28:52', 'clone_10007'),
(10051, 23, 'TOPIC', 'Vertical Tracers', 10004, 'reference', '      Zalesak, S. T.\r\n [1979]: <br>\r\n      <span style="color: darkred;">Fully multidimensional flux corrected transport algorithms for fluids</span><br>\r\n      J. Comput. Phys., 31, 335–362  ', '2017-03-14 21:28:52', 'clone_10008'),
(10052, 24, 'TOPIC', 'Lateral Physics', 39, 'reference', '      Gent P. R., and J. C. McWilliams [1990]: <br>\r\n      <span style="color: darkred;">Isopycnal mixing in ocean circulation models.</span><br>\r\n      Journal of Physical Oceanography, 20, 150-155.  ', '2017-03-14 21:28:52', 'clone_10009'),
(10053, 25, 'TOPIC', 'Momentum', 43, 'reference', '      Roberts M. J., and D. Marshall [1998]: <br>\r\n      <span style="color: darkred;">Do we require adiabatic dissipation schemes in eddy-resolving ocean models?</span><br>\r\n      Journal of Physical Oceanography, 28, 2050-2063.  ', '2017-03-14 21:28:52', 'clone_10010'),
(10054, 26, 'TOPIC', 'Tracers', 39, 'reference', '      Gent P. R., and J. C. McWilliams [1990]: <br>\r\n      <span style="color: darkred;">Isopycnal mixing in ocean circulation models.</span><br>\r\n      Journal of Physical Oceanography, 20, 150-155.  ', '2017-03-14 21:28:52', 'clone_10011'),
(10055, 27, 'TOPIC', 'Vertical Physics', 10012, 'reference', '      Simmons, H., Jayne, S., Laurent, L. S., and Weaver, A.\r\n [2004]: <br>\r\n      <span style="color: darkred;">Tidally driven mixing in a numerical model of the ocean general circulation</span><br>\r\n      Ocean Model., 6, 245–263  ', '2017-03-14 21:28:52', 'clone_10012'),
(10056, 27, 'TOPIC', 'Vertical Physics', 10011, 'reference', '      Rodgers, K. B., Aumont, O., Mikaloff Fletcher, S. E., Plancherel, Y., Bopp, L., de Boyer Montégut, C., Iudicone, D., Keeling, R. F., Madec, G., and Wanninkhof, R. [2014]: <br>\r\n      <span style="color: darkred;">Strong sensitivity of Southern Ocean carbon uptake and nutrient cycling to wind stirring</span><br>\r\n      Biogeosciences, 11, 4077–4098 http://www.biogeosciences.net/11/4077/2014 ', '2017-03-14 21:28:52', 'clone_10013'),
(10057, 27, 'TOPIC', 'Vertical Physics', 10010, 'reference', '      Merryfield, W. J., Holloway, G., and Gargett, A. E. [1999]: <br>\r\n      <span style="color: darkred;">A global ocean model with double-diffusive mixing</span><br>\r\n      J. Phys. Ocean., 29, 1124–1142  ', '2017-03-14 21:28:52', 'clone_10014'),
(10058, 27, 'TOPIC', 'Vertical Physics', 189, 'reference', '      Madec, G. [2008]: <br>\r\n      <span style="color: darkred;">NEMO ocean engine </span><br>\r\n      Note du Pole de modélisation, Institut Pierre-Simon Laplace (IPSL), France, No 27 ISSN No 1288-1619  ', '2017-03-14 21:28:52', 'clone_10015'),
(10059, 27, 'TOPIC', 'Vertical Physics', 10009, 'reference', '      Koch-Larrouy, A., Madec, G., Blanke, B., and Molcard, R. [2008]: <br>\r\n      <span style="color: darkred;">Water mass transformation along the Indonesian throughflow in an OGCM</span><br>\r\n      Ocean Dynam., 58, 289–309  ', '2017-03-14 21:28:52', 'clone_10016'),
(10060, 27, 'TOPIC', 'Vertical Physics', 10008, 'reference', '      Gregg, M. C., Sanford, T. B., and Winkel, D. P. [2003]: <br>\r\n      <span style="color: darkred;">Reduced mixing from the breaking of internal waves in equatorial waters</span><br>\r\n      Nature, 422, 513–515  ', '2017-03-14 21:28:52', 'clone_10017'),
(10061, 27, 'TOPIC', 'Vertical Physics', 10007, 'reference', '      Gaspar, P., Grégoris, Y., and Lefevre, J.-M. [1990]: <br>\r\n      <span style="color: darkred;">A simple eddy kinetic energy model for simulations of the oceanic vertical mixing: tests at Station Papa and long-term upper ocean study site</span><br>\r\n       J. Geophys. Res., 95, 16179–16193 doi:10.1029/JC095iC09p16179 ', '2017-03-14 21:28:52', 'clone_10018'),
(10062, 27, 'TOPIC', 'Vertical Physics', 10005, 'reference', '      Axell, L. B.\r\n [2002]: <br>\r\n      <span style="color: darkred;">Wind-driven Internal Waves and Langmuir Circulations in a Numerical Ocean Model of the Southern Baltic Sea</span><br>\r\n      J. Geophys. Res., 107. 3204 doi:10.1029/2001JC000922, 2002. ', '2017-03-14 21:28:52', 'clone_10019'),
(10063, 27, 'TOPIC', 'Vertical Physics', 10006, 'reference', '      Craig, P. D. and Banner, M. L. [1994]: <br>\r\n      <span style="color: darkred;">Layer Modelling Wave-Enhanced Turbulence in the Ocean Surface</span><br>\r\n      J. Phys. Oceanogr., 24, 2546–2559  ', '2017-03-14 21:28:52', 'clone_10020'),
(10064, 28, 'TOPIC', 'Boundary Layer Mixing', 10011, 'reference', '      Rodgers, K. B., Aumont, O., Mikaloff Fletcher, S. E., Plancherel, Y., Bopp, L., de Boyer Montégut, C., Iudicone, D., Keeling, R. F., Madec, G., and Wanninkhof, R. [2014]: <br>\r\n      <span style="color: darkred;">Strong sensitivity of Southern Ocean carbon uptake and nutrient cycling to wind stirring</span><br>\r\n      Biogeosciences, 11, 4077–4098 http://www.biogeosciences.net/11/4077/2014 ', '2017-03-14 21:28:52', 'clone_10021'),
(10065, 28, 'TOPIC', 'Boundary Layer Mixing', 10008, 'reference', '      Gregg, M. C., Sanford, T. B., and Winkel, D. P. [2003]: <br>\r\n      <span style="color: darkred;">Reduced mixing from the breaking of internal waves in equatorial waters</span><br>\r\n      Nature, 422, 513–515  ', '2017-03-14 21:28:52', 'clone_10022'),
(10066, 28, 'TOPIC', 'Boundary Layer Mixing', 10007, 'reference', '      Gaspar, P., Grégoris, Y., and Lefevre, J.-M. [1990]: <br>\r\n      <span style="color: darkred;">A simple eddy kinetic energy model for simulations of the oceanic vertical mixing: tests at Station Papa and long-term upper ocean study site</span><br>\r\n       J. Geophys. Res., 95, 16179–16193 doi:10.1029/JC095iC09p16179 ', '2017-03-14 21:28:52', 'clone_10023'),
(10067, 28, 'TOPIC', 'Boundary Layer Mixing', 10006, 'reference', '      Craig, P. D. and Banner, M. L. [1994]: <br>\r\n      <span style="color: darkred;">Layer Modelling Wave-Enhanced Turbulence in the Ocean Surface</span><br>\r\n      J. Phys. Oceanogr., 24, 2546–2559  ', '2017-03-14 21:28:52', 'clone_10024'),
(10068, 28, 'TOPIC', 'Boundary Layer Mixing', 10005, 'reference', '      Axell, L. B.\r\n [2002]: <br>\r\n      <span style="color: darkred;">Wind-driven Internal Waves and Langmuir Circulations in a Numerical Ocean Model of the Southern Baltic Sea</span><br>\r\n      J. Geophys. Res., 107. 3204 doi:10.1029/2001JC000922, 2002. ', '2017-03-14 21:28:52', 'clone_10025'),
(10069, 28, 'TOPIC', 'Boundary Layer Mixing', 189, 'reference', '      Madec, G. [2008]: <br>\r\n      <span style="color: darkred;">NEMO ocean engine </span><br>\r\n      Note du Pole de modélisation, Institut Pierre-Simon Laplace (IPSL), France, No 27 ISSN No 1288-1619  ', '2017-03-14 21:28:52', 'clone_10026'),
(10070, 29, 'TOPIC', 'Interior Mixing', 10012, 'reference', '      Simmons, H., Jayne, S., Laurent, L. S., and Weaver, A.\r\n [2004]: <br>\r\n      <span style="color: darkred;">Tidally driven mixing in a numerical model of the ocean general circulation</span><br>\r\n      Ocean Model., 6, 245–263  ', '2017-03-14 21:28:52', 'clone_10027'),
(10071, 29, 'TOPIC', 'Interior Mixing', 10010, 'reference', '      Merryfield, W. J., Holloway, G., and Gargett, A. E. [1999]: <br>\r\n      <span style="color: darkred;">A global ocean model with double-diffusive mixing</span><br>\r\n      J. Phys. Ocean., 29, 1124–1142  ', '2017-03-14 21:28:52', 'clone_10028'),
(10072, 29, 'TOPIC', 'Interior Mixing', 10009, 'reference', '      Koch-Larrouy, A., Madec, G., Blanke, B., and Molcard, R. [2008]: <br>\r\n      <span style="color: darkred;">Water mass transformation along the Indonesian throughflow in an OGCM</span><br>\r\n      Ocean Dynam., 58, 289–309  ', '2017-03-14 21:28:52', 'clone_10029'),
(10073, 29, 'TOPIC', 'Interior Mixing', 10008, 'reference', '      Gregg, M. C., Sanford, T. B., and Winkel, D. P. [2003]: <br>\r\n      <span style="color: darkred;">Reduced mixing from the breaking of internal waves in equatorial waters</span><br>\r\n      Nature, 422, 513–515  ', '2017-03-14 21:28:52', 'clone_10030'),
(10074, 29, 'TOPIC', 'Interior Mixing', 10007, 'reference', '      Gaspar, P., Grégoris, Y., and Lefevre, J.-M. [1990]: <br>\r\n      <span style="color: darkred;">A simple eddy kinetic energy model for simulations of the oceanic vertical mixing: tests at Station Papa and long-term upper ocean study site</span><br>\r\n       J. Geophys. Res., 95, 16179–16193 doi:10.1029/JC095iC09p16179 ', '2017-03-14 21:28:52', 'clone_10031'),
(10075, 30, 'TOPIC', 'Uplow Boundaries', 10015, 'reference', '      Roullet, G. and Madec, G. [2000]: <br>\r\n      <span style="color: darkred;">Salt conservation, free surface, and varying levels: A new formulation for ocean general circulation models</span><br>\r\n      Journal of Geophysical Research: Oceans, 105, 23 927–23 942 http://dx.doi.org/10.1029/2000JC900089 ', '2017-03-14 21:28:52', 'clone_10032'),
(10076, 30, 'TOPIC', 'Uplow Boundaries', 10014, 'reference', '      Beckmann, A. and Doscher, R. [1997]: <br>\r\n      <span style="color: darkred;">A method for improved representation of dense water spreading over topography in geopotential-coordinate models</span><br>\r\n      J. Phys. Oceanogr., 27, 581–591  ', '2017-03-14 21:28:52', 'clone_10033'),
(10077, 30, 'TOPIC', 'Uplow Boundaries', 10013, 'reference', '      Adcroft, A. and Campin, J.-M. [2004]: <br>\r\n      <span style="color: darkred;">Rescaled height coordinates for accurate representation of free-surface flows in ocean circulation models</span><br>\r\n      Ocean Modelling, 7, 269 – 284 http://www.sciencedirect.com/science/article/ ', '2017-03-14 21:28:52', 'clone_10034'),
(10078, 31, 'TOPIC', 'Boundary Forcing', 10019, 'reference', '      Stein, C. A. and Stein, S. [1992]: <br>\r\n      <span style="color: darkred;">A model for the global variation in oceanic depth and heat flow with lithospheric age</span><br>\r\n      Nature, 359, 123–129  ', '2017-03-14 21:28:52', 'clone_10035'),
(10079, 31, 'TOPIC', 'Boundary Forcing', 10018, 'reference', '      Martin, T. and Adcroft, A. [2010]: <br>\r\n      <span style="color: darkred;">Parameterizing the fresh-water flux from land ice to ocean with interactive icebergs in a coupled climate model</span><br>\r\n      Ocean Modelling, 34, 111 – 124 http://www.sciencedirect.com/science/article/ ', '2017-03-14 21:28:52', 'clone_10036'),
(10080, 31, 'TOPIC', 'Boundary Forcing', 10017, 'reference', '      Marsh, R., Ivchenko, V. O., Skliris, N., Alderson, S., Bigg, G. R., Madec, G., Blaker, A. T., Aksenov, Y., Sinha, B., Coward, A. C., Le Sommer, J., Merino, I., and Zalesny, V. [2015]: <br>\r\n      <span style="color: darkred;">NEMO–ICB (v1.0): interactive icebergs in the NEMO ocean model globally configured at eddy-permitting resolution</span><br>\r\n      Geoscientific Model Development, 8, 1547–1562 https://hal-insu.archives-ouvertes.fr/insu-01 ', '2017-03-14 21:28:52', 'clone_10037'),
(10081, 31, 'TOPIC', 'Boundary Forcing', 10016, 'reference', '      Bigg, G. R., Wadley, M. R., Stevens, D. P., and Johnson, J. A. [1997]: <br>\r\n      <span style="color: darkred;">Modelling dynamics and thermodynamics of icebergs</span><br>\r\n      Cold Regions Science and Technology, 26, 113–135  ', '2017-03-14 21:28:52', 'clone_10038'),
(10082, 31, 'TOPIC', 'Boundary Forcing', 10023, 'reference', '      Lengaigne, M., Menkes, C., Aumont, O., Gorgues, T., Bopp, L., André, J.-M. and Madec, G. [2007]: <br>\r\n      <span style="color: darkred;">Influence of the oceanic biology on the tropical Pacific climate in a coupled general circulation model</span><br>\r\n      Climate Dynamics, 28(5), 503-516.  ', '2017-03-14 21:28:52', 'clone_10044'),
(10083, 33, 'TOPIC', 'Tracers', 10016, 'reference', '      Bigg, G. R., Wadley, M. R., Stevens, D. P., and Johnson, J. A. [1997]: <br>\r\n      <span style="color: darkred;">Modelling dynamics and thermodynamics of icebergs</span><br>\r\n      Cold Regions Science and Technology, 26, 113–135  ', '2017-03-14 21:28:52', 'clone_10039'),
(10084, 33, 'TOPIC', 'Tracers', 10017, 'reference', '      Marsh, R., Ivchenko, V. O., Skliris, N., Alderson, S., Bigg, G. R., Madec, G., Blaker, A. T., Aksenov, Y., Sinha, B., Coward, A. C., Le Sommer, J., Merino, I., and Zalesny, V. [2015]: <br>\r\n      <span style="color: darkred;">NEMO–ICB (v1.0): interactive icebergs in the NEMO ocean model globally configured at eddy-permitting resolution</span><br>\r\n      Geoscientific Model Development, 8, 1547–1562 https://hal-insu.archives-ouvertes.fr/insu-01 ', '2017-03-14 21:28:52', 'clone_10040'),
(10085, 33, 'TOPIC', 'Tracers', 10018, 'reference', '      Martin, T. and Adcroft, A. [2010]: <br>\r\n      <span style="color: darkred;">Parameterizing the fresh-water flux from land ice to ocean with interactive icebergs in a coupled climate model</span><br>\r\n      Ocean Modelling, 34, 111 – 124 http://www.sciencedirect.com/science/article/ ', '2017-03-14 21:28:52', 'clone_10041'),
(10086, 10002, 'MODEL', 'NEMO - ORCA025', 10000, 'reference', '      Barnier, B., Madec, G., Penduff, T., Molines, J.-M., Treguier, A.-M., Le Sommer, J., Beckmann, A., Biastoch, A., Böning, C., Dengg, J., Derval, C., Durand, E., Gulev, S., Remy, E., Talandier, C., Theetten, S., Maltrud, M., McClean, J., and De Cuevas, B.\r\n [2006]: <br>\r\n      <span style="color: darkred;">Impact of partial steps and momentum advection schemes in a global ocean circulation model at eddy-permitting resolution.</span><br>\r\n      Ocean Dynamics, 56, 543–567. http://dx.doi.org/10.1007/s10236-006-0082-1 ', '2017-03-27 07:43:23', 'pamv'),
(10087, 10002, 'MODEL', 'NEMO - ORCA025', 189, 'reference', '      Madec, G. [2008]: <br>\r\n      <span style="color: darkred;">NEMO ocean engine </span><br>\r\n      Note du Pole de modélisation, Institut Pierre-Simon Laplace (IPSL), France, No 27 ISSN No 1288-1619  ', '2017-03-27 07:43:54', 'pamv'),
(10088, 10001, 'MODEL', 'NEMO - ORCA1', 189, 'reference', '      Madec, G. [2008]: <br>\r\n      <span style="color: darkred;">NEMO ocean engine </span><br>\r\n      Note du Pole de modélisation, Institut Pierre-Simon Laplace (IPSL), France, No 27 ISSN No 1288-1619  ', '2017-03-27 07:44:20', 'pamv'),
(10089, 10001, 'MODEL', 'NEMO - ORCA1', 10000, 'reference', '      Barnier, B., Madec, G., Penduff, T., Molines, J.-M., Treguier, A.-M., Le Sommer, J., Beckmann, A., Biastoch, A., Böning, C., Dengg, J., Derval, C., Durand, E., Gulev, S., Remy, E., Talandier, C., Theetten, S., Maltrud, M., McClean, J., and De Cuevas, B.\r\n [2006]: <br>\r\n      <span style="color: darkred;">Impact of partial steps and momentum advection schemes in a global ocean circulation model at eddy-permitting resolution.</span><br>\r\n      Ocean Dynamics, 56, 543–567. http://dx.doi.org/10.1007/s10236-006-0082-1 ', '2017-03-27 07:44:35', 'pamv'),
(10090, 10110, 'EXPERIMENT', 'ssp245', 10013, 'reference', '      Adcroft, A. and Campin, J.-M. [2004]: <br>\r\n      <span style="color: darkred;">Rescaled height coordinates for accurate representation of free-surface flows in ocean circulation models</span><br>\r\n      Ocean Modelling, 7, 269 – 284 http://www.sciencedirect.com/science/article/ ', '2017-05-23 13:21:32', 'admin'),
(10091, 10110, 'EXPERIMENT', 'ssp245', 105, 'citation', '      Barker, H.W. and Z. Li [1995]: <br>\r\n      <span style="color: darkred;">Improved simulation of clear-sky shortwave radiative transfer in the CCC-GCM</span><br>\r\n      J. Climate, 8, 2213-2223  ', '2017-05-23 13:21:46', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `ut_tickets`
--

CREATE TABLE IF NOT EXISTS `ut_tickets` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `o_id` int(11) DEFAULT NULL,
  `o_type` enum('PROJECT','REQUEST','EXPERIMENT') DEFAULT NULL,
  `projectid` int(11) NOT NULL COMMENT 'related project',
  `title` varchar(200) DEFAULT NULL,
  `info` text NOT NULL COMMENT 'description of issue',
  `resolution` text COMMENT 'resolution of issue',
  `responsible` int(11) DEFAULT NULL COMMENT 'person responsible for investigating/resolving issue',
  `classification` varchar(20) NOT NULL COMMENT 'issue classification',
  `severity` varchar(20) NOT NULL COMMENT 'issue severity',
  `status` varchar(20) NOT NULL COMMENT 'current status',
  `weblink` varchar(100) DEFAULT NULL COMMENT 'url to related information',
  `duedate` date DEFAULT NULL COMMENT 'date resolution required',
  `deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT '	flag set if ticket has been deleted',
  `upd_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE CURRENT_TIMESTAMP COMMENT 'date of last update',
  `upd_by` varchar(20) NOT NULL COMMENT 'person/process responsible for last update',
  `o_ticket` char(10) NOT NULL DEFAULT 'TICKET' COMMENT 'code for linking to comments',
  PRIMARY KEY (`id`),
  KEY `activityid` (`projectid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='maintains list of issues associated with each project';

--
-- Dumping data for table `ut_tickets`
--

INSERT INTO `ut_tickets` (`id`, `o_id`, `o_type`, `projectid`, `title`, `info`, `resolution`, `responsible`, `classification`, `severity`, `status`, `weblink`, `duedate`, `deleted`, `upd_date`, `upd_by`, `o_ticket`) VALUES
(6, 10000, 'REQUEST', 10012, 'request ticket', 'thius is a request ticket UKESM1.0 N96ORCA1_ssp2', '', 11, 'process', 'normal', 'in progress', '', '2017-01-14', 0, '2017-01-04 13:04:18', 'admin', 'TICKET'),
(4, 10012, 'PROJECT', 10012, 'Project ticket', 'This is a project ticket', '', 27, 'process', 'normal', 'new', '', '2017-01-04', 0, '2017-01-04 13:02:03', 'admin', 'TICKET'),
(5, 10110, 'EXPERIMENT', 10012, 'experiment ticket', 'just an experiment ticket ssp2-45', '', 14, 'process', 'normal', 'resolved', '', '2017-01-24', 0, '2017-01-04 13:02:57', 'admin', 'TICKET');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `at_data_log`
--
ALTER TABLE `at_data_log`
  ADD CONSTRAINT `at_data_log_ibfk_1` FOREIGN KEY (`data_exchange_id`) REFERENCES `at_data_exchange` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
