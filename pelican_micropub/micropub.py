import json
import mf2util
import markdown
import datetime

from pelican.readers import BaseReader
from pelican_micropub.notedown import convert2html, extract_hashtags, \
    extract_mentions, extract_links


# Post type is one of:
#
# 'org', 'person', 'event', 'rsvp', 'invite', 'reply', 'repost', 'like',
# 'photo', 'article', 'note', 'follow'
#
# But we don't support all that.  Basically we support articles and
# note types which are all variations of h-entry
supported_post_types = ['reply', 'repost', 'like', 'photo', 'article', 'note']

# The default default category
default_category = 'miscellanea'


class MicropubReader(BaseReader):
    enabled = True
    file_extensions = ['mp']

    def read(self, filename):
        post = json.loads(read_whole_file(filename))
        html, metadata = micropub2pelican(post, self.settings)
        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)
        return html, adjust_metadata(parsed, text_content(post))


class NotedownReader(BaseReader):
    enabled = True
    file_extensions = ['nd']

    def read(self, filename):
        contents = read_whole_file(filename)

        meta_text = contents.split("\n\n", 2)
        metadata = extract_markdown_metadata(meta_text[0] + "\n\n")

        post_type = infer_post_type(metadata, meta_text[1])
        metadata['post_type'] = post_type
        category = get_category(self.settings, post_type)
        if category:
            metadata['category'] = category

        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)

        return notedown(meta_text[1], self.settings),\
            adjust_metadata(parsed, meta_text[1])


def adjust_metadata(parsed, text):
    if text is None:
        return parsed

    if parsed.get('title') is None:
        parsed['title'] = text

    hashtags = extract_hashtags(text)
    if hashtags:
        parsed['hashtags'] = hashtags

    mentions = extract_mentions(text)
    if mentions:
        parsed['mentions'] = mentions

    links = extract_links(text)
    if links:
        parsed['links'] = links

    return parsed


def infer_post_type(metadata, content):
    for prop, implied_type in [
        ('in_reply_to', 'reply'),
        ('repost_of', 'repost'),
        ('like_of', 'like'),
        ('photos', 'photo'),
        ('photo', 'photo'),
    ]:
        if metadata.get(prop) is not None:
            return implied_type
    if content and metadata.get('title') is not None:
        return 'article'
    return 'note'


def extract_markdown_metadata(metadata_text):
    md = markdown.Markdown(extensions=['meta'])
    md.convert(metadata_text)

    metadata = {}
    for key, value in md.Meta.items():
        metadata[key] = "\n".join(value)
    return metadata


def init_micropub_metadata(generator, metadata):
    # If it's from the micropub server, the key is 'photo',
    # and there's nothing to do here (though we will process
    # the data a bit later)
    #
    # For legacy reasons (raw notedown metadata) we also
    # support 'photos' and 'photos_alt', and we convert it
    # to a normalized form
    if 'photos' in metadata:
        metadata['photo'] = []
        photos = metadata['photos'].split(',')
        photos_alt = []
        if 'photos_alt' in metadata:
            photos_alt = metadata['photos_alt'].split(',')
        for index, photo in enumerate(photos):
            if photos_alt:
                metadata['photo'].append({'value': photo,
                                          'alt': photos_alt[index]})
            else:
                metadata['photo'].append({'value': photo})

    # these headers normally come from micropub, and will hence be lists,
    # but when they come from a traditional Markdown file (where they are
    # strings). We need to turn the values into lists
    for header in get_content_headers(generator.settings):
        if header not in metadata:
            metadata[header] = []
        elif isinstance(metadata[header], str):
            metadata[header] = metadata[header].split(',')


def get_content_headers(settings):
    return settings.get('WEBMENTIONS_CONTENT_HEADERS',
                        ['like_of', 'repost_of', 'in_reply_to', 'bookmark_of'])


def micropub2pelican(post, settings={}):
    post_type = mf2util.post_type_discovery(post)
    if post_type not in supported_post_types:
        raise Exception(f'{post_type} not among supported post types')

    entry = mf2util.interpret_entry({'items': [post]}, '')
    if not entry:
        raise Exception('Could not interpret parsed entry')

    return get_html(settings, post, post_type), \
        get_metadata(settings, entry, post, post_type)


def get_metadata(settings, entry, post, post_type):
    slug = get_slug(post)
    published = get_single_prop(post, 'published')
    updated = get_single_prop(post, 'updated') or published
    metadata = {
        'slug': slug,
        'tags': post['properties'].get('category', []),
        'date': published,
        'modified': updated,
        'title': entry.get('name') or entry.get('content-plain'),
        'summary': entry.get('summary'),
        'in_reply_to': get_url_prop(entry, 'in-reply-to'),
        'like_of': get_url_prop(entry, 'like-of'),
        'repost_of': get_url_prop(entry, 'repost-of'),
        'bookmark_of': get_url_prop(entry, 'bookmark-of'),
        'mp_syndicate_to': post['properties'].get('mp-syndicate-to', []),
        'post_type': post_type
    }

    category = get_category(settings, post_type)
    if category:
        metadata['category'] = category

    if 'author' in entry:
        metadata['author'] = entry['author']['name']
        metadata['author-full'] = entry['author']

    if 'photo' in post['properties']:
        metadata['photo'] = []
        for photo in post['properties']['photo']:
            if isinstance(photo, dict):
                metadata['photo'].append(photo)
            elif isinstance(photo, str):
                metadata['photo'].append({'value': photo})

    return metadata


def get_single_prop(entry, prop):
    p = entry['properties']
    if prop in p and p[prop]:
        return p[prop][0]
    else:
        return None


def get_url_prop(entry, prop):
    return [x['url'] for x in entry.get(prop, [])]


def get_slug(entry):
    props = entry['properties']
    return props.get('mp-slug', [get_default_slug(props)])[0]


def get_default_slug(props):
    datestr = props['published'][0]
    try:
        date = datetime.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        date = datetime.datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S-%f')
    return '{published:%H}{published:%M}{published:%S}'.format(published=date)


def get_category(settings, post_type):
    category_map = settings.get('MICROPUB_CATEGORY_MAP', {})
    if post_type in category_map:
        return category_map[post_type]
    return None


def get_html(settings, post, post_type):
    html = html_content(post)
    if html:
        return html

    plain = text_content(post)
    if not plain:
        return ''

    if post_type == 'article':
        return markdown.markdown(plain)
    else:
        return notedown(plain, settings)


def html_content(mp_entry):
    content = mp_entry['properties'].get('content', None)
    if not content or \
       isinstance(content[0], str) or \
       not isinstance(content[0], dict) or \
       'html' not in content[0]:
        return ''

    return content[0]['html']


def text_content(mp_entry):
    content = mp_entry['properties'].get('content', None)
    if not content or \
       isinstance(content[0], dict) or \
       not isinstance(content[0], str):
        return ''

    return content[0]


def notedown(text, settings):
    url_linking_disabled = settings.get('NOTEDOWN_DISABLE_URL_AUTOLINKING')
    hashtag_template = settings.get('NOTEDOWN_HASHTAG_TEMPLATE')
    mention_template = settings.get('NOTEDOWN_MENTION_TEMPLATE')
    return convert2html(text, not url_linking_disabled, hashtag_template,
                        mention_template)


def read_whole_file(filename):
    with open(filename, 'r') as content_file:
        content = content_file.read()
    return content


def add_reader(readers):
    for ext in MicropubReader.file_extensions:
        readers.reader_classes[ext] = MicropubReader

    for ext in NotedownReader.file_extensions:
        readers.reader_classes[ext] = NotedownReader
