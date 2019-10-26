from pelican import signals
from pelican_micropub.micropub import add_reader, init_micropub_metadata


def register():
    signals.readers_init.connect(add_reader)
    signals.article_generator_context.connect(init_micropub_metadata)
    signals.page_generator_context.connect(init_micropub_metadata)
    signals.static_generator_context.connect(init_micropub_metadata)
