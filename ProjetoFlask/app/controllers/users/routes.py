from flask import Blueprint, redirect, url_for, flash, render_template, request, abort
from flask_login import current_user, login_user, logout_user, login_required

from app import bcrypt, db
from app.controllers.users.utils import save_picture
from app.models.tables import User, Post
from app.models.users.forms import RegistrationForm, RegistrationAdminForm, LoginForm, UpdateAccountForm

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Sua conta foi criada com sucesso! Você pode fazer login agora', 'success')
        # flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html',
                           form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Falha ao fazer log in. Por favor confira seus dados', 'danger')
    return render_template('login.html',
                           form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@users.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(user_id=user.id).all()
    if user == None:
        flash('Usuário %s não encontrado.' % username)
        return redirect(url_for('main.index'))
    return render_template('user.html',
                           user=user,
                           posts=posts)


@users.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    if current_user.is_admin == True:
        form = RegistrationAdminForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=True)
            db.session.add(user)
            db.session.commit()
            flash(f'Uma conta de administrador foi criada com sucesso! Você pode fazer login nela agora', 'success')
            # flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('main.index'))
        return render_template('register_admin.html',
                               form=form)
    else:
        abort(403)


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Seus dados foram atualizados!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',
                           image_file=image_file, form=form)


@users.route('/friend/<username>')
@login_required
def friend(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Usuário %s não encontrado.' % username)
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('Você não pode se adicionar!')
        return redirect(url_for('users.account', username=username))
    u = current_user.friend(user)
    if u is None:
        flash('Você e ' + username + ' já são amigos!')
        return redirect(url_for('users.account', username=username))
    db.session.add(u)
    db.session.commit()
    flash('Você e ' + username + ' são amigos agora!', 'success')
    return redirect(url_for('users.account', username=username))


@users.route('/unfriend/<username>')
@login_required
def unfriend(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Usuário %s não encontrado.' % username)
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('Você não pode desfazer amizade consigo mesmo!')
        return redirect(url_for('users.account', username=username))
    u = current_user.unfriend(user)
    if u is None:
        flash('Você e ' + username + ' não são amigos para desfazer uma amizade!')
        return redirect(url_for('users.account', username=username))
    db.session.add(u)
    db.session.commit()
    flash('Você e ' + username + ' não são mais amigos!', 'success')
    return redirect(url_for('users.account', username=username))
