from flask import url_for, redirect, request
from flask_admin import AdminIndexView, Admin
from flask_login import current_user

from app import app, db
from app.models.tables import User, PostLike, Post


class AdminModel(AdminIndexView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('users.login', next=request.url))


admin = Admin(app, name='Central', template_mode='bootstrap3', index_view=AdminModel())
admin.add_view(AdminIndexView(User, db.session))
admin.add_view(AdminIndexView(Post, db.session))
admin.add_view(AdminIndexView(PostLike, db.session))
