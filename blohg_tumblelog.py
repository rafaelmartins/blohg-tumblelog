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
from oembed import OEmbedConsumer, OEmbedEndpoint, OEmbedError
from urllib2 import urlopen

ext = BlohgExtension(__name__)

## OEmbed providers
providers = {

    # Youtube
    'http://www.youtube.com/oembed': [
        r'regex:https?://(www\.)?youtube\.com/watch.*',
        r'regex:http://youtu\.be/.*'],

    # Vimeo
    'http://vimeo.com/api/oembed.{format}': [
        r'regex:https?://(www\.)?vimeo\.com/.*'],

    # Rdio
    'http://www.rdio.com/api/oembed/': [
        r'regex:http://www\.rdio\.com/(artist|people)/.*',
        r'regex:http://rd\.io/.*'],

    # Flickr
    'http://www.flickr.com/services/oembed': [
        r'regex:https?://(www\.)?flickr\.com/.*'],

    # Instagram
    'http://api.instagram.com/oembed': [
        r'regex:http://instagr(\.am|am\.com)/p/.*'],

    # Imgur
    'http://api.imgur.com/oembed': [
        r'regex:http://(i\.)?imgur\.com/.*'],

    # Twitter
    'https://api.twitter.com/1/statuses/oembed.{format}': [
        r'regex:https?://(www\.)?twitter\.com/.+?/status(es)?/.*'],

    # DailyMotion
    'http://www.dailymotion.com/services/oembed': [
        r'regex:https?://(www\.)?dailymotion\.com/.*'],

    # SmugMug
    'http://api.smugmug.com/services/oembed/': [
        r'regex:https?://(.+\.)?smugmug\.com/.*'],

    # Hulu
    'http://www.hulu.com/api/oembed.{format}': [
        r'regex:https?://(www\.)?hulu\.com/watch/.*'],

    # Viddler
    'http://lab.viddler.com/services/oembed/': [
        r'regex:https?://(www\.)?viddler\.com/.*'],

    # Qik
    'http://qik.com/api/oembed.{format}': [
        r'regex:http://qik\.com/.*'],

    # Revision3
    'http://revision3.com/api/oembed/': [
        r'regex:http://revision3\.com/.*'],

    # Photobucket
    'http://photobucket.com/oembed': [
        r'regex:http://i.*\.photobucket\.com/albums/.*',
        r'regex:http://gi.*\.photobucket\.com/groups/.*'],

    # Scribd
    'http://www.scribd.com/services/oembed': [
        r'regex:https?://(www\.)?scribd\.com/.*'],

    # Wordpress.tv
    'http://wordpress.tv/oembed/': [
        r'regex:http://wordpress\.tv/.*'],

    # Polldaddy
    'http://polldaddy.com/oembed/': [
        r'regex:https?://(.+\.)?polldaddy\.com/.*'],

    # Funny or die
    'http://www.funnyordie.com/oembed': [
        r'regex:https?://(www\.)?funnyordie\.com/videos/.*'],

    # CollegeHumor
    'http://www.collegehumor.com/oembed.{format}': [
        r'regex:http://www\.collegehumor\.com/video/.*'],

    # Jest
    'http://www.jest.com/oembed.{format}': [
        r'regex:http://www\.jest\.com/(video|embed)/.*'],

    # Poll Everywhere
    'http://www.polleverywhere.com/services/oembed/': [
        r'regex:http://www\.polleverywhere\.com/(polls|multiple_choice_polls|'
        r'free_text_polls)/.*'],

    # SlideShare
    'http://www.slideshare.net/api/oembed/2': [
        r'regex:http://www\.slideshare\.net/[^/]+/.*'],

    # CircuitLab
    'https://www.circuitlab.com/circuit/oembed/': [
        r'regex:https://www\.circuitlab\.com/circuit/.*'],

    # SoundCloud
    'http://soundcloud.com/oembed': [
        r'regex:https?://soundcloud\.com/.*'],
}

## Load OEmbed providers
consumer = OEmbedConsumer()
for endpoint, urls in providers.iteritems():
    consumer.addEndpoint(OEmbedEndpoint(endpoint, urls))


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
            response = consumer.embed(directives.uri(self.arguments[0]),
                                      **self.options)
            data = response.getData()
        except OEmbedError, err:
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
