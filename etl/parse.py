from datetime import datetime
from HTMLParser import HTMLParser
# from html.parser import HTMLParser
from bs4 import BeautifulSoup
import requests
import re
import json


html_parser = HTMLParser()
# MAX_NEWLINES = 11


def parse_user(status, users):
    u = {"author_id": status.user.id, "screen_name": '@'+status.user.screen_name, "name": status.user.name,
         "location": status.user.location, "description": status.user.description,
         "profile_img_url": status.user.profile_image_url_https.replace('_normal', '_400x400')}
    users[status.user.id] = u
    if status.quoted_status:
        status = status.quoted_status
        qu = {"author_id": status.user.id, "screen_name": '@'+status.user.screen_name, "name": status.user.name,
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
    url = None if not status.urls else status.urls[0].expanded_url

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
    if 'weekend' in parsed_txt and ('nice' in parsed_txt or 'great' in parsed_txt):
        return None
    elif status.user.screen_name == 'CNBC' and not re.findall("[0-9]+.[0-9]+%", parsed_txt):
        return None
    elif status.user.screen_name == 'CNBCnow' and ('BREAKING' not in parsed_txt or (not url or not media_urls)):
        return None
    elif status.user.screen_name == 'LiveSquawk' and (not re.findall("\$[A-Z]{2,}", parsed_txt) or not media_urls):
        return None
    elif status.user.screen_name == 'SquawkCNBC' and 'LISTEN' in parsed_txt:
        return None
    elif status.user.screen_name == 'OptionsAction' and not re.findall("\$[A-Z]{2,}", parsed_txt):
        return None

    if ext_url and not media_urls:
        media_urls = get_ext_media_url(ext_url, media_urls)

    if status.quoted_status:
        for u in status.quoted_status.urls:  # repeat url process with the retweeted/quoted url
            unquoted_url = requests.utils.unquote(u.expanded_url)
            parsed_quote_txt = parsed_quote_txt.replace(u.url, unquoted_url)
            if 'twitter.com' not in unquoted_url and not unquoted_url.endswith(('.pdf', '.jpg', '.mp4')):
                ext_url = unquoted_url
        tmp_media, parsed_quote_txt = get_twitter_media_urls(status.quoted_status, parsed_quote_txt)
        if tmp_media and not media_urls:
            media_urls = tmp_media
        if ext_url and not media_urls:
            media_urls = get_ext_media_url(ext_url, media_urls)

    tweet_dict = {
        'id': status_id,
        'author_id': author_id,
        'quote_author_id': quote_author_id,
        'timestamp': created_at,
        'unixtime': unixtime,
        'text': parsed_txt,
        'quote_text': parsed_quote_txt,
        'media_urls': media_urls or [],
        'url': url
    }
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

    if response.status_code != 200:
        return urls

    soup = BeautifulSoup(response.text, "html.parser")
    twitter_player = soup.find('meta', attrs={'name': 'twitter:player'})
    twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
    og_image = None

    for meta in soup.findAll("meta"):
        metaname = meta.get('name', '').lower()
        metaprop = meta.get('property', '').lower()
        if 'og:image' == metaname or metaprop.find("og:image")>0:
            og_image = meta['content'].strip()

    if twitter_player:
        urls = [requests.utils.unquote(twitter_player["content"].strip())]
    elif twitter_image:
        urls = [requests.utils.unquote(twitter_image["content"].strip())]
    elif og_image:
        urls = [requests.utils.unquote(og_image)]

    return urls

def get_twitter_media_urls(stat, txt):
    urls = []
    if stat.media is not None and len(stat.media) > 0:
        for u in stat.media:
            url = u.media_url_https
            if 'pscp.tv' in url:
                continue
            for m in stat.media:
                txt = txt.replace(m.url, m.display_url)
            if u.video_info is not None:
                variants = [v for v in stat.media[0].video_info['variants'] if v['content_type'] == 'video/mp4']
                variants = sorted(variants, key=lambda x: int(x['bitrate']), reverse=True)
                url = None if len(variants) == 0 else variants[0]['url'] if len(variants) == 1 else variants[1]['url']
                return [url], txt
            urls.append(url)
    return urls, txt
