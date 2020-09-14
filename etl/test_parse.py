from collections import namedtuple

import parse

Status = namedtuple('Status', ['id_str', 'full_text', 'created_at', 'media', 'urls'])
Media = namedtuple('Media', ['url', 'display_url', 'media_url_https'])
URL = namedtuple('URL', ['url', 'expanded_url'])


def test_parses_status_values():
    sample_status = Status(
        '995034521048403973',
        'Liftoff! https://t.co/gtC39uTdw9 https://t.co/aYHHm24Hca',
        'Fri May 11 20:14:51 +0000 2018',
        [Media('https://t.co/aYHHm24Hca', 'pic.twitter.com/KAaESktUJU',
               'https://pbs.twimg.com/media/Dc8SmQhV4AAP6Ji.jpg')],
        [URL('https://t.co/gtC39uTdw9', 'http://spacex.com/webcast')]
    )
    result = parse.parse_status(sample_status)

    assert result['id'] == sample_status.id_str
    assert result['text'] == 'Liftoff! http://spacex.com/webcast pic.twitter.com/KAaESktUJU'  # transformed urls
    assert result['timestamp'] == '2018-05-11 20:14:51'
    assert result['media_url'] == 'https://pbs.twimg.com/media/Dc8SmQhV4AAP6Ji.jpg'


def test_parses_empty_urls():
    sample_status = Status(
        '995037077950545920',
        'Second stage engine cutoff confirmed. Second stage and satellite now in coast phase',
        'Fri May 11 20:25:00 +0000 2018',
        [],
        []
    )
    result = parse.parse_status(sample_status)

    assert result['id'] == sample_status.id_str
    assert result['text'] == sample_status.full_text  # no transformation
    assert result['timestamp'] == '2018-05-11 20:25:00'
    assert result['media_url'] is None
