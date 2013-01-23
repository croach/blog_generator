#!/usr/bin/env python

import os
import sys
import urlparse

from werkzeug import cached_property
from flask import Flask, render_template, abort
from flask_frozen import Freezer
import yaml
import markdown


# Code for handling blog posts
class Posts(object):
    def __init__(self, app):
        self._cache = {}
        self.root = os.path.join(app.root_path, app.config.get('POSTS_ROOT', ''))
        self.file_ext = app.config.get('POSTS_EXTENSION', '')

    def get_or_404(self, path):
        """
        Returns the Post object at path or raises a NotFound error
        """
        abs_path = os.path.join(self.root, path + self.file_ext)

        # If the post is cached, return it
        post = self._cache.get(abs_path, None)
        if post:
            return post

        # otherwise, find the post in the file system
        try:
            with open(abs_path, 'r') as fin:
                post = Post(fin.read())
        except IOError:
            abort(404)

        # Cache the post and return it
        self._cache[abs_path] = post
        return post

    def initialize_cache(self):
        """
        Walks the root directory and adds all posts to the cache dict
        """
        for (path, dirpaths, filepaths) in os.walk(self.root):
            for filepath in filepaths:
                if filepath.endswith(self.file_ext):
                    abs_path = os.path.join(path, filepath)
                    with open(abs_path, 'r') as fin:
                        self._cache[abs_path] = Post(fin.read())

    @cached_property
    def abs_paths(self):
        if not self._cache:
            self.initialize_cache()
        return self._cache.keys()

    @cached_property
    def rel_paths(self):
        root = self.root + os.sep
        return [abs_path.replace(root, '') for abs_path in self.abs_paths]


class Post(object):
    def __init__(self, content):
        self.content = content

    @cached_property
    def html(self):
        content = self.content.split('\n\n')[1:]
        content = ''.join(content).strip()
        return markdown.markdown(content)

    @cached_property
    def meta(self):
        content = self.content.split('\n\n')[0]
        content.strip()
        return yaml.load(content)


# Configuration
DEBUG = True
POSTS_ROOT = 'posts'
POSTS_EXTENSION = '.md'

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
    return render_template('index.html')

@app.route('/blog/<path:path>/')
def post(path):
    post = posts.get_or_404(path)
    return render_template('post.html', post=post)

# Frozen Flask generators
@freezer.register_generator
def post_url_generator():
    # Remove the markdown file extension to turn each filepath into a URL path
    paths = [path.replace(posts.file_ext, '') for path in posts.rel_paths]
    # Replace the OS specific separator with URL seperators
    paths = [path.replace(os.sep, '/') for path in paths]
    return [('post', {'path': path}) for path in paths]


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        freezer.freeze()
    else:
        app.run(port=8000)
