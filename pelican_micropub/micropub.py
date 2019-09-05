import json
import mf2util
import markdown
import datetime

from pelican import signals
from pelican.readers import BaseReader
from pelican_micropub.notedown import convert2html


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
        return html, parsed


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
    category = get_category(settings, post_type)
    slug = get_slug(post)
    published = get_single_prop(post, 'published')
    updated = get_single_prop(post, 'updated') or published
    metadata = {
        'category': category,
        'slug': slug,
        'tags': post['properties'].get('category', []),
        'date': published,
        'modified': updated,
        'title': entry.get('name') or entry.get('content-plain'),
        'summary': entry.get('summary'),
        'in-reply-to': get_url_prop(entry, 'in-reply-to'),
        'like-of': get_url_prop(entry, 'like-of'),
        'repost-of': get_url_prop(entry, 'repost-of'),
        'bookmark-of': get_url_prop(entry, 'bookmark-of')
    }

    if 'author' in entry:
        metadata['author'] = entry['author']['name']
        metadata['author-full'] = entry['author']

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
    date = datetime.datetime.strptime(props['published'][0],
                                      '%Y-%m-%dT%H:%M:%S.%f')
    return '{published:%H}{published:%M}{published:%S}'.format(published=date)


def get_category(settings, post_type):
    category_map = settings.get('MICROPUB_CATEGORY_MAP', {})
    category = settings.get('MICROPUB_DEFAULT_CATEGORY', default_category)
    if post_type in category_map:
        category = category_map[post_type]
    return category


def get_html(settings, post, post_type):
    html = html_content(post)
    if html:
        return html

    plain = text_content(post)
    if not plain:
        return None

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
        return None

    return content[0]['html']


def text_content(mp_entry):
    content = mp_entry['properties'].get('content', None)
    if not content or \
       isinstance(content[0], dict) or \
       not isinstance(content[0], str):
        return None

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


def register():
    signals.readers_init.connect(add_reader)
