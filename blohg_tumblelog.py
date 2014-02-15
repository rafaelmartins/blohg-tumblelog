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

    # Imgur
    'http://api.imgur.com/oembed': [
        'http://i.imgur.com/*',
        'http://imgur.com/*',
    ],

    # Twitter
    'https://api.twitter.com/1/statuses/oembed.{format}': [
        'http://www.twitter.com/*/status/*',
        'http://www.twitter.com/*/statuses/*',
        'http://twitter.com/*/status/*',
        'http://twitter.com/*/statuses/*',
        'https://www.twitter.com/*/status/*',
        'https://www.twitter.com/*/statuses/*',
        'https://twitter.com/*/status/*',
        'https://twitter.com/*/statuses/*',
    ],

    # Photobucket
    'http://photobucket.com/oembed': [
        'http://i*.photobucket.com/albums/*',
        'http://gi*.photobucket.com/groups/*',
    ],

    # Wordpress.tv
    'http://wordpress.tv/oembed/': [
        'http://wordpress.tv/*'
    ],

    # IFTTT
    'http://www.ifttt.com/oembed/': [
        'http://ifttt.com/recipes/*',
    ],

    # YouTube
    'http://www.youtube.com/oembed': [
        'http://youtube.com/*',
        'http://www.youtube.com/*',
        'https://youtube.com/*',
        'https://www.youtube.com/*',
        'http://youtu.be/*',
    ],

    # Flickr
    'http://www.flickr.com/services/oembed/': [
        'http://*.flickr.com/photos/*',
        'http://flic.kr/p/*',
    ],

    # Viddler
    'http://www.viddler.com/oembed/': [
        'http://www.viddler.com/v/*',
    ],

    # Qik
    'http://qik.com/api/oembed.{format}': [
        'http://qik.com/video/*',
        'http://qik.com/*',
    ],

    # Revision3
    'http://revision3.com/api/oembed/': [
        'http://*.revision3.com/*',
    ],

    # Hulu
    'http://www.hulu.com/api/oembed.{format}': [
        'http://www.hulu.com/watch/*',
    ],

    # Vimeo
    'http://vimeo.com/api/oembed.{format}': [
        'http://vimeo.com/*',
        'http://vimeo.com/groups/*/videos/*',
    ],

    # CollegeHumor
    'http://www.collegehumor.com/oembed.{format}': [
        'http://www.collegehumor.com/video/*',
    ],

    # Jest
    'http://www.jest.com/oembed.{format}': [
        'http://www.jest.com/embed/*',
    ],

    # Jest
    'http://www.jest.com/oembed.{format}': [
        'http://www.jest.com/embed/*',
    ],

    # Poll Everywhere
    'http://www.polleverywhere.com/services/oembed/': [
        'http://www.polleverywhere.com/polls/*',
        'http://www.polleverywhere.com/multiple_choice_polls/*',
        'http://www.polleverywhere.com/free_text_polls/*',
    ],

    # iFixit
    'http://www.ifixit.com/Embed': [
        'http://www.ifixit.com/Guide/View/*',
    ],

    # SmugMug
    'http://api.smugmug.com/services/oembed/': [
        'http://*.smugmug.com/*',
        'http://*.example.com/*',
    ],

    # Deviantart.com
    'http://backend.deviantart.com/oembed': [
        'http://*.deviantart.com/art/*',
        'http://*.deviantart.com/*#/d*',
        'http://fav.me/*',
        'http://sta.sh/*',
    ],

    # SlideShare
    'http://www.slideshare.net/api/oembed/2': [
        'http://www.slideshare.net/*/*',
    ],

    # chirbit.com
    'http://chirb.it/oembed.json': [
        'http://chirb.it/*',
    ],

    # nfb.ca
    'http://www.nfb.ca/remote/services/oembed/': [
        'http://*.nfb.ca/films/*',
    ],

    # Scribd
    'http://www.scribd.com/services/oembed/': [
        'http://www.scribd.com/doc/*',
    ],

    # Dotsub
    'http://dotsub.com/services/oembed': [
        'http://dotsub.com/view/*',
    ],

    # Animoto
    'http://animoto.com/oembeds/create': [
        'http://animoto.com/play/*',
    ],

    # Rdio
    'http://www.rdio.com/api/oembed/': [
        'http://*.rdio.com/artist/*',
        'http://*.rdio.com/people/*',
    ],

    # MixCloud
    'http://www.mixcloud.com/oembed/': [
        'http://www.mixcloud.com/*/*/',
    ],

    # Screenr
    'http://www.screenr.com/api/oembed.{format}': [
        'http://www.screenr.com/*/',
    ],

    # FunnyOrDie
    'http://www.funnyordie.com/oembed.{format}': [
        'http://www.funnyordie.com/videos/*',
    ],

    # Poll Daddy
    'http://polldaddy.com/oembed/': [
        'http://*.polldaddy.com/s/*',
        'http://*.polldaddy.com/poll/*',
        'http://*.polldaddy.com/ratings/*',
    ],

    # VideoJug
    'http://www.videojug.com/oembed.{format}': [
        'http://www.videojug.com/film/*',
        'http://www.videojug.com/interview/*',
    ],

    # Sapo Videos
    'http://videos.sapo.pt/oembed': [
        'http://videos.sapo.pt/*',
    ],

    # Justin.tv
    'http://api.justin.tv/api/embed/from_url.{json}': [
        'http://www.justin.tv/*',
    ],

    # Official FM
    'http://official.fm/services/oembed.{format}': [
        'http://official.fm/tracks/*',
        'http://official.fm/playlists/*',
    ],

    # HuffDuffer
    'http://huffduffer.com/oembed': [
        'http://huffduffer.com/*/*',
    ],

    # Shoudio
    'http://shoudio.com/api/oembed': [
        'http://shoudio.com/*',
        'http://shoud.io/*',
    ],

    # Moby Picture
    'http://api.mobypicture.com/oEmbed': [
        'http://www.mobypicture.com/user/*/view/*',
        'http://moby.to/*',
    ],

    # 23HQ
    'http://www.23hq.com/23/oembed': [
        'http://www.23hq.com/*/photo/*',
    ],

    # Urtak
    'http://oembed.urtak.com/1/oembed': [
        'http://urtak.com/u/*',
        'http://urtak.com/clr/*',
    ],

    # Cacoo
    'http://cacoo.com/oembed.{format}': [
        'https://cacoo.com/diagrams/*',
    ],

    # Dipity
    'http://www.dipity.com/oembed/timeline/': [
        'http://www.dipity.com/*/*/',
    ],

    # Roomshare
    'http://roomshare.jp/en/oembed.{format}': [
        'http://roomshare.jp/post/*',
        'http://roomshare.jp/en/post/*',
    ],

    # Daily Motion
    'http://www.dailymotion.com/services/oembed': [
        'http://www.dailymotion.com/video/*',
    ],

    # Crowd Ranking
    'http://crowdranking.com/api/oembed.{format}': [
        'http://crowdranking.com/*/*',
    ],

    # CircuitLab
    'https://www.circuitlab.com/circuit/oembed/': [
        'https://www.circuitlab.com/circuit/*',
    ],

    # Geograph Britain and Ireland
    'http://api.geograph.org.uk/api/oembed': [
        'http://*.geograph.org.uk/*',
        'http://*.geograph.co.uk/*',
        'http://*.geograph.ie/*',
        'http://*.wikimedia.org/*_geograph.org.uk_*',
    ],

    # Geograph Germany
    'http://geo.hlipp.de/restapi.php/api/oembed': [
        'http://geo-en.hlipp.de/*',
        'http://geo.hlipp.de/*',
        'http://germany.geograph.org/*',
    ],

    # Geograph Channel Islands
    'http://www.geograph.org.gg/api/oembed': [
        'http://*.geograph.org.gg/*',
        'http://*.geograph.org.je/*',
        'http://channel-islands.geograph.org/*',
        'http://channel-islands.geographs.org/*',
        'http://*.channel.geographs.org/*',
    ],

    # Quiz.biz
    'http://www.quiz.biz/api/oembed': [
        'http://www.quiz.biz/quizz-*.html',
    ],

    # Quizz.biz
    'http://www.quizz.biz/api/oembed': [
        'http://www.quizz.biz/quizz-*.html',
    ],

    # Coub
    'http://coub.com/api/oembed.{format}': [
        'http://coub.com/view/*',
        'http://coub.com/embed/*',
    ],

    # SpeakerDeck
    'https://speakerdeck.com/oembed.json': [
        'http://speakerdeck.com/*/*',
        'https://speakerdeck.com/*/*',
    ],

    # Alpha App Net
    'https://alpha-api.app.net/oembed': [
        'https://alpha.app.net/*/post/*',
        'https://photos.app.net/*/*',
    ],

    # BlipTV
    'http://blip.tv/oembed/': [
        'http://*.blip.tv/*/*',
    ],

    # YFrog
    'http://www.yfrog.com/api/oembed': [
        'http://*.yfrog.com/*',
        'http://yfrog.us/*',
    ],

    # Instagram
    'http://api.instagram.com/oembed': [
        'http://instagram.com/p/*',
        'http://instagr.am/p/*',
    ],

    # SoundCloud
    'https://soundcloud.com/oembed': [
        'http://soundcloud.com/*',
    ],

    # On Aol
    'http://on.aol.com/api': [
        'http://on.aol.com/video/*',
    ],

    # Kickstarter
    'http://www.kickstarter.com/services/oembed': [
        'http://www.kickstarter.com/projects/*',
    ],

    # Ustream
    'http://www.ustream.tv/oembed': [
        'http://*.ustream.tv/*',
        'http://*.ustream.com/*',
    ],

    # GMEP
    'https://gmep.org/oembed.{format}': [
        'https://gmep.org/media/*',
    ],

    # Daily Mile
    'http://api.dailymile.com/oembed?format=json': [
        'http://www.dailymile.com/people/*/entries/*',
    ],

    # Sketchfab
    'http://sketchfab.com/oembed': [
        'http://sketchfab.com/show/*',
        'https://sketchfab.com/show/*',
    ],

    # Meetup
    'https://api.meetup.com/oembed': [
        'http://meetup.com/*',
        'http://meetu.ps/*',
    ],
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
