CREATE DATABASE User_Monitoring;

USE User_Monitoring;

CREATE TABLE ucs (
	uuid INT,
    score DECIMAL(6,5) NOT NULL
);

desc UCS;

SELECT * FROM UCS;

----------------
CREATE TABLE task_scores (
	ts TIMESTAMP,
    quiz_task_uuid INT,
    user_uuid INT,
    task_score DECIMAL(6,5)
);

desc task_scores;

SELECT * FROM task_scores;


----------------
CREATE TABLE datahunt_tracker (
	datahunt_id INT,
    num_rows_processed INT
);

desc datahunt_tracker;

SELECT * FROM datahunt_tracker;