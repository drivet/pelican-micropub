import re

# RE to find @person references
mention_re = re.compile("(^|\s)([＠@]{1}([^\s#<>[\]|{}]+))", re.UNICODE)


# RE to find #hashtags
hashtag_re = re.compile("(^|\s)([＃#]{1}(\w+))", re.UNICODE)


# RE to find links
link_re = re.compile("(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)", re.UNICODE)


# Only match whitespace that has whitespace behind it (lookbehind)
multispace_re = re.compile(r"(?<=\s)\s")


def extract_hashtags(text):
    return [m[2] for m in hashtag_re.findall(text)]


def extract_mentions(text):
    return [m[2] for m in mention_re.findall(text)]


def extract_links(text):
    return link_re.findall(text)


def convert2html(text, url_linking=False,
                 hashtag_template=None,
                 mention_template=None):
    if url_linking:
        text = link_re.sub(r'<a href="\1">\1</a>', text)

    if hashtag_template:
        text = hashtag_re.sub(r'\1<a href="' +
                              hashtag_template.format(hashtag=r'\3') +
                              r'">\2</a>', text)

    if mention_template:
        text = mention_re.sub(r'\1<a href="' +
                              mention_template.format(mention=r'\3') +
                              r'">\2</a>', text)

    # we'll say, somewhat arbitrarily, that tabs are replaced by four spaces
    text = text.replace('\t', '    ')

    # replace newlines and carriage returns with HTML breaks
    text = text.replace('\r\n', '<br/>')
    text = text.replace('\n', '<br/>')

    # replace more than two spaces with escape codes
    text = multispace_re.sub('&nbsp;', text)
    
    return text
