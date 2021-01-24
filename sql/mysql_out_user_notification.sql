SELECT IFNULL(user_notification_id,'') AS user_notification_id,IFNULL(user_guid,'') AS user_guid,
IFNULL(message,'') AS message,IFNULL(UNIX_TIMESTAMP(created_time),'') AS created_time
FROM user_notification
INTO OUTFILE "/var/lib/mysql-files/user_notification.csv"
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';