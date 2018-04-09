BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `admin` (
	`ids`	integer UNIQUE,
	`admin_name`	text,
	`admin_email`	text,
	`admin_phone`	text,
	`email_report_active`	bool,
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
	PRIMARY KEY(`ids`)
);
INSERT INTO `admin` VALUES (1,'admin','admin@yourcompany.com','555.555.5555',0,'0001-01-01 23:59:00','2017-01-13 12:22:19','AwL7SuQ=','AwL772oGpkpqMQ==',0,'CODE5',10,'16','smtpout.secureserver.net','465','1','kcb@keycodebox.com','AwJ5aGxSrgp7fMQQ3OYH','5901','AwJ5aGxSrgp7fMQQ3OYH','0','1','','AwJ5yGY=','AwJ5+9S4GPbWjw==',0,0);
COMMIT;
