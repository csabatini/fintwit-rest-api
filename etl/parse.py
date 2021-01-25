from datetime import datetime
from HTMLParser import HTMLParser
# from html.parser import HTMLParser
from bs4 import BeautifulSoup
import requests
import re


html_parser = HTMLParser()
# MAX_NEWLINES = 11


def parse_user(status, users):
    u = {"author_id": status.user.id, "screen_name": '@'+status.user.screen_name, "name": status.user.screen_name,
         "location": status.user.location, "description": status.user.description,
         "profile_img_url": status.user.profile_image_url_https.replace('_normal', '_400x400')}
    users[status.user.id] = u
    if status.quoted_status:
        status = status.quoted_status
        qu = {"author_id": status.user.id, "screen_name": '@'+status.user.screen_name, "name": status.user.screen_name,
              "location": status.user.location, "description": status.user.description,
              "profile_img_url": status.user.profile_image_url_https.replace('_normal', '_400x400')}
        users[status.user.id] = qu

def parse_status(status):
    status_id = status.id
    author_id = status.user.id
    quote_author_id = status.quoted_status.user.id if status.quoted_status else None
    created_at = \
        datetime.strptime(status.created_at, '%a %b %d %H:%M:%S +0000 %Y').strftime('%Y-%m-%d %H:%M:%S')
    unixtime = \
        int((datetime.strptime(status.created_at, '%a %b %d %H:%M:%S +0000 %Y') - datetime(1970, 1, 1)).total_seconds())
    parsed_txt = \
        html_parser.unescape(status.retweeted_status.full_text if status.retweeted_status else status.full_text)
    parsed_quote_txt = \
        html_parser.unescape(status.quoted_status.full_text) if status.quoted_status else None
    # if parsed_txt.count('\n') > MAX_NEWLINES:
    #     parsed_txt = parsed_txt.replace('\n', ' ')
    # if status.quoted_status and parsed_quote_txt.count('\n') > MAX_NEWLINES:
    #     parsed_quote_txt = parsed_quote_txt.replace('\n', ' ')

    ext_url = None
    if status.quoted_status:
        for u in status.quoted_status.urls:
            unquoted_url = requests.utils.unquote(u.expanded_url)
            parsed_quote_txt = parsed_quote_txt.replace(u.url, unquoted_url)
            if 'twitter.com' not in unquoted_url and not unquoted_url.endswith(('.pdf', '.jpg', '.mp4')):
                ext_url = unquoted_url
    for u in status.urls:
        unquoted_url = requests.utils.unquote(u.expanded_url)
        parsed_txt = parsed_txt.replace(u.url, unquoted_url)
        if 'twitter.com' not in unquoted_url and not unquoted_url.endswith(('.pdf', '.jpg', '.mp4')):
            ext_url = unquoted_url

    # get the media from the original tweet
    media_urls, parsed_txt = get_twitter_media_urls(status, parsed_txt)
    if ext_url and not media_urls:
        media_urls = get_ext_media_url(ext_url, media_urls)

    if status.quoted_status:
        status = status.quoted_status
        for u in status.urls:  # repeat url process with the retweeted/quoted url
            unquoted_url = requests.utils.unquote(u.expanded_url)
            parsed_quote_txt = parsed_quote_txt.replace(u.url, unquoted_url)
            if 'twitter.com' not in unquoted_url and not unquoted_url.endswith(('.pdf', '.jpg', '.mp4')):
                ext_url = unquoted_url

    # possibly override the original media with retweet/quote media
    if status.id != status_id:
        tmp_media, parsed_quote_txt = get_twitter_media_urls(status, parsed_quote_txt)
        if tmp_media:
            media_urls = tmp_media
        elif ext_url:
            tmp_media = get_ext_media_url(ext_url, media_urls)
            if tmp_media:
                media_urls = tmp_media
    tweet_dict = {
        'id': status_id,
        'author_id': author_id,
        'quote_author_id': quote_author_id,
        'timestamp': created_at,
        'unixtime': unixtime,
        'text': parsed_txt,
        'quote_text': parsed_quote_txt,
        'media_urls': media_urls
    }

    if status.user.screen_name == 'CNBC' and not re.findall("[0-9]+.[0-9]+%", parsed_txt):
        return None
    elif status.user.screen_name == 'LiveSquawk' and not re.findall("\$[A-Z]{2,}", parsed_txt):
        return None
    else:
        return tweet_dict

def get_ext_media_url(ext_url, media_urls):
    urls = media_urls 
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'referrer': 'https://google.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Pragma': 'no-cache'
    }
    try:
        response = requests.get(ext_url, headers=headers, timeout=15)
    except Exception as e:
        return None

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        twitter_player = soup.find('meta', attrs={'name': 'twitter:player'})
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        og_image = soup.find('meta', attrs={'property': 'og:image'})

        if twitter_player:
            urls = [requests.utils.unquote(twitter_player["content"].strip())]
        elif twitter_image:
            urls = [requests.utils.unquote(twitter_image["content"].strip())]
        elif og_image:
            urls = [requests.utils.unquote(og_image["content"].strip())]
    return urls

def get_twitter_media_urls(stat, txt):
    urls = []
    if stat.media is not None and len(stat.media) > 0:
        for u in stat.media:
            url = u.media_url_https
            for m in stat.media:
                txt = txt.replace(m.url, m.display_url)
            if u.video_info is not None:
                variants = [v for v in stat.media[0].video_info['variants'] if v['content_type'] == 'video/mp4']
                variants = sorted(variants, key=lambda x: int(x['bitrate']), reverse=True)
                url = None if len(variants) == 0 else variants[0]['url'] if len(variants) == 1 else variants[1]['url']
                return [url], txt
            urls.append(url)
    return urls, txt
