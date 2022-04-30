"""
    Routes
    ~~~~~~
"""
import os

import flask.helpers
from flask import Blueprint, abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import send_file
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from wiki.core import Processor
from wiki.web.downloads import generatePDF, generateTXT
from wiki.web.forms import EditorForm, RegisterForm, UnregisterForm
from wiki.web.forms import LoginForm
from wiki.web.forms import SearchForm
from wiki.web.forms import URLForm
from wiki.web import current_wiki, current_profiles
from wiki.web import current_users
from wiki.web.profile import Profile
from wiki.web.user import protect

bp = Blueprint('wiki', __name__)

@bp.route('/')
@protect
def home():
    page = current_wiki.get('home')
    if page:
        return display('home')
    return render_template('home.html')

@bp.route('/index/')
@protect
def index():
    pages = current_wiki.index()
    return render_template('index.html', pages=pages)

@bp.route('/static/content/<path:image_name>')
@protect
def send_file(image_name):
    return current_wiki.get_image(image_name)

@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    return render_template('page.html', page=page)


@bp.route('/<path:url>/pdf')
@protect
def topdf(url):
    page = current_wiki.get_or_404(url)
    html = render_template('pdf_and_txt_page.html', page=page)
    pdf_file_path = f"{os.getcwd()}/{url}.pdf"
    print(pdf_file_path)
    generatePDF(pdf_file_path, html)
    return flask.helpers.send_file(pdf_file_path, as_attachment=True)


@bp.route('/<path:url>/txt')
@protect
def totxt(url):
    page = current_wiki.get_or_404(url)
    html = render_template('pdf_and_txt_page.html', page=page)
    txt_file_path = f"{os.getcwd()}/{url}.txt"
    print(txt_file_path)
    generateTXT(txt_file_path, html)
    return flask.helpers.send_file(txt_file_path, as_attachment=True)

@bp.route('/image/<path:page_number>', methods=['GET', 'POST'])
@protect
def image(page_number):
    return render_template('images.html',
        current_page = int(page_number[1:]) ,
        gallery = current_wiki.get_gallery_page(page_number[1:]),
        final_page = len(current_wiki.get_gallery()) // 6 + 1,
        des = current_wiki.get_image_des())

@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    return render_template('create.html', form=form)

@bp.route('/upload', methods=["GET", "POST"])
@protect
def upload():
    if request.method == "POST":
        image = request.files["image"]
        description = request.form.get("description")

        if image and description and image.filename.split(".")[-1].lower() in ["png", "jpg", "jpeg", "gif"]:
            if (current_wiki.img_exists(image.filename)):
                flash("Image already exist!", "danger")
            else:
                current_wiki.save_image(image, description)
                flash("Successfully uploaded image to gallery!", "success")
            return redirect(url_for("wiki.upload"))
        else:
            flash("An error occurred while uploading the image!", "danger")
            return redirect(url_for("wiki.upload"))
    return render_template("upload.html")

@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    page = current_wiki.get(url)
    form = EditorForm(obj=page)
    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)
        form.populate_obj(page)
        page.save()
        flash('"%s" was saved.' % page.title, 'success')
        return redirect(url_for('wiki.display', url=url))
    return render_template('editor.html', form=form, page=page)


@bp.route('/preview/', methods=['POST'])
@protect
def preview():
    data = {}
    processor = Processor(request.form['body'])
    data['html'], data['body'], data['meta'] = processor.process()
    return data['html']


@bp.route('/move/<path:url>/', methods=['GET', 'POST'])
@protect
def move(url):
    page = current_wiki.get_or_404(url)
    form = URLForm(obj=page)
    if form.validate_on_submit():
        newurl = form.url.data
        current_wiki.move(url, newurl)
        return redirect(url_for('wiki.display', url=newurl))
    return render_template('move.html', form=form, page=page)


@bp.route('/delete/<path:url>/')
@protect
def delete(url):
    page = current_wiki.get_or_404(url)
    current_wiki.delete(url)
    flash('Page "%s" was deleted.' % page.title, 'success')
    return redirect(url_for('wiki.home'))


@bp.route('/tags/')
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template('tags.html', tags=tags)


@bp.route('/tag/<string:name>/')
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template('tag.html', pages=tagged, tag=name)


@bp.route('/search/', methods=['GET', 'POST'])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        results = current_wiki.search(form.term.data, form.ignore_case.data)
        return render_template('search.html', form=form,
                               results=results, search=form.term.data)
    return render_template('search.html', form=form, search=None)


@bp.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.name.data)
        login_user(user)
        user.set('authenticated', True)
        flash('Login successful.', 'success')
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('login.html', form=form)


@bp.route('/user/logout/')
@login_required
def user_logout():
    current_user.set('authenticated', False)
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('wiki.index'))


@bp.route('/user/register/', methods=['GET', 'POST'])
def user_register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = current_users.add_user(form.username.data, form.password.data)
        current_profiles.add_profile(Profile(form.username.data, form.full_name.data, form.bio.data))
        login_user(user)
        user.set('authenticated', True)
        flash('Registration successful.', 'success')
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('register.html', form=form)


@bp.route('/user/unregister/', methods=['GET', 'POST'])
@protect
def user_unregister():
    form = UnregisterForm()
    if form.validate_on_submit():
        username = current_user.get_id()
        current_user.set('authenticated', False)
        current_users.delete_user(username)
        current_profiles.delete_profile(username)
        logout_user()
        flash(f"Account {username} deleted", 'success')
        return redirect(url_for('wiki.user_login'))
    return render_template('unregister.html', form=form)


@bp.route('/user/<username>', methods=['GET', 'POST'])
@protect
def user_profile(username):
    profile = current_profiles.get_profile(username)
    if not profile:
        profile = abort(404)
    return render_template('profile.html', profile=profile)


@bp.route('/user/')
def user_index():
    pass


@bp.route('/user/create/')
def user_create():
    pass


@bp.route('/user/<int:user_id>/')
def user_admin(user_id):
    pass


@bp.route('/user/delete/<int:user_id>/')
def user_delete(user_id):
    pass


"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
