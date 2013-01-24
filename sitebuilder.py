#!/usr/bin/env python

import os
import sys
import urlparse

from werkzeug import cached_property
from flask import Flask, render_template, abort
from flask_frozen import Freezer
import yaml
import markdown


class SortedDict(dict):
    def __init__(self, items=[], key=lambda item: item, reverse=False):
        self._items = []
        if reverse:
            self._compare = lambda item1, item2: key(item1) > key(item2)
        else:
            self._compare = lambda item1, item2: key(item1) < key(item2)

        # Insert all of the items into the dict
        self.update(items)

    def __setitem__(self, key, value):
        # If the key already exists in the dict, remove it from the
        # ordered items list before inserting it
        if key in self:
            self._items.remove(key)

        # Get the index of the position where to insert the new item
        index = len(self._items)
        for i in range(len(self._items)):
            curr = dict.__getitem__(self, self._items[i])
            if self._compare(value, curr):
                index = i
                break

        # Insert the new item into the ordered items list and self
        self._items.insert(index, key)
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        self._items.remove(key)
        dict.__delitem__(self, key)

    def __iter__(self):
        return iter(self.keys())

    def __reverse__(self):
        return reversed(self.keys())

    def items(self):
        return [(key, self[key]) for key in self._items]

    def keys(self):
        return [k for k, _ in self.items()]

    def values(self):
        return [v for _, v in self.items()]

    def update(self, items=[], **kwargs):
        if hasattr(items, 'keys'):
            for key in items:
                self[key] = items[key]
        else:
            for (key, value) in items:
                self[key] = value

        for key in kwargs:
            self[key] = kwargs[key]


# Code for handling blog posts
class Posts(object):
    def __init__(self, app):
        self._app = app
        self._cache = SortedDict(reverse=True)
        self.root = os.path.join(app.root_path, app.config.get('POSTS_ROOT_DIRECTORY', ''))
        self.file_ext = app.config.get('POSTS_FILE_EXTENSION', '')
        self._initialize_cache()

    def __iter__(self):
        return iter(self._cache.values())

    def __len__(self):
        return len(self._cache)

    def __getitem__(self, key):
        return self._cache.values()[key]

    def get_or_404(self, path):
        """
        Returns the Post object at path or raises a NotFound error
        """
        # Grab the post from the cache
        post = self._cache.get(path, None)

        # If the post isn't cached (or DEBUG), create a new Post object
        if not post or self._app.config.get('DEBUG', False):
            filepath = os.path.join(self.root, path + self.file_ext)
            if not os.path.isfile(filepath):
                abort(404)
            post = Post(filepath, self.root)
            self._cache[path] = post

        return post

    def _initialize_cache(self):
        """
        Walks the root directory and adds all posts to the cache dict
        """
        for (path, dirpaths, filepaths) in os.walk(self.root):
            for filepath in filepaths:
                if filepath.endswith(self.file_ext):
                    abs_path = os.path.join(path, filepath)
                    url = abs_path.replace(self.root, '').replace(self.file_ext, '')
                    self._cache[url] = Post(abs_path, self.root)


class Post(object):
    def __init__(self, path, root=''):
        self.path = os.path.join(root, path)
        self.url = self.path.replace(root + os.sep, '')  # Make it relative to root
        self.url = os.path.splitext(self.url)[0]         # Remove the file extension
        self.url = self.url.replace(os.sep, '/')         # Replace os seperators with URL seperators
        self.published = False
        self._initialize_meta()

    @cached_property
    def html(self):
        with open(self.path, 'r') as fin:
            content = fin.read().split('\n\n', 1)[1].strip()
        return markdown.markdown(content, ['fenced_code', 'codehilite'])

    def _initialize_meta(self):
        content = ''
        with open(self.path, 'r') as fin:
            for line in fin:
                if not line.strip():
                    break
                content += line
        self.__dict__.update(yaml.load(content))


# Configuration
DEBUG = True
POSTS_ROOT_DIRECTORY = 'posts'
POSTS_FILE_EXTENSION = '.md'
POSTS_URL_PREFIX = 'blog'

app = Flask(__name__)
app.config.from_object(__name__)
freezer = Freezer(app)
posts = Posts(app)


# Custom filters
@app.template_filter('date')
def date_filter(value, format='%B %d, %Y'):
    return value.strftime(format)

# Routes
@app.route('/')
def index():
    if app.debug:
        published = [post for post in posts if post.published]
    else:
        published = posts
    return render_template('index.html', posts=published)

@app.route('/blog/<path:path>/')
def post(path):
    post = posts.get_or_404(path)
    return render_template('post.html', post=post)

# Frozen Flask generators
@freezer.register_generator
def post_url_generator():
    if app.debug:
        published = [post for post in posts if post.published]
    else:
        published = posts
    return [('post', {'path': post.url}) for post in published]


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        app.config['DEBUG'] = False
        freezer.freeze()
    else:
        app.run(port=8000)
