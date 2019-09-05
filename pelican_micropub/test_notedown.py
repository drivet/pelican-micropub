from pelican_micropub.notedown import extract_hashtags, \
    extract_mentions, extract_links, convert2html


def test_should_extract_a_hashtag():
    hashtags = extract_hashtags('hello #stuff')
    assert len(hashtags) == 1
    assert hashtags[0] == 'stuff'


def test_should_extract_multiple_hashtags():
    hashtags = extract_hashtags('hello #stuff goodbye #bother')
    assert len(hashtags) == 2
    assert hashtags[0] == 'stuff'
    assert hashtags[1] == 'bother'


def test_should_extract_no_hashtags():
    hashtags = extract_hashtags('hello @stuff')
    assert len(hashtags) == 0


def test_should_extract_one_mention():
    mentions = extract_mentions('hello @stuff')
    assert len(mentions) == 1
    assert mentions[0] == 'stuff'


def test_should_extract_multiple_mentions():
    mentions = extract_mentions('hello @stuff goodbye @bother')
    assert len(mentions) == 2
    assert mentions[0] == 'stuff'
    assert mentions[1] == 'bother'


def test_should_extract_no_mentions():
    hashtags = extract_mentions('hello #stuff')
    assert len(hashtags) == 0


def test_should_extract_one_link():
    links = extract_links('http://www.example.com')
    assert len(links) == 1
    assert links[0] == 'http://www.example.com'


def test_should_extract_multiple_links():
    links = extract_links('hello http://www.example.com goodbye ' +
                          'https://blah.com/qwerty')
    assert len(links) == 2
    assert links[0] == 'http://www.example.com'
    assert links[1] == 'https://blah.com/qwerty'


def test_should_extract_no_links():
    links = extract_links('hello h://www.example.com goodbye ' +
                          'h://blah.com/qwerty')
    assert len(links) == 0


def test_tabs_should_be_four_spaces():
    assert convert2html('hello\tdolly') == 'hello &nbsp;&nbsp;&nbsp;dolly'


def test_two_spaces_or_more_get_converted():
    assert convert2html('hello  there') == 'hello &nbsp;there'
    assert convert2html('hello   there') == 'hello &nbsp;&nbsp;there'


def test_one_space_does_not_get_converted():
    assert convert2html('hello there') == 'hello there'


def test_newline_and_cr_converted_to_br():
    assert convert2html('hello\nthere') == 'hello<br/>there'
    assert convert2html('hello\r\nthere') == 'hello<br/>there'
    assert convert2html('hello\r\n\nthere') == 'hello<br/><br/>there'


def test_links_not_autolinked_if_url_linking_off():
    ptext = 'hello http://example.com'
    htext = convert2html(ptext, False)
    print(htext)
    assert htext == 'hello http://example.com'


def test_links_autolinked_if_url_linking_on():
    ptext = 'hello http://example.com'
    htext = convert2html(ptext, True)
    assert htext == 'hello <a href="http://example.com">http://example.com</a>'


def test_hashtag_not_processed_if_template_empty():
    ptext = 'hello #stuff'
    htext = convert2html(ptext, False, None)
    assert htext == 'hello #stuff'


def test_hashtag_processed_if_template_given():
    ptext = 'hello #stuff'
    htext = convert2html(ptext, False, 'https://twitter/hashtags/{hashtag}')
    assert htext == 'hello <a href="https://twitter/hashtags/stuff">#stuff</a>'


def test_mention_not_processed_if_template_empty():
    ptext = 'hello @stuff'
    htext = convert2html(ptext, False, None, None)
    assert htext == 'hello @stuff'


def test_mention_processed_if_template_given():
    ptext = 'hello @stuff'
    htext = convert2html(ptext, False, None, 'https://twitter/users/{mention}')
    assert htext == 'hello <a href="https://twitter/users/stuff">@stuff</a>'


def test_should_convert_all_the_things():
    ptext = 'hello\tdolly #stuff @blah http://me.com   nice'
    htext = convert2html(ptext, True,
                         'https://twitter/hashtags/{hashtag}',
                         'https://twitter/users/{mention}')
    print(htext)
    assert htext == 'hello &nbsp;&nbsp;&nbsp;dolly ' + \
        '<a href="https://twitter/hashtags/stuff">#stuff</a> ' + \
        '<a href="https://twitter/users/blah">@blah</a> ' + \
        '<a href="http://me.com">http://me.com</a> &nbsp;&nbsp;nice'
