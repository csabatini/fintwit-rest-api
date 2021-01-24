SELECT IFNULL(guid,'') AS guid,IFNULL(push_enabled,'') AS push_enabled,IFNULL(device_token,'') AS device_token,
IFNULL(UNIX_TIMESTAMP(created_time),'') AS created_time,IFNULL(UNIX_TIMESTAMP(status_max_created_at),'') AS status_max_created_at
FROM user_profile
INTO OUTFILE "/var/lib/mysql-files/user_profile.csv"
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';