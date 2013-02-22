#!/usr/bin/env python

import os
import sys
import re
import urlparse
import collections
import datetime
import argparse

from flask import Flask, render_template, url_for, abort, request
from flask.ext import frozen
from werkzeug import cached_property
from werkzeug.contrib.atom import AtomFeed
import markdown
import yaml


class SortedDict(collections.MutableMapping):
    def __init__(self, items=[], key=None, reverse=False):
        self._items = {}
        self._keys = []
        if key:
            self._key_fn = lambda k: key(self._items[k])
        else:
            self._key_fn = lambda k: self._items[k]
        self._reverse = reverse

        self.update(items)

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, value):
        self._items[key] = value
        self._keys.append(key)
        self._keys.sort(key=self._key_fn, reverse=self._reverse)

    def __delitem__(self, key):
        self._items.pop(key)
        self._keys.remove(key)

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        return iter(self._keys)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._items)


class Blog(object):
    def __init__(self, app):
        """Initializes the Blog instance

        Arguments:
        app -- a Flask app object.
        """
        self._initialize_app(app)
        self._initialize_cache(SortedDict(key=lambda p: p.date, reverse=True))

    @property
    def posts(self):
        """Returns a list of all blog posts

        The list of blog posts is sorted according to publication date (desc)
        and all unplublished posts are removed when not in debug mode (i.e.,
        whenever the site is being built).
        """
        if self._app.debug:
            return self._cache.values()
        else:
            return [post for post in self._cache.values() if post.published]

    def get_post_or_404(self, path):
        """Returns the Post object at path or raises a NotFound error

        Arguments:
        path -- the filepath portion of a URL.
        """
        # Grab the post from the cache
        post = self._cache.get(path, None)

        # If the post isn't cached (or DEBUG), create a new Post object
        if not post:
            filepath = os.path.join(
                self._app.config['POSTS_ROOT_DIRECTORY'],
                path + self._app.config['POSTS_FILE_EXTENSION']
            )
            if not os.path.isfile(filepath):
                abort(404)
            post = Post(filepath, root_dir=self._app.config['POSTS_ROOT_DIRECTORY'])
            self._cache[post.urlpath] = post

        return post

    def _initialize_app(self, app):
        """Initializes the given Flask app's configuration

        Arguments:
        app -- the flask app to be initialized.
        """
        self._app = app
        self._app.config.setdefault('POSTS_ROOT_DIRECTORY', 'posts')
        self._app.config.setdefault('POSTS_FILE_EXTENSION', '.markdown')

    def _initialize_cache(self, cache=None):
        """
        Walks the root directory and adds all posts to the _cache dict

        Keyword arguments:
        cache -- if included all posts found will be merged into this object,
            otherwise, a new cache is created and will replace the existing
            cache object.
        """
        cache = cache or SortedDict(key=lambda p: p.date, reverse=True)
        root_dir = self._app.config['POSTS_ROOT_DIRECTORY']
        for (root, dirpaths, filepaths) in os.walk(root_dir):
            for filepath in filepaths:
                filename, ext = os.path.splitext(filepath)
                if ext == self._app.config['POSTS_FILE_EXTENSION']:
                    path = os.path.join(root, filepath).replace(root_dir, '')
                    post = Post(path, root_dir=root_dir)
                    cache[post.urlpath] = post
        self._cache = cache


class Post(object):
    def __init__(self, path, root_dir=''):
        """Initializes the Post instance

        Arguments:
        path -- the relative location of the file representing the blog post.

        Keyword arguments:
        root_dir -- an optional root directory for all of the blog posts
            relative to the current directory.
        """
        self.urlpath = os.path.splitext(path.strip('/'))[0]
        self.filepath = os.path.join(root_dir, path.strip('/'))
        self.published = False
        self._initialize_metadata()

    @cached_property
    def html(self):
        """Returns the HTML for the blog post

        Converts the content portion of the file located at self.filepath to
        HTML and returns it.
        """
        with open(self.filepath, 'r') as fin:
            content = fin.read().split('\n\n', 1)[1].strip()
        return markdown.markdown(content, extensions=['codehilite', 'fenced_code'])

    @cached_property
    def url(self):
        """Returns the URL for the blog post
        """
        return url_for('post', path=self.urlpath)

    @cached_property
    def title(self):
        """Returns a title based on the name of the file

        This property is overwritten by the _initialize_meta method if a title
        attribute is in the meta portion of the blog post file.
        """
        filename_and_ext = os.path.basename(self.filepath)
        filename = os.path.splitext(filename_and_ext)[0]
        title = re.sub('[-_]', ' ', filename).title()
        return title

    @cached_property
    def date(self):
        """Returns the current date

        This property is overwritten by the _initialize_meta method if a title
        attribute is in the meta portion of the blog post file.
        """
        return datetime.date.today()

    def _initialize_metadata(self):
        content = ''
        with open(self.filepath, 'r') as fin:
            for line in fin:
                if not line.strip():
                    break
                content += line
        meta = yaml.load(content)
        self.__dict__.update(meta if isinstance(meta, dict) else {})

# TODO move some of these into an external config file
FREEZER_BASE_URL = 'http://christopherroach.com'
FREEZER_IGNORED_FILES = ['.git', 'CNAME']
POSTS_ROOT_DIRECTORY = 'posts'
POSTS_FILE_EXTENSION = '.md'

app = Flask(__name__)
app.config.from_object(__name__)
freezer = frozen.Freezer(app)
blog = Blog(app)


# Custom Jinja Filter
@app.template_filter('date')
def format_date(value, format='%B %d, %Y'):
    return value.strftime(format)


# Routes
@app.route('/')
def index():
    return render_template('index.html', posts=blog.posts)


@app.route('/blog/<path:path>/')
def post(path):
    post = blog.get_post_or_404(path)
    return render_template('post.html', post=post)


@app.route('/feed.atom')
def feed():
    feed = AtomFeed('My Awesome Blog',
        feed_url=request.url,
        url=request.url_root,
        updated=datetime.datetime.now())
    for post in blog.posts[:10]: # Just show the last 10 posts
        try:
            post_title = '%s: %s' % (post.title, post.subtitle)
        except AttributeError:
            post_title = post.title
        post_url = urlparse.urljoin(request.url_root, post.url)

        feed.add(
            title=post_title,
            content=unicode(post.html),  # this could be a summary for the post
            content_type='html',
            author='Christopher Roach',
            url=post_url,
            updated=post.date,  # published is optional, updated is not
            published=post.date)
    return feed.get_response()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Static site builder",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('command',
        nargs='?',
        default='debug',
        metavar='COMMAND',
        help="""one of the commands listed below (defaults to debug).

build - builds the static website
serve - runs an HTTP server on the result of the build
run   - builds and serves the site
debug - runs the development server in debug mode
    """)
    parser.add_argument('directory',
        nargs='?',
        default='build',
        metavar='DIRECTORY',
        help="the directory in which to build the site (default build)")

    args = parser.parse_args()

    freezer.app.config['FREEZER_DESTINATION'] = args.directory
    if args.command == 'build':
        freezer.freeze()
    elif args.command == 'serve':
        freezer.serve(port=8000)
    elif args.command == 'run':
        freezer.run(port=8000)
    else: # debug
        app.run(port=8000, debug=True)
