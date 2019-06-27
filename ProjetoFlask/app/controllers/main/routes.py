from flask import Blueprint, render_template

from app.models.tables import Post

main = Blueprint('main', __name__)


@main.route('/index/<username>')
@main.route('/', defaults={'user': None})
def index(user):
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@main.route('/noticias')
def noticias():
    return render_template('noticias.html')


@main.route('/topMusicas')
def topMusicas():
    return render_template('topMusicas.html')


@main.route('/topArtistas')
def topArtistas():
    return render_template('topArtistas.html')


@main.route('/contato')
def contato():
    return render_template('contato.html')


@main.route('/defaultLayout')
def layout():
    return render_template('defaultLayout.html')
