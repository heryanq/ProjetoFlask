from datetime import datetime

from flask import url_for, request, redirect, abort
from flask_admin import Admin
from flask_login import UserMixin, current_user
from flask_admin.contrib.sqla import ModelView

from app import db, login_manager, app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


friends = db.Table('friends',
                   db.Column('friend_id', db.Integer, db.ForeignKey('user.id')),
                   db.Column('friendship_id', db.Integer, db.ForeignKey('user.id'))
                   )


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    '''liked = db.relationship('PostLike', foreign_keys='PostLike.user_id', backref='user', lazy='dynamic')

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0'''

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    friendships = db.relationship('User',
                                  secondary=friends,
                                  primaryjoin=(friends.c.friend_id == id),
                                  secondaryjoin=(friends.c.friendship_id == id),
                                  backref=db.backref('friends', lazy='dynamic'),
                                  lazy='dynamic')

    def friend(self, user):
        if not self.is_friend(user):
            self.friendships.append(user)
            return self

    def unfriend(self, user):
        if self.is_friend(user):
            self.friendships.remove(user)
            return self

    def is_friend(self, user):
        return self.friendships.filter(friends.c.friendship_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(friends,
                               (friends.c.friendship_id == Post.user_id)).filter(
            friends.c.friend_id == self.id).order_by(Post.timestamp.desc())

    def __repr__(self):
        return f"User('{self.username}, '{self.email}, '{self.image_file})'"


'''class PostLike(db.Model):
    __tablename__ = 'post_like'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))'''


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    '''likes = db.relationship('PostLike', backref='post', lazy='dynamic')'''

    def __repr__(self):
        return f"User('{self.title}, '{self.date_posted})'"


admin = Admin(app, name='Admin')


class AdminModel(ModelView):

    edit_template = 'admin/model/edit_user.html'
    create_template = 'admin/model/create_user.html'
    list_template = 'admin/model/list_user.html'

    def is_accessible(self):
        if current_user.is_admin == True:
            return current_user.is_authenticated
        else:
            return abort(403)

admin.add_view(AdminModel(User, db.session))
admin.add_view(AdminModel(Post, db.session))
