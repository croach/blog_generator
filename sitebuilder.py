import os
import sys

from werkzeug import cached_property
from flask import Flask, render_template, abort
from flask_frozen import Freezer
import yaml
import markdown


# Code for handling blog posts

class Posts(object):
    def __init__(self, app):
        self.cache = {}
        self.root = os.path.join(app.root_path, app.config.get('POSTS_ROOT', ''))
        self.extension = app.config.get('POSTS_EXTENSION', '')

    def get_or_404(self, path):
        """
        Returns the Post object at path or raises a NotFound error
        """
        path = os.path.join(self.root, path + self.extension)

        # If the post is cached, return it
        post = self.cache.get(path, None)
        if post:
            return post

        # otherwise, find the post in the file system
        try:
            with open(path, 'r') as fin:
                post = Post(path, fin.read())
        except IOError:
            abort(404)

        # Cache the post and return it
        self.cache[path] = post
        return post

class Post(object):
    def __init__(self, path, content):
        self.path = path
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

@app.route('/blog/<path:path>')
def post(path):
    post = posts.get_or_404(path)
    return render_template('post.html', post=post)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        freezer.freeze()
    else:
        app.run(port=8000)
