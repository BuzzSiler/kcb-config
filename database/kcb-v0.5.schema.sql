BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `codesHistory` (
	`ids`	integer UNIQUE,
	`sequence`	text,
	`sequence_order`	integer,
	`locknums`	TEXT,
	`description`	text,
	`code1`	text,
	`code2`	text,
	`starttime`	DATETIME,
	`endtime`	DATETIME,
	`status`	text,
	`access_count`	integer,
	`retry_count`	integer,
	`max_access`	integer,
	`max_retry`	integer,
	`access_time`	DATETIME,
	`admin_notification_sent`	BOOL,
	`user_notification_email`	text,
	`user_notification_sent`	BOOL,
	`answer1`	text,
	`answer2`	text,
	`answer3`	text,
	`lockbox_state`	integer,
	PRIMARY KEY(`ids`)
);
CREATE TABLE IF NOT EXISTS `codes` (
	`ids`	integer UNIQUE,
	`sequence`	text,
	`sequence_order`	integer,
	`locknums`	TEXT,
	`description`	text,
	`code1`	text,
	`code2`	text,
	`starttime`	DATETIME,
	`endtime`	DATETIME,
	`status`	text,
	`access_count`	integer,
	`retry_count`	integer,
	`max_access`	integer,
	`max_retry`	integer,
	`fingerprint1`	integer,
	`fingerprint2`	integer,
	`lockbox_state`	integer,
	`ask_questions`	integer,
	`question1`	text,
	`question2`	text,
	`question3`	text,
	`access_type`	INTEGER,
	PRIMARY KEY(`ids`)
);
CREATE TABLE IF NOT EXISTS `admin` (
	`ids`	integer UNIQUE,
	`admin_name`	text,
	`admin_email`	text,
	`admin_phone`	text,
	`default_report_freq`	DATETIME,
	`default_report_start`	DATETIME,
	`password`	text,
	`access_code`	text,
	`use_predictive_access_code`	bool,
	`predictive_key`	text,
	`predictive_resolution`	integer,
	`max_locks`	TEXT,
	`smtp_server`	TEXT,
	`smtp_port`	TEXT,
	`smtp_type`	TEXT,
	`smtp_username`	TEXT,
	`smtp_password`	TEXT,
	`vnc_port`	TEXT,
	`vnc_password`	TEXT,
	`report_via_email`	TEXT,
	`report_to_file`	TEXT,
	`report_directory`	TEXT,
	`assist_password`	text,
	`assist_code`	text,
	`show_fingerprint`	bool,
	`show_password`	bool,
	`display_power_down_timeout`	INTEGER,
	`report_deletion` DATETIME,
	PRIMARY KEY(`ids`)
);
COMMIT;
