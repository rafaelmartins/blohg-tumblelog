blohg-tumblelog
===============

A blohg extension with reStructuredText directives to run a tumblelog.


How to install
~~~~~~~~~~~~~~

Install it globally using ``pip``::

    $ pip install blohg-tumblelog

Or copy ``blohg_tumblelog.py`` to the ``ext/`` directory of your blog's
repository.

To enable it, add ``tumblelog`` to the ``EXTESIONS`` list in ``config.yaml``.

If you are running the extension from the blog repository, you'll need to
add ``embedded_extensions = True`` to the ``create_app()`` call in your
``WSGI`` endpoint.


Directives
~~~~~~~~~~

link
----

This directive is used to share links. It will embed the content of the link to
the post automatically, if the provided link is from a service that supports
the `oEmbed <http://oembed.com/>`_ protocol. If it isn't, and the link is from
a HTML page, it will include the link with the title of the page to the post.
Otherwise it will just include the raw link to the post.

Usage example:

.. sourcecode:: rst

   .. link:: http://www.youtube.com/watch?v=gp30v6XMxBg


quote
-----

This directive is used to share quotes. It will create a ``blockquote`` element
with the quote and add a signature with the author name, if provided.

Usage example:

.. sourcecode:: rst

   .. quote::
      :author: Myself

      This is a random quote!


chat
----

This directive is used to share chat logs. It will add a div with the chat log,
highlighted with `Pygments <http://pygments.org/>`_.

Usage example:

.. sourcecode:: rst

   .. chat::

      [00:56:38] <rafaelmartins> I'm crazy.
      [00:56:48] <rafaelmartins> I chat alone.

