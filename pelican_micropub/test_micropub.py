from pelican_micropub.micropub import html_content, \
    text_content, micropub2pelican


def test_fetches_html():
    mp_entry = {
        "type": ["h-entry"],
        'properties': {
            'content': [{
                'html': '<p>hello</p>',
            }]
        }
    }
    assert html_content(mp_entry) == '<p>hello</p>'


def test_does_not_fetch_html():
    mp_entry = {
        "type": ["h-entry"],
        'properties': {
            'content': ['hello']
        }
    }
    assert html_content(mp_entry) is None


def test_does_not_fetch_text():
    mp_entry = {
        "type": ["h-entry"],
        'properties': {
            'content': [{
                'html': '<p>hello</p>',
            }]
        }
    }
    assert text_content(mp_entry) is None


def test_fetch_text():
    mp_entry = {
        "type": ["h-entry"],
        'properties': {
            'content': ['hello']
        }
    }
    assert text_content(mp_entry) == 'hello'


def test_should_read_note_text():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"]
        }
    }
    settings = {
        'MICROPUB_CATEGORY_MAP': {
            'note': 'notes'
        }
    }
    html, metadata = micropub2pelican(post, settings)
    assert html == 'test<br/>post'


def test_should_obey_hashtag_template():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["hello #blah"],
            "published": ["2019-08-29T02:03:05.429827"]
        }
    }
    settings = {
        'NOTEDOWN_HASHTAG_TEMPLATE': 'http://stuff.com/{hashtag}'
    }
    html, metadata = micropub2pelican(post, settings)
    assert html == 'hello <a href="http://stuff.com/blah">#blah</a>'


def test_should_read_reply_note_text():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "in-reply-to": ['http://example.com/stuff'],
            "published": ["2019-08-29T02:03:05.429827"]
        }
    }
    settings = {
        'MICROPUB_CATEGORY_MAP': {
            'reply': 'notes'
        }
    }
    html, metadata = micropub2pelican(post, settings)
    assert html == 'test<br/>post'


def test_should_read_article_text():
    post = {
        "type": ["h-entry"],
        "properties": {
            "name": "Awesome post",
            "content": ["test *post*"],
            "published": ["2019-08-29T02:03:05.429827"]
        }
    }
    html, metadata = micropub2pelican(post)
    assert html == '<p>test <em>post</em></p>'


def test_should_supply_default_category():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"]
        }
    }
    settings = {
        'MICROPUB_DEFAULT_CATEGORY': 'defcat'
    }
    html, metadata = micropub2pelican(post, settings)
    assert metadata['category'] == 'defcat'


def test_should_supply_default_default_category():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"]
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['category'] == 'miscellanea'


def test_should_read_slug_if_present():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "mp-slug": ['the_slug'],
            "published": ["2019-08-29T02:03:05.429827"]
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['slug'] == 'the_slug'


def test_should_use_default_slug():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"]
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['slug'] == '020305'


def test_should_set_tags():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "category": ['tag1', 'tag2'],
            "published": ["2019-08-29T02:03:05.429827"]
        }
    }
    html, metadata = micropub2pelican(post)
    print(str(metadata))
    assert metadata['tags'] == ['tag1', 'tag2']


def test_should_set_date():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"]
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['date'] == '2019-08-29T02:03:05.429827'


def test_should_set_updated():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"],
            "updated": ["2019-08-30T03:05:06.429827"],
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['modified'] == '2019-08-30T03:05:06.429827'


def test_should_set_in_reply_to():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"],
            "in-reply-to": ['http://example.com']
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['in-reply-to'] == ['http://example.com']


def test_should_set_like_of():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"],
            "like-of": ['http://example.com']
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['like-of'] == ['http://example.com']


def test_should_set_repost_of():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"],
            "repost-of": ['http://example.com']
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['repost-of'] == ['http://example.com']


def test_should_set_bookmark_of():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"],
            "bookmark-of": ['http://example.com']
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['bookmark-of'] == ['http://example.com']


def test_should_set_summary_from_string():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"],
            "summary": ['this is a summary']
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['summary'] == 'this is a summary'


def test_should_set_summary_from_object():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"],
            "summary": [{'value': 'this is a summary'}]
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['summary'] == 'this is a summary'


def test_should_set_title_from_name():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"],
            "name": ['awesome name']
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['title'] == 'awesome name'


def test_should_set_title_from_content():
    post = {
        "type": ["h-entry"],
        "properties": {
            "content": ["test\npost"],
            "published": ["2019-08-29T02:03:05.429827"]
        }
    }
    html, metadata = micropub2pelican(post)
    assert metadata['title'] == 'test\npost'
