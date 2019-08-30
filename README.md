# Micropub Reader for Pelican

A pelican plugin for reading json-formatted [micropub][0] entries, like the
ones produced from [micropub-git-server][1].

The micropub-git-server will commit plain, minimally processed JSON files,
representing micropub entries, into a configured location of your choice.
If that configured location is part of a pelican content folder, then you
can use this plugin to display those entries in a pelican blog.

## Background

A micropub server allows users to post content on their own website by means
of an associated micropub client, and forms one part of the [IndieWeb][2]
ecosystem, a decentralized alternative to corporate social networks, based
on open standards, where users post and *control* their own content.

Micropub is based heavily on the idea of [microformats][4] - little pieces
of metadata sprinkled in an HTML document that give some clues as to what
the content is supposed to represent.  Examples of different types of
content include:

* h-entry - an authored bit of online content, like a blog post, tweet,
  comment or reply.
* h-event - a calendar event
* h-card - contact information about a person

Please consult the [wiki][3] for information on the IndieWeb and how to
join.

## Article Types and Category

The h-entry type is by far the most common type of content, and the only one
that pelican-micropub supports at this time.  The IndieWeb community defines
several different types of h-entry:

* [articles][5] (not to be confused with pelican articles), otherwise known as blog posts
* short, titleless [notes][6], similar to tweets or status updates
* [bookmarks][7]
* [replies][8]
* [likes][9]

The pelican micropub plugin will identify the type of h-entry and assign the
pelican article to a category based on the classification.  This means that
if you are using the concept of categories for some other form of
classification, then this plugin will not work for you out of the box.

By way of advice, I have found that categories, as a general classification
scheme, are really only useful when applied to blog entries, or what the
IndieWeb community calls articles; the whole point of things like notes and
likes is that they are meant to be quick, one off pieces of content, and
categorizing them tends to get in the way of that.

For categorizing pelican articles within each category, I have found the
[subcategory][10] plugin useful.

[0]: https://www.w3.org/TR/micropub/
[1]: https://github.com/drivet/micropub-git-server
[2]: https://indieweb.org/IndieWeb
[3]: https://indieweb.org
[4]: http://microformats.org/
[5]: https://indieweb.org/article
[6]: https://indieweb.org/note
[7]: https://indieweb.org/bookmark
[8]: https://indieweb.org/reply
[9]: https://indieweb.org/like
[10]: https://github.com/getpelican/pelican-plugins/tree/master/subcategory
