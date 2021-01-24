#!/bin/bash
APP_DIR=/home/www/flask_project/sql
HOME=/home/webapp

function run_export_query() {
    TABLE=$1
    QUERY=$2
    OUTFILE=/var/lib/mysql-files/${TABLE}.csv
    if [[ -f $OUTFILE ]]; then
        sudo rm $OUTFILE
    fi
    mysql --defaults-extra-file=$HOME/.my.cnf --database trumptweets < $QUERY
    mkdir -p $HOME/mysql/export/$TABLE/
    cp $OUTFILE $HOME/mysql/export/$TABLE/table.csv
    gzip -f $HOME/mysql/export/$TABLE/table.csv
    sudo chown -R webapp:webapp $HOME
}

# run table csv exports
run_export_query user_notification $APP_DIR/mysql_out_user_notification.sql
run_export_query user_profile $APP_DIR/mysql_out_user_profile.sql

# run database backup
mkdir -p $HOME/mysql/backup/
mysqldump --defaults-extra-file=$HOME/.my.cnf trumptweets | gzip -f > $HOME/mysql/backup/trumptweets_`date +%a`.sql.gz

# transfer to s3
aws s3 cp --recursive --sse AES256 $HOME/mysql/ s3://production-slickmobile-trumptweets-data/