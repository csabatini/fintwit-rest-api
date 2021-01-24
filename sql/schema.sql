-- trumpwip.db

CREATE TABLE seed_quote (
     quote_id TEXT NOT NULL PRIMARY KEY,
     value TEXT NOT NULL,
     UNIQUE(quote_id)
);

CREATE TABLE quote_word (
     word TEXT NOT NULL PRIMARY KEY,
     UNIQUE(word)
);

CREATE TABLE status (
     status_id TEXT NOT NULL PRIMARY KEY,
     tags TEXT NOT NULL,
     UNIQUE(status_id)
);

CREATE TABLE status_v2 (
     status_id TEXT NOT NULL PRIMARY KEY,
     tags TEXT NULL,
     UNIQUE(status_id)
);

-- trumptweets.db
CREATE TABLE user_profile (
     guid TEXT NULL,
     push_enabled INTEGER NOT NULL,
     device_token TEXT NULL,
     login_time INTEGER NULL,
     UNIQUE(guid)
);
--INSERT INTO user_profile (push_enabled) VALUES (1);

CREATE TABLE status (
     status_id TEXT NOT NULL PRIMARY KEY,
     screen_name TEXT NOT NULL,
     name TEXT NOT NULL,
     profile_img_url TEXT NULL,
     text TEXT NOT NULL,
     media_url TEXT NULL,
     created_at INTEGER NOT NULL,
     loaded_at INTEGER NOT NULL,
     UNIQUE(status_id)
);

CREATE TABLE tag (
     tag_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
     tag TEXT NOT NULL,
     UNIQUE(tag_id)
);

CREATE TABLE status_tag (
     status_tag_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
     status_id TEXT NOT NULL,
     tag_id INTEGER NOT NULL,
     FOREIGN KEY (status_id) REFERENCES status(status_id),
     FOREIGN KEY (tag_id) REFERENCES tag(tag_id),
     UNIQUE(status_id, tag_id)
);

CREATE TABLE favorite (
     status_id TEXT NOT NULL,
     FOREIGN KEY (status_id) REFERENCES status(status_id),
     UNIQUE(status_id)
);

-- trumptweets mysql
CREATE DATABASE trumptweets CHARACTER SET = utf8mb4 COLLATE utf8mb4_general_ci;

CREATE TABLE user_profile (
    guid varchar(36) NOT NULL,
    push_enabled boolean NOT NULL,
    device_token varchar(200) NULL,
    created_time timestamp DEFAULT CURRENT_TIMESTAMP,
    status_max_created_at timestamp NULL DEFAULT NULL,
    PRIMARY KEY (guid)
) DEFAULT CHARSET=utf8;

-- temporary
CREATE TABLE status_word (
    status_word_id int NOT NULL AUTO_INCREMENT,
    word varchar(20) NOT NULL,
    PRIMARY KEY (status_word_id )
) DEFAULT CHARSET=utf8;

CREATE TABLE status (
    status_id varchar(36) NOT NULL,
    author_id int NOT NULL,
    text varchar(1000) NOT NULL,
    media_url varchar(500) NULL,
    created_at timestamp NOT NULL,
    PRIMARY KEY (status_id),
    FOREIGN KEY (author_id) REFERENCES author(author_id)
) DEFAULT CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci;

-- ALTER TABLE status MODIFY COLUMN media_url varchar(500) NULL;

CREATE TABLE author (
    author_id int NOT NULL,
    screen_name varchar(100) NOT NULL,
    name varchar(255) NOT NULL,
    profile_img_url varchar(500) NULL,
    location varchar(255) NOT NULL,
    description varchar(500) NOT NULL,
    PRIMARY KEY (author_id)
) DEFAULT CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci;

CREATE VIEW status_author AS
(
    SELECT s.status_id, a.screen_name, s.profile_img_url, a.name, s.text, s.created_at
    FROM status s INNER JOIN author a
    ON s.author_id = a.author_id 
);

CREATE TABLE tag (
    tag_id int NOT NULL AUTO_INCREMENT,
    tag varchar(25) NOT NULL,
    PRIMARY KEY (tag_id)
) DEFAULT CHARSET=utf8;

CREATE TABLE tag_alias (
    tag_alias_id int NOT NULL AUTO_INCREMENT,
    tag_id int NOT NULL,
    tag_alias varchar(25) NOT NULL,
    PRIMARY KEY (tag_alias_id),
    FOREIGN KEY (tag_id) REFERENCES tag(tag_id)
) DEFAULT CHARSET=utf8;

CREATE TABLE status_tag_v2 (
    status_tag_v2_id int NOT NULL AUTO_INCREMENT,
    status_id varchar(36) NOT NULL,
    tag_id int NOT NULL,
    PRIMARY KEY (status_tag_v2_id),
    UNIQUE KEY ix_status_tag_v2 (status_id, tag_id)
) DEFAULT CHARSET=utf8;

CREATE TABLE user_notification (
    user_notification_id bigint NOT NULL AUTO_INCREMENT,
    user_guid varchar(36) NOT NULL,
    message varchar(100) NOT NULL,
    created_time timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_notification_id),
    FOREIGN KEY (user_guid) REFERENCES user_profile(guid)
);

ALTER TABLE user_notification ADD INDEX ix_user_notification_time (user_guid, created_time);

CREATE TABLE user_notification_log (
    log_time timestamp DEFAULT CURRENT_TIMESTAMP,
    status_created_at bigint NOT NULL,
    success_count int NOT NULL,
    PRIMARY KEY (log_time)
) DEFAULT CHARSET=utf8;

CREATE VIEW vw_tag_count_max_created AS
(
    SELECT tag.*, CASE WHEN count(*) < 100 THEN count(*) ELSE 100 END AS count, MAX(status_v2.created_at) max_created_at
    FROM tag INNER JOIN status_tag_v2
    ON tag.tag_id = status_tag_v2.tag_id INNER JOIN status_v2
    ON status_tag_v2.status_id = status_v2.status_id
    GROUP BY tag.tag_id, tag.tag
    ORDER BY 4 DESC
);

ALTER TABLE status MODIFY COLUMN media_url varchar(500) NULL;

CREATE INDEX up_status_max_created_at_idx ON user_profile (status_max_created_at);

CREATE INDEX status_created_at_idx ON status_v2 (created_at);

CREATE INDEX unl_created_at ON user_notification_log (status_created_at);

CREATE INDEX un_created_time ON user_notification (created_time);

CREATE INDEX up_created_time ON user_profile (created_time);
