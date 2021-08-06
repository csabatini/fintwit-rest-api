from parse import parse_status, parse_user

import MySQLdb
import twitter
import json
import os
import re

cons_key = os.environ['CONSUMER_KEY']
cons_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

def main():
    api = twitter.Api(consumer_key=cons_key,
                    consumer_secret=cons_secret,
                    access_token_key=access_token,
                    access_token_secret=access_token_secret,
                    sleep_on_rate_limit=True,
                    tweet_mode='extended')


    statuses = api.GetListTimeline(list_id='1023639115814920193',
                                count=200,
                                include_rts=False)

    db = MySQLdb.connect(read_default_file='~/.my.cnf', db='fintwit', use_unicode=True, charset="utf8")
    cursor = db.cursor()
    cursor.execute("SET NAMES utf8mb4")
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")


    users = {}
    for s in statuses:
        parse_user(s, users)
    status_kv_pairs = [s for s in map(parse_status, statuses) if s is not None]

    for k, v in users.items():
        cursor.execute("INSERT INTO author (author_id, screen_name, name, profile_img_url, location, description) VALUES (%s, %s, %s, %s, %s, %s) "
                       "ON DUPLICATE KEY UPDATE screen_name=values(screen_name), name=values(name), profile_img_url=values(profile_img_url), location=values(location), description=values(description)",
                       (v['author_id'], v['screen_name'], v['name'], v['profile_img_url'], v['location'], v['description']))
    db.commit()
    for s in status_kv_pairs:
        cursor.execute("INSERT IGNORE INTO status (status_id, author_id, created_at, text, quote_author_id, quote_text) SELECT %s, %s, %s, %s, %s, %s",
                      (s['id'], s['author_id'], s['timestamp'], s['text'], s['quote_author_id'], s['quote_text']))
        for url in s['media_urls']:
            cursor.execute("INSERT IGNORE INTO status_media (status_id, media_url) SELECT %s, %s", (s['id'], url))
    db.commit()
    cursor.close()
    db.close()

if __name__ == '__main__':
    main()