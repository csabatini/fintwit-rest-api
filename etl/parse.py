from datetime import datetime
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import requests

html_parser = HTMLParser()


def parse_status(status):
    status_id = status.id_str
    #print status_id
    if status_id.decode('utf8') != '1304603325942214657':
        return None
    retweet_user = None
    created_at = \
        datetime.strptime(status.created_at, '%a %b %d %H:%M:%S +0000 %Y').strftime('%Y-%m-%d %H:%M:%S')
    unixtime = \
        int((datetime.strptime(status.created_at, '%a %b %d %H:%M:%S +0000 %Y') - datetime(1970, 1, 1)).total_seconds())
    parsed_txt = \
        html_parser.unescape(status.retweeted_status.full_text if status.retweeted_status else status.full_text)
    ext_url = None
    for u in status.urls:
        unquoted_url = requests.utils.unquote(u.expanded_url)
        parsed_txt = parsed_txt.replace(u.url, unquoted_url)
        if 'twitter.com' not in unquoted_url and not unquoted_url.endswith(('.pdf', '.jpg', '.mp4')):
            ext_url = unquoted_url

    # get the media from the original tweet
    print status.media[0]
    media_url, parsed_txt = get_twitter_media_url(status, parsed_txt)
    if ext_url and not media_url:
        media_url, parsed_txt = get_ext_media_url(ext_url, parsed_txt)

    if status.retweeted_status:
        retweet_user = status.retweeted_status.user
        status = status.retweeted_status
        parsed_txt = 'RT @' + retweet_user.screen_name + ': ' + parsed_txt
    elif status.quoted_status:
        user = status.quoted_status.user.screen_name
        parsed_txt = \
            parsed_txt + "\n\n" + "@" + user + ": \"" + html_parser.unescape(status.quoted_status.full_text) + "\""
        status = status.quoted_status

    for u in status.urls:  # repeat url process with the retweeted/quoted url
        unquoted_url = requests.utils.unquote(u.expanded_url)
        parsed_txt = parsed_txt.replace(u.url, unquoted_url)
        if 'twitter.com' not in unquoted_url and not unquoted_url.endswith(('.pdf', '.jpg', '.mp4')):
            ext_url = unquoted_url

    # possibly override the original media with retweet/quote media
    if status.id_str != status_id:
        tmp_media, parsed_txt = get_twitter_media_url(status, parsed_txt)
        if tmp_media:
            media_url = tmp_media
        if ext_url and not tmp_media:
            tmp_media, parsed_txt = get_ext_media_url(ext_url, parsed_txt)
            if tmp_media:
                media_url = tmp_media
    tweet_dict = {
        'id': status_id,
        'timestamp': created_at,
        'unixtime': unixtime,
        'text': parsed_txt,
        'media_url': media_url
    }
    whitelist = \
        ['TeamTrump', 'TrumpWarRoom', 'Mike_Pence', 'GOP', 'IvankaTrump', 'DonaldJTrumpJr', 'EricTrump']
    if retweet_user and (retweet_user.screen_name in whitelist or
                         'rep' in retweet_user.screen_name.lower() or
                         'sen' in retweet_user.screen_name.lower()):
        return tweet_dict
    elif retweet_user and media_url and retweet_user.verified:
        return tweet_dict
    elif retweet_user and ext_url and media_url:
        return tweet_dict
    elif not retweet_user:
        return tweet_dict
    else:
        return None


def get_ext_media_url(ext_url, txt):
    url = None
    response = requests.get(ext_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        og_image = soup.find("meta", property="og:image")
        if og_image:
            url = requests.utils.unquote(og_image["content"].strip())
        og_title = soup.find("meta", property="og:title")
        if og_title:
            clean_title = html_parser.unescape(og_title["content"].strip())
            if clean_title not in txt:
                txt = txt + "\n\n\"" + clean_title + "\""
    return url, txt


def get_twitter_media_url(stat, txt):
    url = None
    if stat.media is not None and len(stat.media) > 0:
        url = stat.media[0].media_url_https
        if stat.media[0].video_info is not None:
            variants = [v for v in stat.media[0].video_info['variants'] if v['content_type'] == 'video/mp4']
            variants = sorted(variants, key=lambda x: int(x['bitrate']), reverse=True)
            if len(variants) > 0:
                url = variants[0]['url']
        for m in stat.media:
            txt = txt.replace(m.url, m.display_url)
    return url, txt
