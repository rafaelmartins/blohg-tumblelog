# -*- coding: utf-8 -*-
"""
    blohg_tumblelog
    ~~~~~~~~~~~~~~~

    A blohg extension that adds some reStructuredText directives to allow the
    creation of tumblelogs using blohg.

    :copyright: (c) 2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from blohg.ext import BlohgExtension
from blohg.rst_parser.directives import SourceCode
from blohg.rst_parser.nodes import opengraph_image
from bs4 import BeautifulSoup
from contextlib import closing
from docutils.parsers.rst import Directive, directives, nodes
from docutils.parsers.rst.directives.body import BlockQuote
from flask import current_app
from pyoembed import oEmbed, PyOembedException
from urllib2 import urlopen

ext = BlohgExtension(__name__)


def text_field(key, value):
    field_name = nodes.field_name(key, key)
    field_body_p = nodes.paragraph(value, value)
    field_body = nodes.field_body('', field_body_p)
    return nodes.field('', field_name, field_body)


def reference_field(key, value, value_text=None):
    field_name = nodes.field_name(key, key)
    field_body_ref = nodes.reference(value, value_text or value, refuri=value)
    field_body_p = nodes.paragraph('', '', field_body_ref)
    field_body = nodes.field_body('', field_body_p)
    return nodes.field('', field_name, field_body)


class LinkDirective(Directive):

    required_arguments = 1  # url
    option_spec = {'maxwidth': directives.nonnegative_int,
                   'maxheight': directives.nonnegative_int,
                   'hide-metadata': directives.flag}

    def run(self):
        if 'maxheight' not in self.options \
           and 'OEMBED_MAXHEIGHT' in current_app.config:
            self.options['maxheight'] = current_app.config['OEMBED_MAXHEIGHT']
        if 'maxwidth' not in self.options \
           and 'OEMBED_MAXWIDTH' in current_app.config:
            self.options['maxwidth'] = current_app.config['OEMBED_MAXWIDTH']
        try:
            data = oEmbed(directives.uri(self.arguments[0]),
                          maxheight=self.options.get('maxheight'),
                          maxwidth=self.options.get('maxwidth'))
        except PyOembedException, err:
            try:
                data = {'type': 'link'}
                with closing(urlopen(directives.uri(self.arguments[0]))) as fp:
                    html = BeautifulSoup(fp.read())
                try:
                    data['title'] = html.head.title.text
                except:
                    pass
            except Exception, err:
                raise self.error('Error in "%s" directive: %s' % (self.name,
                                                                  err))
        except Exception, err:
            raise self.error('Error in "%s" directive: %s' % (self.name, err))

        rv = []

        if data['type'] == 'photo':
            rv.append(nodes.raw('', '<div class="oembed oembed-photo">',
                                format='html'))
            rv.append(nodes.image(data['title'] or '', uri=data['url'],
                                  alt=data['title'] or '',
                                  width=str(data['width']),
                                  height=str(data['height'])))
            rv.append(nodes.raw('', '</div>', format='html'))
        elif data['type'] == 'rich':
            rv.append(nodes.raw('', data['html'], format='html',
                                classes=['oembed', 'oembed-rich']))
        elif data['type'] == 'video':
            rv.append(nodes.raw('', data['html'], format='html',
                                classes=['oembed', 'oembed-video']))
        elif data['type'] == 'link':
            uri = directives.uri(self.arguments[0])
            label = nodes.strong('Link: ', 'Link: ')
            link = nodes.reference(uri, data.get('title', uri), refuri=uri)
            rv.append(nodes.paragraph('', '', label, link))
            return rv

        if 'hide-metadata' in self.options:
            return rv

        rvl = []

        # always use title, if possible.
        if 'title' in data and data['title']:
            rvl.append(text_field('Title', data['title']))

        # description isn't part of the spec. but should be used if provided.
        if 'description' in data:
            rvl.append(text_field('Description', data['description']))

        # always use provider and author, if present, using urls whenever
        # possible, to create links.
        if 'provider_name' in data and data['provider_name']:
            if 'provider_url' in data and data['provider_url']:
                rvl.append(reference_field('Provider',
                                           data['provider_url'],
                                           data['provider_name']))
            else:
                rvl.append(text_field('Content from', data['provider_name']))
        if 'author_name' in data and data['author_name']:
            if 'author_url' in data and data['author_url']:
                rvl.append(reference_field('Author', data['author_url'],
                                           data['author_name']))
            else:
                rvl.append(text_field('Author', data['author_name']))

        # flickr provides a license field
        if 'license' in data and data['license']:
            rvl.append(text_field('License', data['license']))

        rv.append(nodes.field_list('', *rvl))

        # if provided a thumbnail, use it for opengraph
        if 'thumbnail_url' in data:
            rv.append(opengraph_image('', uri=data['thumbnail_url']))

        return rv


class QuoteDirective(BlockQuote):

    option_spec = {'author': directives.unchanged}

    def run(self):
        rv = BlockQuote.run(self)
        if 'author' in self.options:
            author = nodes.raw(self.options['author'],
                               u'<span class="author">— ' +
                               self.options['author'] + '</span>',
                               format='html')
            rv[-1].append(nodes.paragraph('', '', author))
            rv[-1].append(nodes.raw('', '<div class="clear"></div>',
                                    format='html'))
        return rv


class ChatDirective(SourceCode):

    required_arguments = 0
    option_spec = {}

    def run(self):
        if 'linenos' in self.options:
            del self.options['linenos']
        self.arguments = ['irc']
        return SourceCode.run(self)


@ext.setup_extension
def setup_extension(app):
    directives.register_directive('link', LinkDirective)
    directives.register_directive('quote', QuoteDirective)
    directives.register_directive('chat', ChatDirective)
